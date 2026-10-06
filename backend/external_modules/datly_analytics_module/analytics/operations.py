
import pandas as pd

from .aggregations import get_aggregation
from .filters import apply_filters
from .models import AnalyticsError


def _check_column_exists(df: pd.DataFrame, column: str) -> None:
    if column not in df.columns:
        raise AnalyticsError("MISSING_COLUMN", f"Column '{column}' does not exist in the dataset.")

def _check_numeric_column(df: pd.DataFrame, column: str, operation: str) -> None:
    _check_column_exists(df, column)
    if not pd.api.types.is_numeric_dtype(df[column]):
        raise AnalyticsError("INCOMPATIBLE_OPERATION", f"Column '{column}' must be numeric for the {operation} operation.")

def aggregate(df: pd.DataFrame, plan: dict) -> pd.DataFrame:
    metrics = plan.get("metric_columns") or ([plan.get("metric_column")] if plan.get("metric_column") else [])
    aggs = plan.get("aggregations") or ([plan.get("aggregation")] if plan.get("aggregation") else [])
    
    if not aggs:
        raise AnalyticsError("MISSING_AGGREGATION", "aggregation is required for aggregate operation.")
        
    result_dict = {}
    import numpy as np
    
    for agg in aggs:
        if agg == "count":
            if metrics:
                for metric in metrics:
                    _check_column_exists(df, metric)
                    val = df[metric].count()
                    key = metric if len(metrics) == 1 and len(aggs) == 1 else f"count_{metric}"
                    result_dict[key] = int(val)
            else:
                val = len(df)
                result_dict["count"] = int(val)
            continue
            
        if not metrics:
            raise AnalyticsError("MISSING_METRIC", f"metric_column is required for {agg} aggregation.")
            
        agg_func = get_aggregation(agg)
        
        for metric in metrics:
            _check_column_exists(df, metric)
            if agg_func in ["sum", "mean", "median", "std", "var"] and not pd.api.types.is_numeric_dtype(df[metric]):
                raise AnalyticsError("INCOMPATIBLE_OPERATION", f"Column '{metric}' must be numeric for the {agg} operation.")
                
            val = df[metric].agg(agg_func)
            
            if pd.isna(val):
                val = None
            elif isinstance(val, (np.floating, float)):
                val = float(val)
            elif isinstance(val, (np.integer, int)):
                val = int(val)
                
            key = metric if len(metrics) == 1 and len(aggs) == 1 else f"{agg}_{metric}"
            result_dict[key] = val
            
    return pd.DataFrame([result_dict])

def apply_filter_op(df: pd.DataFrame, plan: dict) -> pd.DataFrame:
    filters = plan.get("filters", [])
    if not isinstance(filters, list):
        raise AnalyticsError("INVALID_FILTERS", "filters must be a list.")
    return apply_filters(df, filters)

def group_by(df: pd.DataFrame, plan: dict) -> pd.DataFrame:
    group_col = plan.get("group_column")
    metrics = plan.get("metric_columns") or ([plan.get("metric_column")] if plan.get("metric_column") else [])
    agg = plan.get("aggregation")
    sort_dir = plan.get("sort")
    limit = plan.get("limit")
    
    if not group_col or not metrics or not agg:
        raise AnalyticsError("INVALID_GROUP_BY", "group_column, metric_column, and aggregation are required.")
        
    _check_column_exists(df, group_col)
    for metric in metrics:
        _check_column_exists(df, metric)
    
    agg_func = get_aggregation(agg)
    
    for metric in metrics:
        if agg_func in ["sum", "mean", "median", "std", "var"] and not pd.api.types.is_numeric_dtype(df[metric]):
            raise AnalyticsError("INCOMPATIBLE_OPERATION", f"Column '{metric}' must be numeric for the {agg_func} operation.")
    
    agg_dict = {metric: agg_func for metric in metrics}
    grouped = df.groupby(group_col, as_index=False).agg(agg_dict)
    
    if sort_dir:
        if sort_dir not in ["asc", "desc"]:
            raise AnalyticsError("INVALID_SORT", "sort must be 'asc' or 'desc'.")
        # Sort by the first metric if sort_column is not explicitly set
        sort_metric = plan.get("sort_column") or metrics[0]
        grouped = grouped.sort_values(by=sort_metric, ascending=(sort_dir == "asc"))
        
    if limit is not None:
        if not isinstance(limit, int) or limit < 0:
            raise AnalyticsError("INVALID_LIMIT", "limit must be a positive integer.")
        grouped = grouped.head(limit)
        
    return grouped

