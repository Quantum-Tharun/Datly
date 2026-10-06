from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_sarvam():
    with patch("app.services.ai.sarvam.speech_to_text.sarvam_client") as mock_stt_client, \
         patch("app.services.ai.sarvam.text_to_speech.sarvam_client") as mock_tts_client:
        
        mock_stt_client.client = MagicMock()
        mock_tts_client.client = MagicMock()
        
        # Mock STT
        mock_stt_response = MagicMock(transcript="Mock transcribed text.", text="Mock transcribed text.", data=MagicMock(transcript="Mock transcribed text."))
        mock_stt_client.client.speech_to_text.transcribe.return_value = mock_stt_response
        mock_stt_client.client.speech_to_text.translate.return_value = mock_stt_response
        
        # Mock TTS
        mock_tts_response = MagicMock()
        mock_tts_response.audios = ["bW9ja19hdWRpbw=="] # base64 of "mock_audio"
        mock_tts_client.client.text_to_speech.convert.return_value = mock_tts_response
        
        yield (mock_stt_client, mock_tts_client)

def test_transcribe(mock_sarvam):
    response = client.post(
        "/api/v1/voice/transcribe",
        files={"file": ("test.wav", b"dummy audio content", "audio/wav")}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["transcript"] == "Mock transcribed text."

def test_synthesize(mock_sarvam):
    response = client.post(
        "/api/v1/voice/synthesize",
        json={"text": "Hello world"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"
    assert response.content == b"mock_audio"

@patch("app.services.analysis_service.AnalysisService.analyze", new_callable=AsyncMock)
def test_analyze_voice(mock_analyze, mock_sarvam):
    # Setup mock analysis response
    mock_analysis_response = MagicMock()
    mock_analysis_response.dataset_id = "ds_123"
    mock_analysis_response.answer = "This is a mock answer."
    mock_analysis_response.result = {"data": []}
    mock_analysis_response.visualization.model_dump.return_value = {"type": "none"}
    
    mock_analyze.return_value = mock_analysis_response

    response = client.post(
        "/api/v1/voice/analyze",
        data={"dataset_id": "ds_123"},
        files={"file": ("test.wav", b"dummy audio", "audio/wav")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["transcript"] == "Mock transcribed text."
    assert data["answer"] == "This is a mock answer."
    assert "audio_url" in data["audio"]
    
    # Test getting the audio
    audio_url = data["audio"]["audio_url"]
    audio_response = client.get(audio_url)
    assert audio_response.status_code == 200
    assert audio_response.content == b"mock_audio"
