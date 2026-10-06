from enum import Enum

from pydantic import BaseModel


class Operation(str, Enum):
    aggregate = "aggregate"
    filter = "filter"
    group_by = "group_by"
    sort = "sort"
    top_n = "top_n"
    comparison = "comparison"
    trend = "trend"
    percentage = "percentage"
    box = "box"
    histogram = "histogram"
    anomaly_detection = "anomaly_detection"

class Aggregation(str, Enum):
    sum = "sum"
    average = "average"
    count = "count"
    min = "min"
    max = "max"
    median = "median"
    standard_deviation = "standard_deviation"
    variance = "variance"
    count_distinct = "count_distinct"

class VisualizationType(str, Enum):
    bar = "bar"
    line = "line"
    scatter = "scatter"
    table = "table"
    kpi = "kpi"
    none = "none"
    auto = "auto"
    pie = "pie"
    histogram = "histogram"
    area = "area"
    donut = "donut"
    box = "box"

class PlanVisualization(BaseModel):
    type: VisualizationType = VisualizationType.auto
    x: str | None = None
    y: str | None = None
    title: str | None = None

class TimeGranularity(str, Enum):
    day = "day"
    week = "week"
    month = "month"
    quarter = "quarter"
    year = "year"

class IntentType(str, Enum):
    analysis = "analysis"
    unsupported = "unsupported"
    clarification_required = "clarification_required"

class FilterOperator(str, Enum):
    equals = "equals"
    not_equals = "not_equals"
    greater_than = "greater_than"
    less_than = "less_than"
    greater_than_or_equal = "greater_than_or_equal"
    less_than_or_equal = "less_than_or_equal"
    contains = "contains"
    date_before = "date_before"
    date_after = "date_after"
    date_between = "date_between"

class FilterCondition(BaseModel):
    column: str
    operator: FilterOperator
    value: str | int | float | bool
    secondary_value: str | int | float | bool | None = None

class AnalysisPlan(BaseModel):
    operation: Operation
    metric_column: str | None = None
    metric_columns: list[str] | None = None
    group_column: str | None = None
    filters: list[FilterCondition] | None = None
    aggregation: Aggregation | None = None
    aggregations: list[Aggregation] | None = None
    sort: str | None = None
    sort_column: str | None = None
    limit: int | None = None
    anomaly_method: str | None = None
    anomaly_threshold: float | None = None
    visualization: PlanVisualization | None = None
    time_granularity: TimeGranularity | None = None
    intent_type: IntentType = IntentType.analysis
    unsupported_reason: str | None = None

