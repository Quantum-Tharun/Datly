from fastapi import APIRouter, File, UploadFile

from app.core.exceptions import DatlyException
from app.models.dataset import DatasetMetadata
from app.models.schema import DatasetProfile, DatasetSchema
from app.repositories.dataset_store import dataset_store
from app.services.ingestion.service import process_upload
from app.services.schema.detector import detect_schema
from app.services.schema.profiler import profile_dataset

router = APIRouter()

@router.post("/upload", response_model=DatasetMetadata)
def upload_dataset(file: UploadFile = File(...)):  # noqa: B008
    """Upload a dataset for analysis. Supports CSV, XLSX, and JSON."""
    return process_upload(file)

@router.get("/{dataset_id}", response_model=DatasetMetadata)
def get_dataset(dataset_id: str):
    """Retrieve metadata for a previously uploaded dataset."""
    metadata = dataset_store.get_metadata(dataset_id)
    if not metadata:
        raise DatlyException(code="DATASET_NOT_FOUND", message="Dataset not found.", status_code=404)
    return metadata

@router.get("/{dataset_id}/schema", response_model=DatasetSchema)
def get_dataset_schema(dataset_id: str):
    """Retrieve the detected schema for a dataset."""
    df = dataset_store.get_dataset(dataset_id)
    if df is None:
        raise DatlyException(code="DATASET_NOT_FOUND", message="Dataset not found.", status_code=404)
    try:
        return detect_schema(dataset_id, df)
    except Exception as e:  # noqa: BLE001
        raise DatlyException(code="INTERNAL_ERROR", message=f"Failed to detect schema: {e!s}", status_code=500)

@router.get("/{dataset_id}/profile", response_model=DatasetProfile)
def get_dataset_profile(dataset_id: str):
    """Retrieve the basic profile for a dataset."""
    df = dataset_store.get_dataset(dataset_id)
    if df is None:
        raise DatlyException(code="DATASET_NOT_FOUND", message="Dataset not found.", status_code=404)
    try:
        return profile_dataset(dataset_id, df)
    except Exception as e:  # noqa: BLE001
        raise DatlyException(code="INTERNAL_ERROR", message=f"Failed to profile dataset: {e!s}", status_code=500)
