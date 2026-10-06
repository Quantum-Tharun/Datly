
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    NVIDIA_API_KEY: str = ""
    NVIDIA_MODEL: str = "meta/llama-3.2-11b-vision-instruct"
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_FILE_TYPES: str = "csv,xlsx,xls,json"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_STORAGE_BUCKET: str = "datly-datasets"

    SARVAM_API_KEY: str = ""
    SARVAM_STT_MODEL: str = "saaras"
    SARVAM_TTS_MODEL: str = "bulbul"
    SARVAM_STT_MODE: str = "translate"
    SARVAM_TTS_LANGUAGE: str = "en-IN"
    SARVAM_TTS_SPEAKER: str = "shubh"
    SARVAM_TTS_SAMPLE_RATE: int = 24000
    
    VOICE_MAX_AUDIO_SECONDS: int = 30
    VOICE_MAX_TTS_CHARACTERS: int = 2500

    @property
    def allowed_extensions(self) -> list[str]:
        return [ext.strip().lower() for ext in self.ALLOWED_FILE_TYPES.split(",")]

settings = Settings()
