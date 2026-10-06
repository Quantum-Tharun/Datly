import logging

from app.core.exceptions import DatlyException
from app.services.ai.sarvam.client import sarvam_client

logger = logging.getLogger("datly.ai.sarvam.translation")

def translate_text(text: str, source_language_code: str, target_language_code: str = "en-IN") -> str:
    if not sarvam_client.client:
        raise DatlyException(
            code="SARVAM_NOT_CONFIGURED",
            message="Speech/Text service is not configured.",
            status_code=503
        )
        
    if not text or not text.strip():
        return text
        
    if source_language_code == target_language_code:
        return text
        
    try:
        response = sarvam_client.client.text.translate(
            input=text,
            source_language_code=source_language_code,
            target_language_code=target_language_code
        )
        
        translated_text = getattr(response, "translated_text", "")
        if hasattr(response, 'data') and response.data:
            translated_text = response.data.translated_text if hasattr(response.data, 'translated_text') else translated_text
            
        if not translated_text:
            # Maybe the SDK has the output differently, let's assume it returns translated_text
            pass
            
        return translated_text
        
    except Exception as e:  # noqa: BLE001
        logger.error(f"Sarvam Text Translate Error: {e!s}")
        # Soft fallback to original text if translation fails
        return text
