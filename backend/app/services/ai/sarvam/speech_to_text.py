import logging
from typing import IO

from app.core.config import settings
from app.core.exceptions import DatlyException
from app.services.ai.sarvam.client import sarvam_client

logger = logging.getLogger("datly.ai.sarvam.stt")

def transcribe_audio(audio_data: IO[bytes] | bytes | str) -> dict:
    if not sarvam_client.client:
        raise DatlyException(
            code="SARVAM_NOT_CONFIGURED",
            message="Speech service is not configured.",
            status_code=503
        )
        
    try:
        if settings.SARVAM_STT_MODE == "translate":
            response = sarvam_client.client.speech_to_text.translate(
                file=audio_data,
                model=settings.SARVAM_STT_MODEL
            )
        else:
            response = sarvam_client.client.speech_to_text.transcribe(
                file=audio_data,
                model=settings.SARVAM_STT_MODEL
            )
        # response should have a transcript field based on typical SDKs
        # If response has a data field containing transcript, handle that
        # We will assume response.transcript exists, or we might need to inspect the SDK response object.
        transcript_text = getattr(response, "transcript", "") or getattr(response, "text", "")
        # The docs say response could be SpeechToTextResponse
        if hasattr(response, 'data') and response.data:
            transcript_text = response.data.transcript if hasattr(response.data, 'transcript') else transcript_text
            
        if not transcript_text:
            raise DatlyException(
                code="SARVAM_INVALID_RESPONSE",
                message="Received empty transcript from speech service.",
                status_code=502
            )
            
        # Optional: capture language if available
        lang = getattr(response, "language_code", "en-IN")
        if hasattr(response, 'data') and hasattr(response.data, 'language_code'):
             lang = response.data.language_code
             
        return {
            "text": transcript_text,
            "language_code": lang
        }
    except DatlyException:
        raise
    except Exception as e:  # noqa: BLE001
        logger.error(f"Sarvam STT Error: {e!s}")
        if "timeout" in str(e).lower():
            raise DatlyException(code="SARVAM_STT_TIMEOUT", message="Speech transcription timed out.", status_code=504)
        raise DatlyException(code="SARVAM_STT_FAILED", message="Speech transcription failed.", status_code=502)
