from pathlib import Path
from types import SimpleNamespace

from app.services.llm_settings_service import get_llm_settings


def test_llm_settings_endpoint_reads_current_config(client, monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.llm_settings_service.get_settings",
        lambda: SimpleNamespace(
            llm_provider="lmstudio",
            lmstudio_base_url="http://127.0.0.1:1234",
            lmstudio_model="qwen/qwen3-8b",
            claude_model="claude-sonnet-4-6",
            claude_base_url="https://api.anthropic.com/v1",
            claude_api_key="sk-ant-1234567890",
        ),
    )

    response = client.get("/api/llm/settings")

    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "lmstudio"
    assert body["claude_api_key_configured"] is True
    assert body["claude_api_key_masked"].startswith("sk-a")


def test_llm_settings_endpoint_updates_env_and_provider(client, monkeypatch, tmp_path: Path) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text(
        "\n".join(
            [
                "LLM_PROVIDER=lmstudio",
                "LMSTUDIO_BASE_URL=http://127.0.0.1:1234",
                "LMSTUDIO_MODEL=qwen/qwen3-8b",
                "CLAUDE_MODEL=claude-sonnet-4-6",
                "CLAUDE_BASE_URL=https://api.anthropic.com/v1",
                "CLAUDE_API_KEY=",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    def fake_reload():
        return SimpleNamespace(
            llm_provider="claude",
            lmstudio_base_url="http://127.0.0.1:1234",
            lmstudio_model="qwen/qwen3-8b",
            claude_model="claude-sonnet-4-6",
            claude_base_url="https://api.anthropic.com/v1",
            claude_api_key="sk-ant-live-key",
        )

    monkeypatch.setattr("app.services.llm_settings_service.get_env_file_path", lambda: env_path)
    monkeypatch.setattr("app.services.llm_settings_service.reload_settings", fake_reload)
    monkeypatch.setattr("app.services.llm_settings_service.get_settings", fake_reload)

    response = client.put(
        "/api/llm/settings",
        json={
            "provider": "claude",
            "claude_api_key": "sk-ant-live-key",
            "claude_model": "claude-sonnet-4-6",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "claude"
    assert body["claude_api_key_configured"] is True
    env_text = env_path.read_text(encoding="utf-8")
    assert "LLM_PROVIDER=claude" in env_text
    assert "CLAUDE_API_KEY=sk-ant-live-key" in env_text


def test_get_llm_settings_masks_short_keys(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.llm_settings_service.get_settings",
        lambda: SimpleNamespace(
            llm_provider="claude",
            lmstudio_base_url="http://127.0.0.1:1234",
            lmstudio_model="qwen/qwen3-8b",
            claude_model="claude-sonnet-4-6",
            claude_base_url="https://api.anthropic.com/v1",
            claude_api_key="abcd1234",
        ),
    )

    settings = get_llm_settings()

    assert settings.claude_api_key_masked == "********"
