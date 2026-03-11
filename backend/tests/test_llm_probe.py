from types import SimpleNamespace


def test_claude_probe_reports_missing_key(client, monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.llm_probe_service.get_settings",
        lambda: SimpleNamespace(
            claude_api_key=None,
            claude_model="claude-3-5-sonnet-latest",
            claude_base_url="https://api.anthropic.com/v1",
            lmstudio_model="qwen/qwen3-8b",
            lmstudio_base_url="http://127.0.0.1:1234",
        ),
    )

    response = client.post("/api/llm/probe", json={"provider": "claude"})
    assert response.status_code == 200
    assert response.json()["status"] == "missing_key"


def test_claude_probe_reports_unauthorized_for_fake_key(client, monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.llm_probe_service.get_settings",
        lambda: SimpleNamespace(
            claude_api_key="env-key",
            claude_model="claude-3-5-sonnet-latest",
            claude_base_url="https://api.anthropic.com/v1",
            lmstudio_model="qwen/qwen3-8b",
            lmstudio_base_url="http://127.0.0.1:1234",
        ),
    )

    class FakeResponse:
        status_code = 401
        is_success = False

    class FakeHttpxClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def post(self, *args, **kwargs):
            return FakeResponse()

    monkeypatch.setattr("app.services.llm_probe_service.httpx.Client", FakeHttpxClient)

    response = client.post(
        "/api/llm/probe",
        json={"provider": "claude", "api_key_override": "fake-key"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "unauthorized"
    assert body["used_override_key"] is True
