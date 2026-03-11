from __future__ import annotations

from time import perf_counter

import httpx

from app.core.config import get_settings
from app.schemas import LLMProbeRequest, LLMProbeResponse


def probe_llm_provider(request: LLMProbeRequest) -> LLMProbeResponse:
    provider = request.provider.lower()
    if provider == "claude":
        return _probe_claude(request)
    if provider == "lmstudio":
        return _probe_lmstudio(request)
    return LLMProbeResponse(
        provider=provider,
        model=request.model_override or "unknown",
        ok=False,
        status="unreachable",
        error_detail="Unsupported provider",
    )


def _probe_claude(request: LLMProbeRequest) -> LLMProbeResponse:
    settings = get_settings()
    api_key = request.api_key_override or settings.claude_api_key
    model = request.model_override or settings.claude_model
    base_url = settings.claude_base_url.rstrip("/")
    if not api_key:
        return LLMProbeResponse(
            provider="claude",
            model=model,
            ok=False,
            status="missing_key",
            used_override_key=False,
            error_detail="Claude API key is not configured",
        )

    start = perf_counter()
    try:
        with httpx.Client(timeout=httpx.Timeout(20.0, connect=5.0)) as client:
            response = client.post(
                f"{base_url}/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": model,
                    "max_tokens": 16,
                    "messages": [{"role": "user", "content": "Respond with OK."}],
                },
            )
    except httpx.HTTPError as exc:
        return LLMProbeResponse(
            provider="claude",
            model=model,
            ok=False,
            status="unreachable",
            latency_ms=int((perf_counter() - start) * 1000),
            used_override_key=request.api_key_override is not None,
            error_detail=str(exc),
        )

    latency_ms = int((perf_counter() - start) * 1000)
    if response.status_code == 401:
        return LLMProbeResponse(
            provider="claude",
            model=model,
            ok=False,
            status="unauthorized",
            latency_ms=latency_ms,
            used_override_key=request.api_key_override is not None,
            error_detail="Claude rejected the supplied API key",
        )
    if response.status_code == 404:
        return LLMProbeResponse(
            provider="claude",
            model=model,
            ok=False,
            status="invalid_model",
            latency_ms=latency_ms,
            used_override_key=request.api_key_override is not None,
            error_detail="Claude model was not found",
        )
    if response.is_success:
        return LLMProbeResponse(
            provider="claude",
            model=model,
            ok=True,
            status="reachable",
            latency_ms=latency_ms,
            used_override_key=request.api_key_override is not None,
        )
    return LLMProbeResponse(
        provider="claude",
        model=model,
        ok=False,
        status="unreachable",
        latency_ms=latency_ms,
        used_override_key=request.api_key_override is not None,
        error_detail=f"Claude probe failed with status {response.status_code}",
    )


def _probe_lmstudio(request: LLMProbeRequest) -> LLMProbeResponse:
    settings = get_settings()
    model = request.model_override or settings.lmstudio_model
    base_url = settings.lmstudio_base_url.rstrip("/")
    if not base_url.endswith("/v1"):
        base_url = f"{base_url}/v1"

    start = perf_counter()
    try:
        with httpx.Client(timeout=httpx.Timeout(20.0, connect=5.0)) as client:
            response = client.post(
                f"{base_url}/chat/completions",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": "Respond with OK."}],
                    "temperature": 0,
                },
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        status = "invalid_model" if exc.response.status_code == 404 else "unreachable"
        return LLMProbeResponse(
            provider="lmstudio",
            model=model,
            ok=False,
            status=status,
            latency_ms=int((perf_counter() - start) * 1000),
            error_detail=f"LM Studio probe failed with status {exc.response.status_code}",
        )
    except httpx.HTTPError as exc:
        return LLMProbeResponse(
            provider="lmstudio",
            model=model,
            ok=False,
            status="unreachable",
            latency_ms=int((perf_counter() - start) * 1000),
            error_detail=str(exc),
        )

    return LLMProbeResponse(
        provider="lmstudio",
        model=model,
        ok=True,
        status="reachable",
        latency_ms=int((perf_counter() - start) * 1000),
    )
