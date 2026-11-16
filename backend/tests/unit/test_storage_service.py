import tempfile
import uuid
import pytest
from pathlib import Path
from app.services.storage_service import LocalStorageProvider, SupabaseStorageProvider, get_storage_provider


@pytest.mark.asyncio
async def test_local_storage_lifecycle():
    with tempfile.TemporaryDirectory() as tmp_dir:
        provider = LocalStorageProvider(base_dir=tmp_dir)
        user_id = uuid.uuid4()
        test_bytes = b"%PDF-1.4 test resume content"

        # 1. Save
        storage_key, file_hash = await provider.save_file(user_id, "test.pdf", test_bytes)
        assert storage_key.endswith(".pdf")
        assert len(file_hash) == 64

        # 2. Exists
        assert await provider.file_exists(storage_key) is True

        # 3. Read
        read_bytes = await provider.get_file_bytes(storage_key)
        assert read_bytes == test_bytes

        # 4. Local path
        local_path = provider.get_local_path(storage_key)
        assert local_path is not None
        assert local_path.is_file()

        # 5. Delete
        assert await provider.delete_file(storage_key) is True
        assert await provider.file_exists(storage_key) is False


@pytest.mark.asyncio
async def test_storage_provider_factory():
    local_p = get_storage_provider("local")
    assert isinstance(local_p, LocalStorageProvider)

    # When supabase credentials are not set, Supabase provider falls back cleanly
    supabase_p = get_storage_provider("supabase")
    assert isinstance(supabase_p, SupabaseStorageProvider)
    assert supabase_p._is_configured() is False
