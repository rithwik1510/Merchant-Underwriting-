import json
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    app_env: str = "development"
    app_port: int = 8000
    lmstudio_base_url: str = "http://localhost:1234/v1"
    lmstudio_model: str = "qwen3:8b"
    llm_provider: str = "lmstudio"
    claude_api_key: str | None = None
    claude_model: str = "claude-sonnet-4-6"
    claude_base_url: str = "https://api.anthropic.com/v1"
    app_base_url: str = "http://localhost:8000"
    twilio_account_sid: str | None = None
    twilio_auth_token: str | None = None
    twilio_whatsapp_from: str | None = None
    twilio_content_sid: str | None = None
    twilio_content_variables_json: str | None = None

    @property
    def twilio_content_variables(self) -> dict[str, str] | None:
        if not self.twilio_content_variables_json:
            return None
        return json.loads(self.twilio_content_variables_json)


@lru_cache
def get_settings() -> Settings:
    return Settings()


def reload_settings() -> Settings:
    get_settings.cache_clear()
    return get_settings()


def get_env_file_path() -> Path:
    return Path(__file__).resolve().parents[2] / ".env"
