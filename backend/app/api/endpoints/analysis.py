
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class AnalysisRequest(BaseModel):
    question: str

from app.models.analysis_result import AnalysisResponse
from app.services.analysis_service import AnalysisService


@router.post("/{dataset_id}/analyze", response_model=AnalysisResponse)
async def analyze_dataset(dataset_id: str, request: AnalysisRequest):
    return await AnalysisService.analyze(dataset_id, request.question)

