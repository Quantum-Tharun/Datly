import json
import logging

from app.core.exceptions import DatlyException
from app.models.analysis_plan import AnalysisPlan
from app.models.schema import DatasetProfile, DatasetSchema
from app.services.ai.nvidia_client import nvidia_client
from app.services.ai.prompts import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger("datly.ai.planner")

async def generate_analysis_plan(
    question: str, 
    schema: DatasetSchema, 
    profile: DatasetProfile
) -> AnalysisPlan:
    schema_json = schema.model_dump_json(exclude={"success", "dataset_id", "rows"})
    profile_json = profile.model_dump_json(exclude={"success", "dataset_id", "rows"})
    
    user_prompt = build_user_prompt(question, schema_json, profile_json)
    
    try:
        response_text = await nvidia_client.get_structured_response(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt
        )
        
        import re
        logger.info(f"NIM raw response for question '{question[:80]}': {response_text[:300]}")
        
        # Cleanly extract JSON object using regex if there's markdown or text
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(0)
            
        parsed_json = json.loads(response_text)
        plan = AnalysisPlan.model_validate(parsed_json)
        
        # ── Semantic guardrails (safety net) ──
        q_lower = question.lower()
        if plan.operation.value not in ["group_by", "trend", "percentage"]:
            if "average" in q_lower or "mean" in q_lower:
                plan.operation = "aggregate"
                plan.aggregation = "average"
            elif "total" in q_lower or "sum" in q_lower:
                plan.operation = "aggregate"
                plan.aggregation = "sum"
        
        if "percentage" in q_lower or "share" in q_lower:
            plan.operation = "percentage"
        
        return plan
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM JSON: {e!s}")
        raise DatlyException(
            code="INVALID_ANALYSIS_PLAN",
            message="LLM returned invalid JSON format.",
            status_code=400
        )
    except ValueError as e:
        logger.error(f"Plan validation failed: {e!s}")
        raise DatlyException(
            code="INVALID_ANALYSIS_PLAN",
            message=f"Plan validation: {e!s}",
            status_code=400
        )
    except DatlyException:
        raise
    except Exception as e:  # noqa: BLE001
        logger.error(f"Unexpected planning error: {e!s}")
        raise DatlyException(
            code="LLM_PLANNING_FAILED",
            message="Unexpected error during LLM planning.",
            status_code=500
        )

