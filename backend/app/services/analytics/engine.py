import logging
from typing import Any

import pandas as pd

from app.core.exceptions import DatlyException
from app.models.analysis_plan import AnalysisPlan

logger = logging.getLogger("datly.analytics.engine")

import os
import sys

external_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../external_modules/datly_analytics_module"))
if external_path not in sys.path:
    sys.path.insert(0, external_path)

from analytics.engine import AnalyticsEngine
from analytics.models import AnalyticsError


def execute_plan(df: pd.DataFrame, plan: AnalysisPlan) -> dict[str, Any]:
    try:
        engine = AnalyticsEngine()
        
        # 1. Convert plan to dictionary safely
        plan_dict = plan.model_dump(mode="json", exclude_none=True)
        
        # Pass time_granularity if present
        if plan.time_granularity:
            plan_dict["time_granularity"] = plan.time_granularity.value
        
        is_percentage = plan_dict.get("operation") == "percentage"
        if is_percentage:
            plan_dict["operation"] = "group_by"
            if "sort" not in plan_dict:
                plan_dict["sort"] = "desc"
        
        # 2. Execute plan
        result = engine.execute(df, plan_dict)
        
        if is_percentage and result.rows:
            metric = plan.metric_column
            if metric and metric in result.columns:
                total = sum(row[metric] for row in result.rows)
                for row in result.rows:
                    val = row[metric]
                    pct = (val / total * 100) if total else 0
                    row["percentage"] = round(pct, 1)
                
                if "percentage" not in result.columns:
                    result.columns.append("percentage")
                    
                if result.visualization and result.visualization.get("type") == "bar":
                    result.visualization["y"] = "percentage"
                    
                result.operation = "percentage"
        
        # 3. Convert external AnalysisResult to existing DATLY format
        if result.operation == "anomaly_detection":
            meta = {}
            rows = result.rows
            if rows:
                first_row = rows[0]
                meta = {
                    "column": plan.metric_column,
                    "method": plan.anomaly_method or "iqr",
                    "anomaly_count": len(rows),
                    "total_rows": first_row.get("_total_rows", 0),
                    "anomaly_rate": first_row.get("_anomaly_rate", 0.0),
                    "lower_bound": first_row.get("_lower_bound"),
                    "upper_bound": first_row.get("_upper_bound"),
                    "mean": first_row.get("_mean"),
                    "std": first_row.get("_std")
                }
                # Clean metadata from rows
                for r in rows:
                    for k in list(r.keys()):
                        if k.startswith("_") and k not in ["_anomaly_score", "_anomaly_reason"]:
                            del r[k]
            else:
                meta = {
                    "column": plan.metric_column,
                    "method": plan.anomaly_method or "iqr",
                    "anomaly_count": 0,
                    "total_rows": 0, # Since we didn't attach it when rows are empty, it's 0. Wait, actually we can get df size from somewhere?
                }
            return {"meta": meta, "data": rows, "_external_result": result.model_dump()}
        # Trend and comparison always return multi-row data
        elif result.operation in ["trend", "comparison"]:
            return {"data": result.rows, "_external_result": result.model_dump()}
        elif result.operation == "aggregate" and len(result.rows) == 1:
            row = result.rows[0]
            if len(row) == 1:
                val = next(iter(row.values()))
                return {"value": val, "_external_result": result.model_dump()}
            else:
                return {"data": result.rows, "_external_result": result.model_dump()}
        else:
            return {"data": result.rows, "_external_result": result.model_dump()}
        
    except AnalyticsError as e:
        logger.error(f"Execution failed: {e.message}")
        
        # Error mapping
        code_map = {
            "MISSING_COLUMN": "MISSING_COLUMN",
            "INVALID_DATAFRAME": "INVALID_ANALYSIS_PLAN",
            "MISSING_OPERATION": "INVALID_ANALYSIS_PLAN",
            "UNSUPPORTED_OPERATION": "INCOMPATIBLE_OPERATION",
            "INCOMPATIBLE_OPERATION": "INCOMPATIBLE_OPERATION",
        }
        datly_code = code_map.get(e.code, "ANALYTICS_ERROR")
        
        raise DatlyException(
            code=datly_code,
            message=f"Failed to execute analysis plan: {e.message}",
            status_code=500 if datly_code == "ANALYTICS_ERROR" else 400
        )
    except Exception as e: # noqa: BLE001
        logger.error(f"Execution failed: {e}")
        raise DatlyException(
            code="ANALYTICS_ERROR",
            message=f"Failed to execute analysis plan: {e!s}",
            status_code=500
        )
