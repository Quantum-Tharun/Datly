from app.core.exceptions import DatlyException
from app.models.analysis_result import AnalysisResponse
from app.repositories.dataset_store import dataset_store
from app.services.ai.planner import generate_analysis_plan
from app.services.analytics.answer_formatter import format_answer
from app.services.analytics.engine import execute_plan
from app.services.schema.detector import detect_schema
from app.services.schema.profiler import profile_dataset
from app.services.visualization.chart_selector import VisualizationSelector


class AnalysisService:
    @staticmethod
    async def analyze(dataset_id: str, question: str) -> AnalysisResponse:
        df = dataset_store.get_dataset(dataset_id)
        if df is None:
            raise DatlyException(code="DATASET_NOT_FOUND", message="Dataset not found.", status_code=404)
            
        schema = detect_schema(dataset_id, df)
        profile = profile_dataset(dataset_id, df)
        
        plan = await generate_analysis_plan(question, schema, profile)
        
        result = execute_plan(df, plan)
        
        viz_spec = VisualizationSelector.select_visualization(plan, result, schema)
        answer = format_answer(plan, result, viz_spec)
        
        return AnalysisResponse(
            dataset_id=dataset_id,
            question=question,
            answer=answer,
            result=result,
            visualization=viz_spec,
            analysis_plan=plan
        )
