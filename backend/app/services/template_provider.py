from __future__ import annotations


class TemplateProvider:
    provider_name = "template_fallback"
    model_name = "deterministic_templates"

    def generate_explanation(self, payload: dict) -> dict:
        facts = payload["key_facts"][:2]
        merchant_name = payload["merchant_name"]
        decision = payload["decision"].replace("_", " ")
        tier = payload["risk_tier"].replace("_", " ").title()
        metrics = payload.get("merchant_metrics", {})
        benchmarks = payload.get("benchmark_metrics", {})
        offer_summary = payload.get("offer_summary", "")

        summary = f"{merchant_name} is {decision} at {tier}."
        rationale = [offer_summary or f"{merchant_name} is being reviewed using finalized underwriting facts."]
        if metrics.get("gmv_growth_12m_pct"):
            rationale.append(
                f"Your GMV has grown {metrics['gmv_growth_12m_pct']}% over the last 12 months, which supports business momentum."
            )
        if metrics.get("customer_return_rate"):
            sentence = f"Your customer return rate is {metrics['customer_return_rate']}%"
            if benchmarks.get("category_customer_return_rate"):
                sentence += f" versus a category benchmark of {benchmarks['category_customer_return_rate']}%"
            rationale.append(f"{sentence}, which signals repeat demand quality.")
        if metrics.get("avg_refund_rate_3m") or metrics.get("return_and_refund_rate"):
            merchant_refund = metrics.get("avg_refund_rate_3m") or metrics.get("return_and_refund_rate")
            sentence = f"Your refund and return pressure is {merchant_refund}%"
            if benchmarks.get("category_refund_rate"):
                sentence += f" against a category benchmark of {benchmarks['category_refund_rate']}%"
            rationale.append(f"{sentence}, which directly informs the offer risk posture.")
        if facts:
            rationale.append(facts[0])
        rationale = rationale[:4]
        return {
            "summary": summary,
            "rationale_sentences": rationale,
            "key_strengths": facts[:2],
            "key_risks": payload["key_facts"][2:3],
            "cited_metrics": payload.get("cited_metrics", []),
        }

    def generate_whatsapp_message(self, payload: dict) -> dict:
        message_type = payload.get("message_type", "combined_offer")
        decision = payload["decision"]
        merchant_name = payload["merchant_name"]

        if message_type == "credit_offer":
            if decision == "approved":
                body = (
                    f"{merchant_name}, your GrabCredit offer is ready. "
                    f"Credit up to {payload.get('credit_limit') or 'shared on review'} at {payload.get('interest_range') or 'applicable'}."
                )
            elif decision == "manual_review":
                body = (
                    f"{merchant_name}, your GrabCredit profile is pre-qualified subject to review. "
                    f"Indicative credit up to {payload.get('credit_limit') or 'shared after review'}."
                )
            else:
                body = f"{merchant_name}, your profile was reviewed. Additional eligibility is required before a credit offer can be shared."
        elif message_type == "insurance_offer":
            if decision == "approved":
                body = (
                    f"{merchant_name}, your GrabInsurance offer is ready. "
                    f"Coverage up to {payload.get('coverage_amount') or 'shared on review'} with premium {payload.get('premium_amount') or 'applicable'}."
                )
            elif decision == "manual_review":
                body = (
                    f"{merchant_name}, your GrabInsurance profile is pre-qualified subject to review. "
                    f"Indicative coverage up to {payload.get('coverage_amount') or 'shared after review'}."
                )
            else:
                body = f"{merchant_name}, your profile was reviewed. Additional eligibility is required before an insurance offer can be shared."
        else:
            if decision == "approved":
                body = (
                    f"{merchant_name}, your GrabCredit and GrabInsurance offers are ready. "
                    f"Credit up to {payload.get('credit_limit') or 'shared on review'} and coverage up to {payload.get('coverage_amount') or 'shared on review'}."
                )
            elif decision == "manual_review":
                body = (
                    f"{merchant_name}, your profile is pre-qualified subject to final review. "
                    f"Indicative credit and insurance terms are available for review."
                )
            else:
                body = f"{merchant_name}, your profile was reviewed. Additional eligibility is required before an offer can be shared."
        return {
            "message_body": body,
            "cta_text": "View offer",
            "tone_label": "professional",
        }
