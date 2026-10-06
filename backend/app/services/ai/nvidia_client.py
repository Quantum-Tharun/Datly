import logging

from openai import AsyncOpenAI

from app.core.config import settings
from app.core.exceptions import DatlyException

logger = logging.getLogger("datly.ai")

class NvidiaLLMClient:
    def __init__(self):
        self.api_key = settings.NVIDIA_API_KEY
        self.model = settings.NVIDIA_MODEL
        self.base_url = settings.NVIDIA_BASE_URL
        
        if not self.api_key:
            logger.warning("NVIDIA_API_KEY is missing! Using mock API responses for offline testing.")
            self.client = None
        else:
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=30.0
            )
            
    async def get_structured_response(self, system_prompt: str, user_prompt: str) -> str:
        if not self.client:
            raise DatlyException(
                code="LLM_NOT_CONFIGURED",
                message="NVIDIA API Key is missing. Cannot reach LLM.",
                status_code=500
            )
            
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=1024
            )
            return str(response.choices[0].message.content)
        except Exception as e:  # noqa: BLE001
            logger.error(f"NVIDIA API Error: {e!s}")
            raise DatlyException(
                code="LLM_UNAVAILABLE",
                message=f"Failed to communicate with NVIDIA API: {e!s}",
                status_code=502
            )

nvidia_client = NvidiaLLMClient()
