import pandas as pd
import pytest

from app.models.analysis_plan import (
    AnalysisPlan,
    Operation,
    PlanVisualization,
    VisualizationType,
)
from app.services.analytics.engine import execute_plan
from app.services.visualization.chart_selector import VisualizationSelector


def get_test_df():
    return pd.DataFrame({
        "revenue": [100, 110, 105, 95, 100, 105, 1000],
        "city": ["A", "A", "A", "B", "B", "B", "C"],
        "temp": [25, 26, 25, 24, 25, 26, -50]
    })

def test_anomaly_iqr():
    plan = AnalysisPlan(
        operation=Operation.anomaly_detection,
        metric_column="revenue",
        anomaly_method="iqr",
        anomaly_threshold=1.5
    )
    result = execute_plan(get_test_df(), plan)
    
    assert "meta" in result
    meta = result["meta"]
    assert meta["anomaly_count"] == 1
    assert meta["column"] == "revenue"
    
    data = result["data"]
    assert len(data) == 1
    assert data[0]["revenue"] == 1000
    assert "_anomaly_score" in data[0]

def test_anomaly_zscore():
    plan = AnalysisPlan(
        operation=Operation.anomaly_detection,
        metric_column="temp",
        anomaly_method="zscore",
        anomaly_threshold=2.0
    )
    result = execute_plan(get_test_df(), plan)
    
    meta = result["meta"]
    assert meta["anomaly_count"] == 1
    assert result["data"][0]["temp"] == -50

def test_no_anomalies():
    plan = AnalysisPlan(
        operation=Operation.anomaly_detection,
        metric_column="revenue",
        anomaly_method="iqr",
        anomaly_threshold=200.0  # High threshold
    )
    result = execute_plan(get_test_df(), plan)
    
    assert result["meta"]["anomaly_count"] == 0
    assert len(result["data"]) == 0

def test_non_numeric_anomaly():
    plan = AnalysisPlan(
        operation=Operation.anomaly_detection,
        metric_column="city"
    )
    from app.core.exceptions import DatlyException
    with pytest.raises(DatlyException) as exc:
        execute_plan(get_test_df(), plan)
    assert "INCOMPATIBLE_OPERATION" in str(exc.value.code)

def test_anomaly_chart_selection():
    plan = AnalysisPlan(
        operation=Operation.anomaly_detection,
        metric_column="revenue",
    )
    result = execute_plan(get_test_df(), plan)
    viz = VisualizationSelector.select_visualization(plan, result)
    assert viz.type == VisualizationType.box
    assert viz.y == "revenue"
    
    # Test explicitly requested scatter
    plan.visualization = PlanVisualization(type=VisualizationType.scatter)
    viz_explicit = VisualizationSelector.select_visualization(plan, result)
    assert viz_explicit.type == VisualizationType.scatter
