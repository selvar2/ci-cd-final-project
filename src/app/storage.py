import json
from pathlib import Path
from typing import Any

from .config import get_settings
from .logging_config import get_logger

logger = get_logger(__name__)

try:
    from google.cloud import storage  # type: ignore
except Exception:  # pragma: no cover - optional dependency for tests
    storage = None


class StorageClient:
    """Simple storage abstraction backed by Cloud Storage or local disk."""

    def __init__(self, storage_path: Path | None = None) -> None:
        settings = get_settings()
        self.bucket_name = settings.gcs_bucket
        self.storage_path = storage_path or settings.storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _local_file(self, name: str) -> Path:
        return self.storage_path / name

    def _gcs_blob(self, name: str):  # pragma: no cover - requires GCP
        if not self.bucket_name or storage is None:
            return None
        client = storage.Client()
        bucket = client.bucket(self.bucket_name)
        return bucket.blob(name)

    def read_json(self, name: str, default: Any) -> Any:
        """Read JSON content from storage, returning default if missing."""

        if blob := self._gcs_blob(name):  # pragma: no cover
            try:
                data = blob.download_as_text()
                return json.loads(data)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Falling back to default after GCS read error: %s", exc)
                return default

        local_file = self._local_file(name)
        if local_file.exists():
            try:
                return json.loads(local_file.read_text())
            except json.JSONDecodeError:
                logger.warning("Invalid JSON detected in %s; resetting file", local_file)
        return default

    def write_json(self, name: str, payload: Any) -> None:
        """Persist JSON data to storage."""

        serialized = json.dumps(payload, ensure_ascii=False, indent=2)
        if blob := self._gcs_blob(name):  # pragma: no cover
            blob.upload_from_string(serialized, content_type="application/json")
            return

        local_file = self._local_file(name)
        local_file.write_text(serialized)


storage_client = StorageClient()
