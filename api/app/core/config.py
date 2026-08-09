from functools import lru_cache

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/puzzlessbox"
    BETTER_AUTH_BASE_URL: str = "http://localhost:3000/api/auth"
    BETTER_AUTH_JWKS_URL: str = "http://localhost:3000/api/auth/jwks"
    SERVICE_BEARER_TOKEN: str = "change-me-service-bearer"
    SERVICE_OWNER_ID: str = ""  # ponytail: bootstrap MCP principal when set
    MCP_BOOTSTRAP_TOKEN: str = ""
    ENCRYPTION_KEY: str = "change-me-32-byte-encryption-key!!"
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "https://api.puzzlesstool.online/auth/google/callback"
    WEBAPP_URL: str = "http://localhost:3000"
    ENV: str = "dev"
    # Comma-separated browser origins allowed for credentialed CORS
    CORS_ORIGINS: str = "http://localhost:3000,https://pbox.puzzlesstool.online,https://app.puzzlesstool.online"
    # Empty = host-only cookie (local); prod sets .puzzlesstool.online
    SESSION_COOKIE_DOMAIN: str = ""
    SCRAPER_ENABLED: bool = False
    FIRECRAWL_URL: str = "http://localhost:3002"
    FIRECRAWL_BEARER: str = ""
    CAMOUFOX_URL: str = "http://localhost:8080"
    CAMOUFOX_BEARER: str = ""
    DOCS_BASIC_AUTH: str = ""

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if value.startswith("postgres://"):
            value = "postgresql+psycopg2://" + value[len("postgres://") :]
        elif value.startswith("postgresql://"):
            value = "postgresql+psycopg2://" + value[len("postgresql://") :]
        return value

    @model_validator(mode="after")
    def reject_localhost_webapp_in_prod(self) -> "Settings":
        if self.is_prod:
            host = (self.WEBAPP_URL or "").lower()
            if "localhost" in host or "127.0.0.1" in host:
                raise ValueError(
                    "WEBAPP_URL must not point at localhost when ENV=prod"
                )
        return self

    @property
    def is_prod(self) -> bool:
        return self.ENV.lower() == "prod"


@lru_cache
def get_settings() -> Settings:
    return Settings()
