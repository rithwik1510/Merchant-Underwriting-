from __future__ import annotations


class TemplateProvider:
    provider_name = "template_fallback"
    model_name = "deterministic_templates"

    def generate_explanation(self, payload: dict) -> dict:
        facts = payload["key_facts"][:3]
        decision = payload["decision"].replace("_", " ")
        summary = f"{payload['merchant_name']} is {decision} at {payload['risk_tier'].replace('_', ' ').title()}."
        rationale = [
            f"{payload['merchant_name']} was evaluated using finalized merchant performance data and category benchmarks.",
        ]
        rationale.extend(facts[:2] if facts else ["The final decision is based on the stored underwriting run facts only."])
        rationale.append("The offer terms shown are deterministic outputs from the underwriting engine, not AI-generated numbers.")
        return {
            "summary": summary,
            "rationale_sentences": rationale[:5],
            "key_strengths": facts[:2],
            "key_risks": facts[2:3],
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
