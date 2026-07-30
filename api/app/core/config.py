from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/puzzlessbox"
    BETTER_AUTH_BASE_URL: str = "http://localhost:3000/api/auth"
    BETTER_AUTH_JWKS_URL: str = "http://localhost:3000/api/auth/jwks"
    SERVICE_BEARER_TOKEN: str = "change-me-service-bearer"
    ENCRYPTION_KEY: str = "change-me-32-byte-encryption-key!!"
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "https://api.puzzlesstool.online/auth/google/callback"
    ENV: str = "dev"
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

    @property
    def is_prod(self) -> bool:
        return self.ENV.lower() == "prod"


@lru_cache
def get_settings() -> Settings:
    return Settings()
