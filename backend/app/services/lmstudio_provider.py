from __future__ import annotations

import json

import httpx

from app.core.config import get_settings


class LMStudioProvider:
    provider_name = "lmstudio"

    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = self._normalize_base_url(settings.lmstudio_base_url)
        self.model_name = settings.lmstudio_model

    def generate_explanation(self, payload: dict) -> dict:
        return self._generate(
            payload,
            (
                "Return strict JSON with keys: summary, rationale_sentences, key_strengths, "
                "key_risks, cited_metrics. rationale_sentences must contain exactly 3 to 5 concise sentences."
            ),
        )

    def generate_whatsapp_message(self, payload: dict) -> dict:
        return self._generate(
            payload,
            "Return strict JSON with keys: message_body, cta_text, tone_label. "
            "Write concise merchant-facing WhatsApp copy. "
            "Do not mention internal labels such as risk tier, underwriting tier, score, or policy engine. "
            "Use only the formatted monetary values and rate strings present in the payload.",
        )

    def _generate(self, payload: dict, output_contract: str) -> dict:
        prompt = {
            "role": "user",
            "content": (
                "You are a constrained business copy generator. "
                "Use only the facts provided. Do not invent numbers or claims. "
                f"{output_contract}\nPayload:\n{json.dumps(payload, ensure_ascii=True)}"
            ),
        }
        with httpx.Client(timeout=httpx.Timeout(20.0, connect=5.0)) as client:
            request_json = {
                "model": self.model_name,
                "messages": [prompt],
                "temperature": 0.2,
                "response_format": {"type": "json_object"},
            }
            response = client.post(f"{self.base_url}/chat/completions", json=request_json)
            if response.status_code == 400:
                request_json.pop("response_format", None)
                response = client.post(f"{self.base_url}/chat/completions", json=request_json)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return self._parse_json_content(content)

    @staticmethod
    def _normalize_base_url(base_url: str) -> str:
        normalized = base_url.rstrip("/")
        if not normalized.endswith("/v1"):
            normalized = f"{normalized}/v1"
        return normalized

    @staticmethod
    def _parse_json_content(content: str) -> dict:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            start = content.find("{")
            end = content.rfind("}")
            if start >= 0 and end > start:
                return json.loads(content[start : end + 1])
            raise
