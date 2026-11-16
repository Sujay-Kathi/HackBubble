import pytest
from httpx import AsyncClient
from app.core.config import get_settings
from app.core.exceptions import AppException, NotFoundError
from app.core.security import create_access_token, decode_access_token
from app.models import (
    Base,
    Hackathon,
    Notification,
    Team,
    User,
    UserProfile,
    UserResume,
)


@pytest.mark.asyncio
async def test_root_endpoint(async_client: AsyncClient):
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "HackBubble"
    assert data["version"] == "0.1.0"
    assert "health" in data


@pytest.mark.asyncio
async def test_health_check_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["app_name"] == "HackBubble"
    assert payload["data"]["version"] == "0.1.0"
    assert "status" in payload["data"]


def test_settings_load():
    settings = get_settings()
    assert settings.APP_NAME == "HackBubble"
    assert settings.EMBEDDING_DIMENSION == 384
    assert settings.API_V1_PREFIX == "/api/v1"


def test_token_creation_and_decoding():
    token = create_access_token(subject="user-123", claims={"role": "participant"})
    decoded = decode_access_token(token)
    assert decoded["sub"] == "user-123"
    assert decoded["role"] == "participant"


def test_models_metadata_registration():
    table_names = Base.metadata.tables.keys()
    assert "users" in table_names
    assert "user_profiles" in table_names
    assert "user_skills" in table_names
    assert "hackathons" in table_names
    assert "teams" in table_names
    assert "team_roles" in table_names
    assert "team_applications" in table_names
    assert "team_members" in table_names
    assert "user_resumes" in table_names
    assert "candidate_embeddings" in table_names
    assert "notifications" in table_names
    assert "audit_logs" in table_names
