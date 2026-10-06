import pandas as pd


def detect_inferred_type(series: pd.Series) -> str:
    dtype = str(series.dtype)
    print("DEBUG col:", series.name, "dtype:", dtype)
    
    if "int" in dtype:
        return "integer"
    if "float" in dtype:
        return "float"
    if "bool" in dtype:
        return "boolean"
    if "datetime" in dtype:
        return "datetime"
        
    if dtype in ("object", "string", "str") or "str" in dtype or dtype == "O":
        sample = series.dropna().head(20)
        if len(sample) > 0:
            str_sample = sample.astype(str).str.lower()
            if set(str_sample).issubset({"true", "false", "yes", "no", "y", "n"}):
                return "boolean"
                
            try:
                pd.to_datetime(sample, errors="raise")
                return "datetime"
            except Exception:  # noqa: BLE001, S110
                pass
                
        unique_count = series.nunique()
        total_count = len(series)
        
        if total_count > 0:
            unique_ratio = unique_count / total_count
            if unique_ratio > 0.5:
                avg_len = series.dropna().astype(str).str.len().mean()
                if avg_len > 30:
                    return "text"
            
        return "categorical"
        
    return "categorical"
