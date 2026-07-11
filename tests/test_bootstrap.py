from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.bootstrap import build_application_services
from app.config import Settings
from app.main import create_app


def complete_settings() -> Settings:
    return Settings(
        _env_file=None,
        openai_api_key="test-openai",
        supabase_url="https://example.supabase.co",
        supabase_service_role_key="test-supabase",
        firecrawl_api_key="test-firecrawl",
    )


def test_complete_configuration_builds_application_services() -> None:
    database = MagicMock()
    with (
        patch("app.bootstrap.create_client", return_value=database),
        patch("app.bootstrap.OpenAIStructuredClient"),
    ):
        services = build_application_services(complete_settings())

    assert services.sessions._client is database
    assert services.products._client is database
    assert services.orchestrator.source_names == ["olx_firecrawl", "ceneo_firecrawl"]
    assert services.orchestrator._explanations is not None


def test_incomplete_configuration_stays_controlled() -> None:
    settings = Settings(_env_file=None, environment="test")
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        build_application_services(settings)

    app = create_app(settings)
    with TestClient(app) as client:
        response = client.post("/sessions")
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "services_not_configured"


def test_placeholder_credentials_are_not_treated_as_configured() -> None:
    settings = Settings(
        _env_file=None,
        openai_api_key="sk-...",
        supabase_url="https://<project-ref>.supabase.co",
        supabase_service_role_key="eyJ...",
        firecrawl_api_key="fc-...",
    )
    assert settings.external_services_configured is False
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        build_application_services(settings)