def sort_dataframe(df: pd.DataFrame, plan: dict) -> pd.DataFrame:
    sort_col = plan.get("sort_column")
    sort_dir = plan.get("sort", "asc")
    limit = plan.get("limit")
    
    if not sort_col:
        raise AnalyticsError("MISSING_SORT_COLUMN", "sort_column is required.")
        
    _check_column_exists(df, sort_col)
    
    if sort_dir not in ["asc", "desc"]:
        raise AnalyticsError("INVALID_SORT", "sort must be 'asc' or 'desc'.")
        
    result = df.sort_values(by=sort_col, ascending=(sort_dir == "asc"))
    
    if limit is not None:
        if not isinstance(limit, int) or limit < 0:
            raise AnalyticsError("INVALID_LIMIT", "limit must be a positive integer.")
        result = result.head(limit)
        
    return result

def top_n(df: pd.DataFrame, plan: dict) -> pd.DataFrame:
    metric = plan.get("metric_column")
    n = plan.get("n")
    sort_dir = plan.get("sort", "desc")
    
    if not metric or n is None:
        raise AnalyticsError("INVALID_TOP_N", "metric_column and n are required for top_n.")
        
    _check_column_exists(df, metric)
    
    if not isinstance(n, int) or n < 0:
        raise AnalyticsError("INVALID_N", "n must be a positive integer.")
        
    if sort_dir not in ["asc", "desc"]:
        raise AnalyticsError("INVALID_SORT", "sort must be 'asc' or 'desc'.")
        
    result = df.sort_values(by=metric, ascending=(sort_dir == "asc"))
    return result.head(n)


def trend_analysis(df: pd.DataFrame, plan: dict) -> pd.DataFrame:
    """Time-series trend: groups by a datetime column at a specified granularity."""
    group_col = plan.get("group_column")
    metric = plan.get("metric_column")
    agg = plan.get("aggregation", "sum")
    sort_dir = plan.get("sort", "asc")

    if not group_col or not metric:
        raise AnalyticsError("INVALID_TREND", "group_column (datetime) and metric_column are required for trend.")

    _check_column_exists(df, group_col)
    _check_column_exists(df, metric)

    work = df.copy()
    # Coerce the group column to datetime
    work[group_col] = pd.to_datetime(work[group_col], errors="coerce")
    work = work.dropna(subset=[group_col])

    # Determine time granularity
    granularity = plan.get("time_granularity", "month")
    if granularity == "year":
        work["_period"] = work[group_col].dt.to_period("Y").astype(str)
    elif granularity == "quarter":
        work["_period"] = work[group_col].dt.to_period("Q").astype(str)
    elif granularity == "week":
        work["_period"] = work[group_col].dt.to_period("W").apply(lambda p: str(p.start_time.date()))
    elif granularity == "day":
        work["_period"] = work[group_col].dt.to_period("D").astype(str)
    else:
        # Default: month
        work["_period"] = work[group_col].dt.to_period("M").astype(str)

    agg_func = get_aggregation(agg)
    grouped = work.groupby("_period", as_index=False).agg({metric: agg_func})
    grouped = grouped.rename(columns={"_period": group_col})

    ascending = sort_dir != "desc"
    grouped = grouped.sort_values(by=group_col, ascending=ascending)

    return grouped


def comparison(df: pd.DataFrame, plan: dict) -> pd.DataFrame:
    """Returns two numeric columns for scatter plot / comparison."""
    x_col = plan.get("group_column")
    y_col = plan.get("metric_column")

    if not x_col or not y_col:
        raise AnalyticsError("INVALID_COMPARISON", "group_column (x) and metric_column (y) are required for comparison.")

    _check_column_exists(df, x_col)
    _check_column_exists(df, y_col)

    result = df[[x_col, y_col]].dropna()
    return result


import numpy as np


def box_plot(df: pd.DataFrame, plan: dict) -> pd.DataFrame:
    metric = plan.get("metric_column")
    group_col = plan.get("group_column")
    
    if not metric:
        raise AnalyticsError("MISSING_METRIC", "metric_column is required for box.")
    _check_numeric_column(df, metric, "box")
    
    def calc_box(s):
        s = s.dropna()
        if s.empty:
            return pd.Series({"min": None, "q1": None, "median": None, "q3": None, "max": None, "outliers": []})
        
        q1 = float(s.quantile(0.25))
        q3 = float(s.quantile(0.75))
        median = float(s.median())
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        min_val = float(s[s >= lower_bound].min()) if not s[s >= lower_bound].empty else float(s.min())
        max_val = float(s[s <= upper_bound].max()) if not s[s <= upper_bound].empty else float(s.max())
        
        outliers = [float(x) for x in s[(s < lower_bound) | (s > upper_bound)].tolist()]
        return pd.Series({"min": min_val, "q1": q1, "median": median, "q3": q3, "max": max_val, "outliers": outliers})

    if group_col:
        _check_column_exists(df, group_col)
        result = df.groupby(group_col)[metric].apply(calc_box).unstack().reset_index()
    else:
        stats = calc_box(df[metric])
        result = pd.DataFrame([stats.to_dict()])
        
    return result

