
import pandas as pd

from app.models.dataset import DatasetMetadata


class InMemoryDatasetStore:
    def __init__(self):
        self._dataframes: dict[str, pd.DataFrame] = {}
        self._metadata: dict[str, DatasetMetadata] = {}

    def save_dataset(self, metadata: DatasetMetadata, df: pd.DataFrame) -> None:
        print(f"DEBUG: save_dataset called on {id(self)} with ds_id {metadata.dataset_id}")
        self._metadata[metadata.dataset_id] = metadata
        self._dataframes[metadata.dataset_id] = df
        print(f"DEBUG: current keys in metadata: {list(self._metadata.keys())}")

    def get_dataset(self, dataset_id: str) -> pd.DataFrame | None:
        return self._dataframes.get(dataset_id)

    def get_metadata(self, dataset_id: str) -> DatasetMetadata | None:
        print(f"DEBUG: get_metadata called on {id(self)} with ds_id {dataset_id}")
        print(f"DEBUG: current keys in metadata: {list(self._metadata.keys())}")
        return self._metadata.get(dataset_id)

    def exists(self, dataset_id: str) -> bool:
        return dataset_id in self._metadata

dataset_store = InMemoryDatasetStore()
