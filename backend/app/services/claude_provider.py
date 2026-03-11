from __future__ import annotations

import json

import httpx

from app.core.config import get_settings


class ClaudeProvider:
    provider_name = "claude"

    def __init__(self, api_key: str | None = None, model_name: str | None = None, base_url: str | None = None) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.claude_api_key
        self.model_name = model_name or settings.claude_model
        self.base_url = (base_url or settings.claude_base_url).rstrip("/")

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
            (
                "Return strict JSON with keys: message_body, cta_text, tone_label. "
                "Write concise merchant-facing WhatsApp copy. "
                "Do not mention internal labels such as risk tier, underwriting tier, score, or policy engine. "
                "Use only the formatted monetary values and rate strings present in the payload."
            ),
        )

    def _generate(self, payload: dict, output_contract: str) -> dict:
        if not self.api_key:
            raise RuntimeError("Claude API key is not configured")

        with httpx.Client(timeout=httpx.Timeout(30.0, connect=5.0)) as client:
            response = client.post(
                f"{self.base_url}/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": self.model_name,
                    "max_tokens": 600,
                    "temperature": 0.2,
                    "system": (
                        "You are a constrained business copy generator. "
                        "Use only the facts provided. Do not invent numbers or claims."
                    ),
                    "messages": [
                        {
                            "role": "user",
                            "content": f"{output_contract}\nPayload:\n{json.dumps(payload, ensure_ascii=True)}",
                        }
                    ],
                },
            )
            response.raise_for_status()
            data = response.json()
            content = "".join(
                block.get("text", "")
                for block in data.get("content", [])
                if isinstance(block, dict) and block.get("type") == "text"
            )
            return self._parse_json_content(content)

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
