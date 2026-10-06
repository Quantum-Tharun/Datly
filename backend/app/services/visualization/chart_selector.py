import re
from typing import Any

from app.models.analysis_plan import AnalysisPlan, Operation
from app.models.analysis_result import VisualizationSpec, VisualizationType
from app.models.schema import DatasetSchema


class VisualizationSelector:
    @staticmethod
    def select_visualization(plan: AnalysisPlan, result: dict[str, Any], schema: DatasetSchema | None = None) -> VisualizationSpec:
        # 1. Determine if user made an explicit valid request
        explicit_viz = None
        if plan.visualization and plan.visualization.type and plan.visualization.type.value not in ["none", "auto"]:
            explicit_viz = plan.visualization

        # Check if result is just a single scalar value
        if "value" in result:
            if explicit_viz and explicit_viz.type == VisualizationType.none:
                return VisualizationSpec(type=VisualizationType.none)
            title = explicit_viz.title if explicit_viz and explicit_viz.title else (plan.metric_column.capitalize() if plan.metric_column else "Result")
            return VisualizationSpec(type=VisualizationType.kpi, title=title)
            
        if "data" not in result or not result["data"] or not isinstance(result["data"], list):
            return VisualizationSpec(type=VisualizationType.none)
            
        # 2. If explicit viz requested, validate compatibility
        if explicit_viz:
            req_type = explicit_viz.type
            title = explicit_viz.title or "Analysis Result"
            x = explicit_viz.x or plan.group_column
            y = explicit_viz.y or plan.metric_column
            
            # If they want a table, always safe
            if req_type == VisualizationType.table:
                return VisualizationSpec(type=VisualizationType.table, title=title)
                
            # If they want a bar/line/pie chart, need group + metric (x + y)
            if req_type in (VisualizationType.bar, VisualizationType.line, VisualizationType.pie, VisualizationType.donut, VisualizationType.area) and x and y:
                return VisualizationSpec(type=req_type, x=x, y=y, title=title)
                
            # If they want a scatter chart, need two numeric variables.
            if req_type == VisualizationType.scatter:
                if plan.operation == Operation.anomaly_detection and y:
                    return VisualizationSpec(type=req_type, x=x, y=y, title=title)
                if x and y:
                    return VisualizationSpec(type=req_type, x=x, y=y, title=title)
                
            # If they want a histogram, need at least one numeric variable (x or y).
            if req_type == VisualizationType.histogram and (x or y):
                return VisualizationSpec(type=req_type, x=x or y, y=y, title=title)
                
            # Box plot compatibility
            if req_type == VisualizationType.box and (x or y):
                return VisualizationSpec(type=req_type, x=x, y=y, title=title)

        # 3. Check if external engine visualization is available (Fallback level 1)
        if "_external_result" in result and "visualization" in result["_external_result"]:
            ext_viz = result["_external_result"]["visualization"]
            if ext_viz:
                viz_type = ext_viz.get("type", "none")
                try:
                    viz_enum = VisualizationType(viz_type)
                except ValueError:
                    viz_enum = VisualizationType.table
                
                # Only use external visualization if it's not 'none' or 'table' or if we have no better heuristics
                if viz_enum not in (VisualizationType.none, VisualizationType.table):
                    return VisualizationSpec(
                        type=viz_enum,
                        x=ext_viz.get("x") or plan.group_column,
                        y=ext_viz.get("y") or plan.metric_column,
                        title=ext_viz.get("title") or "Analysis Result"
                    )

        # 3. Automatic Heuristics (Fallback)
        # 3. Automatic Heuristics (Fallback)
        metric = plan.metric_column or (plan.metric_columns[0] if plan.metric_columns else None)
        
        # If no metric column is defined, but data is present, default to table
        is_count = False
        if plan.operation == Operation.aggregate:
            if getattr(plan, "aggregation", None) == "count" or getattr(plan, "aggregations", None) and "count" in plan.aggregations:
                is_count = True
                
        if not metric and not is_count:
             return VisualizationSpec(type=VisualizationType.table, title="Analysis Result")
             
        # Histogram
        if plan.operation == Operation.histogram and metric:
            return VisualizationSpec(type=VisualizationType.histogram, x=metric, title=f"Distribution of {metric.capitalize()}")
            
        # Box
        if plan.operation == Operation.box and metric:
            return VisualizationSpec(type=VisualizationType.box, x=plan.group_column, y=metric, title=f"Distribution of {metric.capitalize()}")

        # Scatter for numeric vs numeric comparisons
        if plan.operation == Operation.comparison and plan.group_column and metric:
             return VisualizationSpec(
                type=VisualizationType.scatter,
                x=plan.group_column,
                y=metric,
                title=f"{plan.group_column.capitalize()} vs {metric.capitalize()}"
            )
            
        # Anomaly Detection
        if plan.operation == Operation.anomaly_detection and metric:
            if plan.group_column:
                # Time/Group + anomaly detection
                return VisualizationSpec(
                    type=VisualizationType.scatter, 
                    x=plan.group_column, 
                    y=metric, 
                    title=f"Anomalies in {metric.capitalize()} by {plan.group_column.capitalize()}"
                )
            else:
                # Numeric distribution anomaly
                return VisualizationSpec(
                    type=VisualizationType.box, 
                    y=metric, 
                    title=f"Anomaly Distribution of {metric.capitalize()}"
                )
            
        # Percentage (Part-to-whole)
        if plan.operation == Operation.percentage and plan.group_column and metric:
            # Check cardinality
            data_len = len(result.get("data", []))
            if data_len <= 10:
                return VisualizationSpec(
                    type=VisualizationType.pie,
                    x=plan.group_column,
                    y="percentage",
                    title=f"{metric.capitalize()} Share by {plan.group_column.capitalize()}"
                )
            else:
                # Too many slices, fallback to bar
                return VisualizationSpec(
                    type=VisualizationType.bar,
                    x=plan.group_column,
                    y="percentage",
                    title=f"{metric.capitalize()} Share by {plan.group_column.capitalize()}"
                )
             
        # Categorical Comparison & Ranking & Trend
        if plan.operation in (Operation.group_by, Operation.top_n, Operation.trend) and plan.group_column and metric:
            # check if group column is a date
            is_date = False
            if schema:
                for col in schema.columns:
                    if col.name == plan.group_column and col.data_type in ("datetime", "date"):
                        is_date = True
                        break
            # Or heuristic based on plan or column name
            if not is_date and (re.search(r"date|time|year|month|day", plan.group_column.lower())):
                is_date = True
                
            if is_date or plan.operation == Operation.trend:
                return VisualizationSpec(
                    type=VisualizationType.line,
                    x=plan.group_column,
                    y=metric,
                    title=f"{metric.capitalize()} Trend"
                )
            else:
                return VisualizationSpec(
                    type=VisualizationType.bar,
                    x=plan.group_column,
                    y=metric,
                    title=f"{metric.capitalize()} by {plan.group_column.capitalize()}"
                )
                
        # Default to table for multi-column output
        return VisualizationSpec(
            type=VisualizationType.table, 
            title="Analysis Result"
        )
