from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "AgroVisor Edge API"
    environment: str = "development"
    database_url: str = "sqlite:///./agrovisor.db"
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def resolved_database_url(self) -> str:
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        if url.startswith("sqlite:///"):
            raw_path = url[len("sqlite:///"):]
            path_obj = Path(raw_path)
            if not path_obj.is_absolute():
                abs_path = (BACKEND_DIR / path_obj).resolve().as_posix()
                return f"sqlite:///{abs_path}"
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()
