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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
def startup_event():
    logger.info("DATLY Backend Starting Up...")