def histogram(df: pd.DataFrame, plan: dict) -> pd.DataFrame:
    metric = plan.get("metric_column")
    if not metric:
        raise AnalyticsError("MISSING_METRIC", "metric_column is required for histogram.")
    _check_numeric_column(df, metric, "histogram")
    
    s = df[metric].dropna()
    if s.empty:
        return pd.DataFrame()
        
    counts, bins = np.histogram(s, bins='auto')
    
    hist_data = []
    for i in range(len(counts)):
        hist_data.append({
            "bin_start": float(bins[i]),
            "bin_end": float(bins[i+1]),
            "count": int(counts[i])
        })
        
    return pd.DataFrame(hist_data)


def anomaly_detection(df: pd.DataFrame, plan: dict) -> pd.DataFrame:
    """Deterministic anomaly detection (IQR or Z-Score)."""
    metric = plan.get("metric_column")
    method = plan.get("anomaly_method", "iqr")
    if not method:
        method = "iqr"
    method = method.lower()
    
    threshold = plan.get("anomaly_threshold")
    if threshold is None:
        threshold = 1.5 if method == "iqr" else 3.0
    threshold = float(threshold)
    
    if not metric:
        raise AnalyticsError("MISSING_METRIC", "metric_column is required for anomaly_detection.")
        
    _check_numeric_column(df, metric, "anomaly_detection")
    
    s = df[metric]
    s_numeric = pd.to_numeric(s, errors="coerce")
    
    if s_numeric.isna().all():
        raise AnalyticsError("INVALID_DATA", f"Column '{metric}' contains only invalid/null values.")
        
    result_df = df.copy()
    
    if method == "iqr":
        q1 = s_numeric.quantile(0.25)
        q3 = s_numeric.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr
        
        is_anomaly = (s_numeric < lower_bound) | (s_numeric > upper_bound)
        anomalies = result_df[is_anomaly].copy()
        
        anomalies["_anomaly_score"] = s_numeric[is_anomaly]
        anomalies["_anomaly_reason"] = anomalies["_anomaly_score"].apply(
            lambda x: "value is below the lower IQR bound" if x < lower_bound else "value is above the upper IQR bound"
        )
        
        # We need to return a summary as the main rows?
        # The user requested: rows=[...], lower_bound, upper_bound, anomaly_count, etc.
        # But AnalyticsEngine expects a DataFrame. We can return the anomalies DataFrame,
        # but what about the metadata? The `AnalysisResult` only has columns, rows, row_count, visualization.
        # Let's attach metadata as a JSON string in a special column or just return the anomalies,
        # and we can handle it in the answer formatter or `engine.py`.
        # Alternatively, we can return the anomalies DataFrame and add the bounds as columns.
        anomalies["_lower_bound"] = float(lower_bound)
        anomalies["_upper_bound"] = float(upper_bound)
        anomalies["_total_rows"] = len(df)
        anomalies["_anomaly_rate"] = float(len(anomalies) / len(df) * 100) if len(df) > 0 else 0.0
        
        return anomalies
        
    elif method == "zscore":
        mean = s_numeric.mean()
        std = s_numeric.std()
        
        if pd.isna(std) or std == 0:
            return pd.DataFrame() # No anomalies if standard deviation is 0
            
        z_scores = (s_numeric - mean) / std
        is_anomaly = z_scores.abs() > threshold
        
        anomalies = result_df[is_anomaly].copy()
        anomalies["_anomaly_score"] = z_scores[is_anomaly]
        anomalies["_anomaly_reason"] = "absolute z-score exceeds threshold"
        
        anomalies["_mean"] = float(mean)
        anomalies["_std"] = float(std)
        anomalies["_total_rows"] = len(df)
        anomalies["_anomaly_rate"] = float(len(anomalies) / len(df) * 100) if len(df) > 0 else 0.0
        
        return anomalies
        
    else:
        raise AnalyticsError("UNSUPPORTED_METHOD", f"Anomaly method '{method}' is not supported.")


# Mapping dictionary for strict execution
OPERATION_MAP = {
    "aggregate": aggregate,
    "filter": apply_filter_op,
    "group_by": group_by,
    "sort": sort_dataframe,
    "top_n": top_n,
    "trend": trend_analysis,
    "comparison": comparison,
    "box": box_plot,
    "histogram": histogram,
    "anomaly_detection": anomaly_detection,
}
