from typing import Any

from app.models.analysis_plan import AnalysisPlan, Operation


def format_number(num: Any) -> str:
    if isinstance(num, (int, float)):
        return f"{num:,.2f}".rstrip('0').rstrip('.')
    return str(num)

from app.models.analysis_result import VisualizationSpec, VisualizationType


def format_answer(plan: AnalysisPlan, result: dict[str, Any], viz_spec: VisualizationSpec | None = None) -> str:
    if "meta" in result and plan.operation == Operation.anomaly_detection:
        meta = result["meta"]
        count = meta.get("anomaly_count", 0)
        method = meta.get("method", "iqr").upper()
        rate = meta.get("anomaly_rate", 0)
        metric = meta.get("column", "the requested column")
        
        if count == 0:
            return f"No anomalies were found in {metric} using the {method} method."
            
        return f"{count} {metric} values were identified as anomalies using the {method} method. They represent {format_number(rate)}% of the analyzed data."
    if "value" in result:
        val = result["value"]
        if val is None:
             return "No matching records were found."
        formatted_val = format_number(val)
        
        if plan.operation == Operation.aggregate:
             if plan.aggregation == "count":
                  return f"There are {formatted_val} records."
             if plan.aggregation == "sum" and plan.metric_column:
                  return f"The total {plan.metric_column} is ₹{formatted_val}."
             if plan.aggregation == "average" and plan.metric_column:
                  return f"The average {plan.metric_column} is ₹{formatted_val}."
             if plan.aggregation == "min" and plan.metric_column:
                  return f"The minimum {plan.metric_column} is ₹{formatted_val}."
             if plan.aggregation == "max" and plan.metric_column:
                  return f"The maximum {plan.metric_column} is ₹{formatted_val}."
             if plan.aggregation == "median" and plan.metric_column:
                  return f"The median {plan.metric_column} is ₹{formatted_val}."
             if plan.aggregation == "standard_deviation" and plan.metric_column:
                  return f"The standard deviation of {plan.metric_column} is {formatted_val}."
             if plan.aggregation == "variance" and plan.metric_column:
                  return f"The variance of {plan.metric_column} is {formatted_val}."
             if plan.aggregation == "count_distinct" and plan.metric_column:
                  return f"There are {formatted_val} unique {plan.metric_column}."
             
             if plan.metric_column:
                  return f"The {plan.aggregation} of {plan.metric_column} is {formatted_val}."
        
        return f"The result is {formatted_val}."

    if "data" in result:
        data = result["data"]
        if not data:
            return "No matching records were found."
            
        viz_type = viz_spec.type if viz_spec else None
        metric = plan.metric_column or (plan.metric_columns[0] if getattr(plan, "metric_columns", None) else "value")
        group = plan.group_column or "category"
        
        # ── Trend results ──
        if plan.operation == Operation.trend and plan.group_column and plan.metric_column:
            n = len(data)
            if n >= 2:
                first_period = data[0].get(plan.group_column, "start")
                last_period = data[-1].get(plan.group_column, "end")
                # Find the highest period
                best = max(data, key=lambda r: r.get(plan.metric_column, 0) or 0)
                best_period = best.get(plan.group_column, "?")
                best_val = format_number(best.get(plan.metric_column, 0))
                
                prefix = f"{plan.metric_column.capitalize()} trend from {first_period} to {last_period} ({n} periods). The highest {plan.metric_column} was ₹{best_val} in {best_period}."
                if viz_type == VisualizationType.line:
                    return f"{prefix} I have chosen a line chart to best visualize the {metric} trend over time."
                return prefix
            return f"Trend analysis returned {n} period(s). See the chart for details."
        
        # ── Comparison / scatter results ──
        if plan.operation == Operation.comparison and plan.group_column and plan.metric_column:
            n = len(data)
            if viz_type == VisualizationType.scatter:
                 return f"Showing {n} data points comparing {plan.group_column} vs {plan.metric_column}. I've provided a scatter plot to help you see the relationship."
            return f"Showing {n} data points comparing {plan.group_column} vs {plan.metric_column}. See the chart for details."
            
        # ── Multi-metric scalar result ──
        if plan.operation == Operation.aggregate and len(data) == 1:
            row = data[0]
            parts = []
            for k, v in row.items():
                parts.append(f"{k} = {format_number(v)}")
            return "The calculated results are: " + ", ".join(parts) + "."
        
        # ── Single-row grouped result ──
        if len(data) == 1 and plan.group_column and plan.metric_column:
            row = data[0]
            group_val = row.get(plan.group_column)
            metric_val = row.get(plan.metric_column)
            if group_val is not None and metric_val is not None:
                if plan.operation == Operation.percentage and "percentage" in row:
                    return f"{group_val} contributed {format_number(row['percentage'])}% of the total {plan.metric_column}."
                if plan.sort == "desc" or plan.operation == Operation.top_n:
                    return f"{group_val} has the highest {plan.metric_column} with a value of ₹{format_number(metric_val)}."
                if plan.sort == "asc":
                    return f"{group_val} has the lowest {plan.metric_column} with a value of ₹{format_number(metric_val)}."
                return f"For {group_val}, the {plan.metric_column} is ₹{format_number(metric_val)}."
                
        # ── Percentage results ──
        if plan.operation == Operation.percentage:
            if len(data) >= 2 and plan.group_column:
                first = data[0]
                second = data[1]
                prefix = f"{first.get(plan.group_column)} contributed the highest share of {plan.metric_column} at {format_number(first.get('percentage'))}%, followed by {second.get(plan.group_column)} at {format_number(second.get('percentage'))}%."
            else:
                prefix = "Analysis completed successfully."
                
            if viz_type in (VisualizationType.pie, VisualizationType.donut):
                return f"{prefix} I selected a {viz_type} chart as it is the best technique to show the {metric} distribution by {group}."
            return f"{prefix} See the result chart for percentage of {metric} by {group}."
            
        # ── Grouped / top_n results ──
        if plan.operation in (Operation.group_by, Operation.top_n):
             if viz_type == VisualizationType.bar:
                 return f"I have analyzed the data and generated a bar chart, as it is the most useful technique to compare {metric} across {group}."
             if viz_type == VisualizationType.line:
                 return f"I have analyzed the data and generated a line chart to best show {metric} over time."
             return f"Analysis completed successfully. See the result table for {metric} grouped by {group}."
             
        if viz_type == VisualizationType.histogram:
             return f"I have analyzed the data and chosen a histogram to clearly show the frequency distribution of {metric}."
        if viz_type == VisualizationType.box:
             return f"I have analyzed the data and chosen a box plot to help you visualize the spread and distribution of {metric}."
              
    return "Analysis completed successfully. See the result table for details."

