from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_repo_root() -> Path:
    # apps/api/app/settings.py → repo root
    return Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Job Pilot"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    database_url: str = ""
    memory_path: str = ""
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    apify_token: str | None = None
    alert_poll_minutes: int = 60

    @property
    def repo_root(self) -> Path:
        return _default_repo_root()

    @property
    def data_dir(self) -> Path:
        return self.repo_root / "data"

    @property
    def memory_dir(self) -> Path:
        if self.memory_path:
            return Path(self.memory_path)
        return self.repo_root / "memory"

    @property
    def resume_originals_dir(self) -> Path:
        return self.memory_dir / "rag" / "resume" / "originals"

    @property
    def sqlite_path(self) -> Path:
        return self.data_dir / "job_pilot_v2.sqlite"

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return f"sqlite:///{self.sqlite_path.as_posix()}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
