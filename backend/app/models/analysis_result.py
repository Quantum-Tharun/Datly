from enum import Enum
from typing import Any

from pydantic import BaseModel


class VisualizationType(str, Enum):
    bar = "bar"
    line = "line"
    area = "area"
    pie = "pie"
    donut = "donut"
    scatter = "scatter"
    box = "box"
    histogram = "histogram"
    table = "table"
    kpi = "kpi"
    none = "none"


class VisualizationSpec(BaseModel):
    type: VisualizationType
    x: str | None = None
    y: str | None = None
    title: str | None = None

from app.models.analysis_plan import AnalysisPlan


class AnalysisResponse(BaseModel):
    success: bool = True
    dataset_id: str | None = None
    question: str
    answer: str
    result: dict[str, Any]
    visualization: VisualizationSpec
    analysis_plan: AnalysisPlan
