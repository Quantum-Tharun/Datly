from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel

from app.core.exceptions import DatlyException
from app.services.ai.sarvam.speech_to_text import transcribe_audio
from app.services.ai.sarvam.text_to_speech import synthesize_speech
from app.services.analysis_service import AnalysisService

router = APIRouter()

class SynthesizeRequest(BaseModel):
    text: str

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):  # noqa: B008
    if not file or not file.filename:
        raise DatlyException(code="INVALID_FILE", message="No audio file uploaded.", status_code=400)
    
    # Read file content directly
    audio_bytes = await file.read()
    if not audio_bytes:
        raise DatlyException(code="INVALID_FILE", message="Audio file is empty.", status_code=400)
        
    result = transcribe_audio(audio_bytes)
    return {
        "success": True,
        "transcript": result["text"],
        "language_code": result["language_code"]
    }

@router.post("/synthesize")
async def synthesize(request: SynthesizeRequest):
    audio_bytes = synthesize_speech(request.text)
    return Response(content=audio_bytes, media_type="audio/wav")

import uuid

# Simple in-memory store for generated audio
audio_store: dict[str, bytes] = {}

@router.post("/analyze")
async def analyze_voice(dataset_id: str = Form(...), file: UploadFile = File(...)):  # noqa: B008
    if not file or not file.filename:
        raise DatlyException(code="INVALID_FILE", message="No audio file uploaded.", status_code=400)
        
    audio_bytes = await file.read()
    if not audio_bytes:
        raise DatlyException(code="INVALID_FILE", message="Audio file is empty.", status_code=400)
        
    # 1. STT
    stt_result = transcribe_audio(audio_bytes)
    transcript = stt_result["text"]
    original_lang = stt_result["language_code"]
    
    if not transcript or not transcript.strip():
        raise DatlyException(code="INVALID_QUESTION", message="Could not understand audio. Transcript is empty.", status_code=400)
        
    # 2. Analyze
    analysis_response = await AnalysisService.analyze(dataset_id, transcript)
    
    # 3. Translate answer back to regional language if necessary
    final_answer = analysis_response.answer
    if original_lang and original_lang != "en-IN":
        from app.services.ai.sarvam.text_translation import translate_text
        final_answer = translate_text(
            text=analysis_response.answer,
            source_language_code="en-IN",
            target_language_code=original_lang
        )
        # We also need to update the transcript returned to frontend so it matches the original language,
        # but the STT in translate mode already returned English. If the user wants the result in their language,
        # the text is fine. The response has the translated final_answer.
    
    # 4. TTS
    tts_audio_bytes = synthesize_speech(final_answer, language_code=original_lang)
    
    # 5. Store audio temporarily
    audio_id = f"audio_{uuid.uuid4().hex[:8]}"
    audio_store[audio_id] = tts_audio_bytes
    
    # 6. Return JSON with audio path
    return {
        "success": True,
        "dataset_id": analysis_response.dataset_id,
        "transcript": transcript,
        "answer": final_answer,
        "result": analysis_response.result,
        "visualization": analysis_response.visualization.model_dump() if hasattr(analysis_response.visualization, "model_dump") else analysis_response.visualization.dict(),
        "audio": {
            "content_type": "audio/wav",
            "available": True,
            "audio_url": f"/api/v1/voice/audio/{audio_id}"
        }
    }

@router.get("/audio/{audio_id}")
async def get_audio(audio_id: str):
    if audio_id not in audio_store:
        raise DatlyException(code="AUDIO_NOT_FOUND", message="Audio not found or expired.", status_code=404)
        
    audio_bytes = audio_store[audio_id]
    return Response(content=audio_bytes, media_type="audio/wav")
