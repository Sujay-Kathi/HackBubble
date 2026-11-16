"""
Storage Provider Layer.

Provides unified file storage abstraction supporting:
- Local filesystem storage (default, `./uploads`).
- Supabase Storage bucket (`resumes`).

Prevents hard crashes by gracefully falling back to local storage if
Supabase credentials are not configured.
"""

from __future__ import annotations

import abc
import hashlib
import logging
from pathlib import Path
from typing import Optional
from uuid import UUID

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class BaseStorageProvider(abc.ABC):
    """Abstract interface for file persistence."""

    @abc.abstractmethod
    async def save_file(
        self, user_id: UUID, file_name: str, file_bytes: bytes
    ) -> tuple[str, str]:
        """
        Store file bytes.
        Returns tuple of (storage_key, sha256_file_hash).
        """

    @abc.abstractmethod
    async def get_file_bytes(self, storage_key: str) -> bytes:
        """Retrieve stored file bytes."""

    @abc.abstractmethod
    async def file_exists(self, storage_key: str) -> bool:
        """Check whether the stored file exists."""

    @abc.abstractmethod
    async def delete_file(self, storage_key: str) -> bool:
        """Delete file if possible. Returns True if removed."""

    def get_local_path(self, storage_key: str) -> Optional[Path]:
        """Return local file path if stored locally on disk."""
        return None


class LocalStorageProvider(BaseStorageProvider):
    """Stores files on the local filesystem partitioned by user_id."""

    def __init__(self, base_dir: str | Path | None = None) -> None:
        self.base_dir = Path(base_dir or settings.LOCAL_STORAGE_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_target_path(self, user_id: UUID, file_hash: str) -> Path:
        user_dir = self.base_dir / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir / f"{file_hash}.pdf"

    async def save_file(
        self, user_id: UUID, file_name: str, file_bytes: bytes
    ) -> tuple[str, str]:
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        target_path = self._get_target_path(user_id, file_hash)
        with open(target_path, "wb") as f:
            f.write(file_bytes)
        return str(target_path), file_hash

    async def get_file_bytes(self, storage_key: str) -> bytes:
        path = Path(storage_key)
        if not path.is_file():
            raise FileNotFoundError(f"Storage file not found: {storage_key}")
        with open(path, "rb") as f:
            return f.read()

    async def file_exists(self, storage_key: str) -> bool:
        return Path(storage_key).is_file()

    async def delete_file(self, storage_key: str) -> bool:
        path = Path(storage_key)
        if path.is_file():
            try:
                path.unlink()
                return True
            except OSError as err:
                logger.warning("Could not delete file %s: %s", path, err)
        return False

    def get_local_path(self, storage_key: str) -> Optional[Path]:
        path = Path(storage_key)
        return path if path.is_file() else None


class SupabaseStorageProvider(BaseStorageProvider):
    """
    Stores files in a Supabase Storage bucket via REST API.
    Gracefully falls back to local storage if credentials are incomplete.
    """

    def __init__(self) -> None:
        self.url = (settings.SUPABASE_URL or "").rstrip("/")
        self.key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY
        self.bucket = settings.SUPABASE_STORAGE_BUCKET or "resumes"
        self._local_fallback = LocalStorageProvider()

    def _is_configured(self) -> bool:
        return bool(self.url and self.key)

    async def save_file(
        self, user_id: UUID, file_name: str, file_bytes: bytes
    ) -> tuple[str, str]:
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        if not self._is_configured():
            logger.info("Supabase not fully configured; falling back to local storage.")
            return await self._local_fallback.save_file(user_id, file_name, file_bytes)

        import httpx

        object_path = f"{user_id}/{file_hash}.pdf"
        endpoint = f"{self.url}/storage/v1/object/{self.bucket}/{object_path}"
        headers = {
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/pdf",
            "x-upsert": "true",
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(endpoint, content=file_bytes, headers=headers)
            if resp.status_code not in (200, 201):
                logger.warning("Supabase upload failed (%s): %s; using local fallback", resp.status_code, resp.text)
                return await self._local_fallback.save_file(user_id, file_name, file_bytes)

        storage_key = f"supabase://{self.bucket}/{object_path}"
        return storage_key, file_hash

    async def get_file_bytes(self, storage_key: str) -> bytes:
        if storage_key.startswith("supabase://") and self._is_configured():
            import httpx

            rel_path = storage_key.replace(f"supabase://{self.bucket}/", "")
            endpoint = f"{self.url}/storage/v1/object/{self.bucket}/{rel_path}"
            headers = {"Authorization": f"Bearer {self.key}"}

            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(endpoint, headers=headers)
                if resp.status_code == 200:
                    return resp.content
                raise FileNotFoundError(f"Supabase object not found ({resp.status_code}): {storage_key}")

        return await self._local_fallback.get_file_bytes(storage_key)

    async def file_exists(self, storage_key: str) -> bool:
        if storage_key.startswith("supabase://") and self._is_configured():
            try:
                await self.get_file_bytes(storage_key)
                return True
            except Exception:
                return False
        return await self._local_fallback.file_exists(storage_key)

    async def delete_file(self, storage_key: str) -> bool:
        if storage_key.startswith("supabase://") and self._is_configured():
            import httpx

            rel_path = storage_key.replace(f"supabase://{self.bucket}/", "")
            endpoint = f"{self.url}/storage/v1/object/{self.bucket}/{rel_path}"
            headers = {"Authorization": f"Bearer {self.key}"}

            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.delete(endpoint, headers=headers)
                return resp.status_code in (200, 204)

        return await self._local_fallback.delete_file(storage_key)

    def get_local_path(self, storage_key: str) -> Optional[Path]:
        return self._local_fallback.get_local_path(storage_key)


def get_storage_provider(provider: str | None = None) -> BaseStorageProvider:
    """Factory returning the active storage provider."""
    active_provider = (provider or settings.STORAGE_PROVIDER).lower()
    if active_provider == "supabase":
        return SupabaseStorageProvider()
    return LocalStorageProvider()
