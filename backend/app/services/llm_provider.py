from __future__ import annotations

from typing import Protocol


class LLMProvider(Protocol):
    provider_name: str
    model_name: str

    def generate_explanation(self, payload: dict) -> dict: ...

    def generate_whatsapp_message(self, payload: dict) -> dict: ...
