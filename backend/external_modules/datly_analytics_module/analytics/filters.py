import pandas as pd

from .models import AnalyticsError


def apply_filters(df: pd.DataFrame, filters: list[dict]) -> pd.DataFrame:
    """
    Applies deterministic filters to the DataFrame.
    
    Supported operators:
    - equals
    - not_equals
    - greater_than
    - less_than
    - greater_than_or_equal
    - less_than_or_equal
    - contains
    - date_before
    - date_after
    - date_between
    """
    result = df.copy()
    
    for f in filters:
        col = f.get("column")
        op = f.get("operator")
        val = f.get("value")
        
        if not col or not op:
            raise AnalyticsError("INVALID_FILTER", "Filter must contain 'column' and 'operator'.")
            
        if col not in result.columns:
            raise AnalyticsError("MISSING_COLUMN", f"Column '{col}' does not exist in the dataset.")
            
        if op == "equals":
            result = result[result[col] == val]
        elif op == "not_equals":
            result = result[result[col] != val]
        elif op == "greater_than":
            result = result[result[col] > val]
        elif op == "less_than":
            result = result[result[col] < val]
        elif op == "greater_than_or_equal":
            result = result[result[col] >= val]
        elif op == "less_than_or_equal":
            result = result[result[col] <= val]
        elif op == "contains":
            # For contains, treat safely as string
            result = result[result[col].astype(str).str.contains(str(val), na=False)]
        elif op == "date_before":
            result = result[pd.to_datetime(result[col]) < pd.to_datetime(val)]
        elif op == "date_after":
            result = result[pd.to_datetime(result[col]) > pd.to_datetime(val)]
        elif op == "date_between":
            val_end = f.get("value_end")
            if val_end is None:
                raise AnalyticsError("INVALID_FILTER", "date_between requires 'value_end'.")
            result = result[
                (pd.to_datetime(result[col]) >= pd.to_datetime(val)) &
                (pd.to_datetime(result[col]) <= pd.to_datetime(val_end))
            ]
        else:
            raise AnalyticsError("UNSUPPORTED_OPERATOR", f"Filter operator '{op}' is not supported.")
            
    return result
