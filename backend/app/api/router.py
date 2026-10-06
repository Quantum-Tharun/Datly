from fastapi import APIRouter

from app.api.endpoints import analysis, datasets, voice

api_router = APIRouter()

@api_router.get("/health")
def health_check():
    return {"status": "ok"}

api_router.include_router(datasets.router, prefix="/datasets", tags=["Datasets"])
api_router.include_router(analysis.router, prefix="/datasets", tags=["Analysis"])
api_router.include_router(voice.router, prefix="/voice", tags=["Voice"])
