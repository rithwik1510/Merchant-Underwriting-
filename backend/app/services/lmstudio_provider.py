from __future__ import annotations

import json
import re

import httpx

from app.core.config import get_settings


class LMStudioProvider:
    provider_name = "lmstudio"
    _REQUEST_TIMEOUT_SECONDS = 90.0
    _THINK_BLOCK_PATTERN = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)

    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = self._normalize_base_url(settings.lmstudio_base_url)
        self.model_name = settings.lmstudio_model

    def generate_explanation(self, payload: dict) -> dict:
        output = self._generate(
            payload,
            (
                "Return strict JSON with keys: summary, rationale_sentences, key_strengths, "
                "key_risks, cited_metrics. "
                "summary must be one sentence. "
                "rationale_sentences must contain exactly 4 concise sentences in the style of an underwriting note. "
                "For approved offers, start the first sentence with 'We are offering' and include the final offer terms. "
                "For manual review, start the first sentence with 'We are recommending manual review because'. "
                "For rejected cases, start the first sentence with 'We are unable to offer'. "
                "At least two of the remaining sentences must reference exact merchant metrics. "
                "When benchmark data exists, explicitly compare the merchant metric to the category benchmark using the exact comparison_text phrases supplied in the payload cited_metrics. "
                "Do not infer whether a metric is above or below benchmark on your own. "
                "Do not use vague filler such as 'strong profile' without citing the supporting metric."
            ),
        )
        return self._normalize_explanation_output(payload, output)

    def generate_whatsapp_message(self, payload: dict) -> dict:
        output = self._generate(
            payload,
            "Return strict JSON with keys: message_body, cta_text, tone_label. "
            "Write a proper merchant-facing business notification for WhatsApp, not a text dump. "
            "message_body must be 2 to 4 short sentences and sound ready to send to a merchant. "
            "For approved offers, sentence one should clearly state that the pre-approved offer is ready. "
            "The message must include the product name and the exact offer terms relevant to the selected message_type. "
            "When payload metrics exist, include one short supporting sentence grounded in GMV growth, customer return rate, or refund rate versus category benchmark. "
            "If you reference category comparison, copy the exact comparison_text supplied in the payload instead of inventing your own above/below phrasing. "
            "Do not mention internal labels such as risk tier, underwriting tier, score, policy engine, validation, or templates. "
            "Do not use markdown, bullets, emojis, or placeholders. "
            "Use only the formatted monetary values, percentages, benchmark comparisons, and tenure strings present in the payload.",
        )
        return self._normalize_whatsapp_output(payload, output)

    def _generate(self, payload: dict, output_contract: str) -> dict:
        prompt = {
            "role": "user",
            "content": (
                "You are a constrained business copy generator. "
                "Use only the facts provided. Do not invent numbers or claims. "
                "Do not output chain-of-thought, reasoning traces, or <think> tags. "
                "Output only a single valid JSON object and nothing else. "
                f"{output_contract}\nPayload:\n{json.dumps(payload, ensure_ascii=True)}"
                "\n/no_think"
            ),
        }
        with httpx.Client(timeout=httpx.Timeout(self._REQUEST_TIMEOUT_SECONDS, connect=5.0)) as client:
            request_json = {
                "model": self.model_name,
                "messages": [prompt],
                "temperature": 0.2,
                "max_tokens": 700,
            }
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

    @classmethod
    def _parse_json_content(cls, content: str) -> dict:
        cleaned = cls._THINK_BLOCK_PATTERN.sub("", content).strip()
        cleaned = cleaned.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start >= 0 and end > start:
                return json.loads(cleaned[start : end + 1])
            raise

    @staticmethod
    def _normalize_whatsapp_output(payload: dict, output: dict) -> dict:
        message_body = str(output.get("message_body", "")).strip()
        if not message_body:
            return output

        merchant_name = payload.get("merchant_name")
        product_name = payload.get("product_name")
        decision = payload.get("decision")

        if merchant_name and merchant_name.lower() not in message_body.lower():
            message_body = f"GrabOn update for {merchant_name}: {message_body[0].lower() + message_body[1:] if len(message_body) > 1 else message_body}"

        if product_name and product_name.lower() not in message_body.lower():
            message_body = f"{message_body} This notification relates to {product_name}."

        if decision == "approved" and "pre-approved" not in message_body.lower():
            if "offer is ready" in message_body.lower():
                message_body = re.sub("offer is ready", "pre-approved offer is ready", message_body, flags=re.IGNORECASE)
            elif "offer for" in message_body.lower():
                message_body = re.sub("offer for", "pre-approved offer for", message_body, flags=re.IGNORECASE)

        if decision in {"approved", "manual_review"} and "dashboard" not in message_body.lower():
            suffix = "Please review and accept the offer in your merchant dashboard."
            if decision == "manual_review":
                suffix = "Please review the latest status in your merchant dashboard."
            message_body = f"{message_body.rstrip()} {suffix}"

        output["message_body"] = message_body
        output["cta_text"] = str(output.get("cta_text") or "Review offer")
        output["tone_label"] = str(output.get("tone_label") or "business_notification")
        return output

    @staticmethod
    def _normalize_explanation_output(payload: dict, output: dict) -> dict:
        rationale = output.get("rationale_sentences")
        if not isinstance(rationale, list) or not rationale:
            return output

        decision = payload.get("decision")
        credit_offer = payload.get("credit_offer", {})
        insurance_offer = payload.get("insurance_offer", {})
        merchant_metrics = payload.get("merchant_metrics", {})
        benchmark_metrics = payload.get("benchmark_metrics", {})

        if decision == "approved":
            credit_limit = credit_offer.get("final_limit")
            min_rate = credit_offer.get("interest_rate_min")
            max_rate = credit_offer.get("interest_rate_max")
            gmv_growth = merchant_metrics.get("gmv_growth_12m_pct")
            customer_return = merchant_metrics.get("customer_return_rate")
            category_return = benchmark_metrics.get("category_customer_return_rate")
            refund_rate = merchant_metrics.get("avg_refund_rate_3m") or merchant_metrics.get("return_and_refund_rate")
            category_refund = benchmark_metrics.get("category_refund_rate")
            first_sentence = (
                f"We are offering Rs {LMStudioProvider._money_short_text(credit_limit)} at Tier {str(payload.get('risk_tier', '')).replace('tier_', '')} rates"
                if credit_limit
                else "We are offering finalized terms"
            )
            clauses = []
            if gmv_growth:
                clauses.append(f"your GMV has grown {gmv_growth}% YoY")
            if customer_return:
                clauses.append(f"your customer return rate of {customer_return}% indicates demand stability")
            if refund_rate and category_refund:
                clauses.append(
                    f"your refund rate of {refund_rate}% is {LMStudioProvider._comparison_phrase(refund_rate, category_refund)} the category average of {category_refund}%"
                )
            if clauses:
                rationale[0] = f"{first_sentence} because " + ", ".join(clauses[:3]) + "."
        elif decision == "manual_review":
            if not str(rationale[0]).lower().startswith("we are recommending manual review because"):
                rationale[0] = "We are recommending manual review because the profile needs analyst review before final terms can be issued."
        elif decision == "rejected":
            if not str(rationale[0]).lower().startswith("we are unable to offer"):
                rationale[0] = "We are unable to offer pre-approved terms because the merchant did not clear the core underwriting checks."

        output["rationale_sentences"] = rationale
        return output

    @staticmethod
    def _money_short_text(value: str) -> str:
        amount = float(value)
        if amount >= 10000000:
            return f"{amount / 10000000:.1f}".rstrip("0").rstrip(".") + "Cr"
        if amount >= 100000:
            return f"{amount / 100000:.1f}".rstrip("0").rstrip(".") + "L"
        if amount >= 1000:
            return f"{amount / 1000:.1f}".rstrip("0").rstrip(".") + "K"
        return f"{amount:.1f}".rstrip("0").rstrip(".")

    @staticmethod
    def _comparison_phrase(value: str, benchmark: str) -> str:
        try:
            value_num = float(value)
            benchmark_num = float(benchmark)
        except ValueError:
            return "aligned with"
        if value_num < benchmark_num:
            return "below"
        if value_num > benchmark_num:
            return "above"
        return "in line with"
