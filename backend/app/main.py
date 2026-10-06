from fastapi import FastAPI

from app.api.router import api_router
from app.core.exceptions import DatlyException, datly_exception_handler
from app.core.logging import logger

app = FastAPI(
    title="DATLY API",
    description="Backend API for DATLY - Schema-Agnostic Natural Language Data Analyst",
    version="1.0.0",
)

app.add_exception_handler(DatlyException, datly_exception_handler)

from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
def startup_event():
    logger.info("DATLY Backend Starting Up...")
