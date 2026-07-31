from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SERVICE_BEARER_TOKEN: str = "change-me-service-bearer"
    MCP_API_BASE_URL: str = "http://puzzlessbox-api:8000"
    ENV: str = "dev"

    @property
    def is_prod(self) -> bool:
        return self.ENV.lower() == "prod"


@lru_cache
def get_settings() -> Settings:
    return Settings()
