from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException

from app.core.config import get_env_file_path, get_settings, reload_settings
from app.schemas import LLMSettingsResponse, LLMSettingsUpdateRequest


SUPPORTED_PROVIDERS = {"lmstudio", "claude"}


def get_llm_settings() -> LLMSettingsResponse:
    settings = get_settings()
    return LLMSettingsResponse(
        provider=settings.llm_provider,
        lmstudio_base_url=settings.lmstudio_base_url,
        lmstudio_model=settings.lmstudio_model,
        claude_model=settings.claude_model,
        claude_base_url=settings.claude_base_url,
        claude_api_key_configured=bool(settings.claude_api_key),
        claude_api_key_masked=_mask_api_key(settings.claude_api_key),
    )


def update_llm_settings(request: LLMSettingsUpdateRequest) -> LLMSettingsResponse:
    provider = request.provider.strip().lower()
    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=400, detail="Unsupported LLM provider")

    env_path = get_env_file_path()
    env_map = _read_env_file(env_path)

    env_map["LLM_PROVIDER"] = provider
    if request.lmstudio_base_url:
        env_map["LMSTUDIO_BASE_URL"] = request.lmstudio_base_url.strip()
    if request.lmstudio_model:
        env_map["LMSTUDIO_MODEL"] = request.lmstudio_model.strip()
    if request.claude_model:
        env_map["CLAUDE_MODEL"] = request.claude_model.strip()
    if request.claude_base_url:
        env_map["CLAUDE_BASE_URL"] = request.claude_base_url.strip()
    if request.claude_api_key is not None:
        env_map["CLAUDE_API_KEY"] = request.claude_api_key.strip()

    _write_env_file(env_path, env_map)
    reload_settings()
    return get_llm_settings()


def _mask_api_key(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}{'*' * (len(value) - 8)}{value[-4:]}"


def _read_env_file(path: Path) -> dict[str, str]:
    env_map: dict[str, str] = {}
    if not path.exists():
        return env_map
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env_map[key.strip()] = value.strip()
    return env_map


def _write_env_file(path: Path, env_map: dict[str, str]) -> None:
    existing_lines: list[str] = []
    if path.exists():
        existing_lines = path.read_text(encoding="utf-8").splitlines()

    seen: set[str] = set()
    updated_lines: list[str] = []
    for raw_line in existing_lines:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or "=" not in raw_line:
            updated_lines.append(raw_line)
            continue
        key, _ = raw_line.split("=", 1)
        normalized_key = key.strip()
        if normalized_key in env_map:
            updated_lines.append(f"{normalized_key}={env_map[normalized_key]}")
            seen.add(normalized_key)
        else:
            updated_lines.append(raw_line)

    for key, value in env_map.items():
        if key not in seen:
            updated_lines.append(f"{key}={value}")

    path.write_text("\n".join(updated_lines).rstrip() + "\n", encoding="utf-8")
