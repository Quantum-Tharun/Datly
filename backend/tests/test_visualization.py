from app.models.analysis_plan import Aggregation, AnalysisPlan, Operation
from app.models.analysis_result import VisualizationType
from app.services.visualization.chart_selector import VisualizationSelector


def test_visualization_scalar_none():
    plan = AnalysisPlan(operation=Operation.aggregate, aggregation=Aggregation.sum, metric_column="revenue")
    result = {"value": 5000}
    viz = VisualizationSelector.select_visualization(plan, result)
    assert viz.type == VisualizationType.kpi

def test_visualization_group_by_bar():
    plan = AnalysisPlan(operation=Operation.group_by, group_column="city", metric_column="revenue")
    result = {"data": [{"city": "A", "revenue": 10}]}
    viz = VisualizationSelector.select_visualization(plan, result)
    assert viz.type == VisualizationType.bar

def test_visualization_time_series_line():
    plan = AnalysisPlan(operation=Operation.trend, group_column="date", metric_column="revenue")
    result = {"data": [{"date": "2024-01-01", "revenue": 10}]}
    viz = VisualizationSelector.select_visualization(plan, result)
    assert viz.type == VisualizationType.line
    
def test_visualization_scatter():
    plan = AnalysisPlan(operation=Operation.comparison, group_column="quantity", metric_column="revenue")
    result = {"data": [{"quantity": 2, "revenue": 10}]}
    viz = VisualizationSelector.select_visualization(plan, result)
    assert viz.type == VisualizationType.scatter
    
def test_visualization_pie_percentage():
    plan = AnalysisPlan(operation=Operation.percentage, group_column="region", metric_column="revenue")
    result = {"data": [{"region": "A", "percentage": 50}, {"region": "B", "percentage": 50}]}
    viz = VisualizationSelector.select_visualization(plan, result)
    assert viz.type == VisualizationType.pie

def test_visualization_bar_percentage_many_categories():
    plan = AnalysisPlan(operation=Operation.percentage, group_column="region", metric_column="revenue")
    result = {"data": [{"region": str(i), "percentage": 10} for i in range(15)]}
    viz = VisualizationSelector.select_visualization(plan, result)
    assert viz.type == VisualizationType.bar
    
def test_visualization_histogram():
    plan = AnalysisPlan(operation=Operation.histogram, metric_column="profit")
    result = {"data": [{"profit_bin": "1-10", "count": 5}]}
    viz = VisualizationSelector.select_visualization(plan, result)
    assert viz.type == VisualizationType.histogram

def test_visualization_box():
    plan = AnalysisPlan(operation=Operation.box, metric_column="profit", group_column="region")
    result = {"data": [{"region": "North", "min": 1, "max": 10}]}
    viz = VisualizationSelector.select_visualization(plan, result)
    assert viz.type == VisualizationType.box

def test_visualization_explicit_override():
    from app.models.analysis_plan import PlanVisualization
    plan = AnalysisPlan(
        operation=Operation.group_by, 
        group_column="city", 
        metric_column="revenue",
        visualization=PlanVisualization(type=VisualizationType.pie)
    )
    result = {"data": [{"city": "A", "revenue": 10}]}
    viz = VisualizationSelector.select_visualization(plan, result)
    assert viz.type == VisualizationType.pie

def test_visualization_fallback_table():
    plan = AnalysisPlan(operation=Operation.filter)
    result = {"data": [{"col1": "A", "col2": "B"}]}
    viz = VisualizationSelector.select_visualization(plan, result)
    assert viz.type == VisualizationType.table
