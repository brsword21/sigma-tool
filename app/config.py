from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Sigma Shopping Agent"
    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1, le=65535)
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"]
    )

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_timeout_seconds: float = Field(default=30, gt=0, le=120)
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None
    firecrawl_api_key: str | None = None
    firecrawl_timeout_seconds: float = Field(default=20, gt=0, le=120)
    demo_timeout_seconds: float = Field(default=180, gt=0, le=300)

    @property
    def external_services_configured(self) -> bool:
        return all(
            self.is_real_service_value(value)
            for value in (
                self.openai_api_key,
                self.supabase_url,
                self.supabase_service_role_key,
                self.firecrawl_api_key,
            )
        )

    @staticmethod
    def is_real_service_value(value: str | None) -> bool:
        return bool(
            value
            and "..." not in value
            and "<" not in value
            and ">" not in value
            and not value.casefold().startswith(("your-", "replace-"))
        )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str) and not value.lstrip().startswith("["):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
