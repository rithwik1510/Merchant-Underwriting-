from __future__ import annotations


class TemplateProvider:
    provider_name = "template_fallback"
    model_name = "deterministic_templates"

    def generate_sanity_check(self, payload: dict) -> dict:
        return {
            "status": "passed",
            "issue_codes": [],
            "notes": ["Deterministic packet is available for explanation and communication."],
            "suggested_explanation_focus": ["Lead with the deterministic offer and strongest benchmark-backed metrics."],
            "suggested_message_focus": ["Keep the merchant-facing message concise and grounded in approved offer terms."],
        }

    def generate_explanation(self, payload: dict) -> dict:
        facts = payload["key_facts"][:2]
        merchant_name = payload["merchant_name"]
        decision = payload["decision"].replace("_", " ")
        tier = payload["risk_tier"].replace("_", " ").title()
        metrics = payload.get("merchant_metrics", {})
        benchmarks = payload.get("benchmark_metrics", {})
        credit_offer = payload.get("credit_offer", {})
        insurance_offer = payload.get("insurance_offer", {})

        summary = f"{merchant_name} is {decision} at {tier}."
        rationale = [self._build_offer_sentence(payload, credit_offer, insurance_offer)]
        if metrics.get("gmv_growth_12m_pct"):
            rationale.append(
                f"Your GMV has grown {metrics['gmv_growth_12m_pct']}% over the last 12 months, which supports business momentum."
            )
        if metrics.get("customer_return_rate"):
            sentence = f"Your customer return rate of {metrics['customer_return_rate']}%"
            if benchmarks.get("category_customer_return_rate"):
                sentence += f" is compared against the category benchmark of {benchmarks['category_customer_return_rate']}%"
            rationale.append(f"{sentence}, which indicates repeat demand stability.")
        if metrics.get("avg_refund_rate_3m") or metrics.get("return_and_refund_rate"):
            merchant_refund = metrics.get("avg_refund_rate_3m") or metrics.get("return_and_refund_rate")
            sentence = f"Your refund rate of {merchant_refund}%"
            if benchmarks.get("category_refund_rate"):
                sentence += f" is measured against the category benchmark of {benchmarks['category_refund_rate']}%"
            rationale.append(f"{sentence}, which directly shapes the risk posture.")
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
        gmv_growth = payload.get("gmv_growth_12m_pct")
        customer_return = payload.get("customer_return_rate")
        category_return = payload.get("category_customer_return_rate")
        refund_rate = payload.get("refund_rate")
        category_refund = payload.get("category_refund_rate")

        support_sentence = None
        if gmv_growth:
            support_sentence = f"This reflects {gmv_growth} year-over-year GMV growth on GrabOn."
        elif customer_return and category_return:
            support_sentence = (
                f"Your customer return rate of {customer_return} is being assessed against the category benchmark of {category_return}."
            )
        elif refund_rate and category_refund:
            support_sentence = f"Your refund rate of {refund_rate} is being assessed against the category benchmark of {category_refund}."

        if message_type == "credit_offer":
            if decision == "approved":
                body = (
                    f"GrabOn update for {merchant_name}: your pre-approved GrabCredit offer is ready. "
                    f"You are eligible for working capital up to {payload.get('credit_limit') or 'shared on review'} at {payload.get('interest_range') or 'applicable'} with tenure options of {payload.get('tenure_options_text') or 'shared on review'}."
                )
            elif decision == "manual_review":
                body = (
                    f"GrabOn update for {merchant_name}: your GrabCredit profile is shortlisted and under final review. "
                    f"Indicative working capital up to {payload.get('credit_limit') or 'shared after review'} is available subject to review."
                )
            else:
                body = f"GrabOn update for {merchant_name}: we are unable to issue a GrabCredit pre-approved offer at this time based on the current underwriting review."
        elif message_type == "insurance_offer":
            if decision == "approved":
                body = (
                    f"GrabOn update for {merchant_name}: your pre-approved GrabInsurance offer is ready. "
                    f"You are eligible for {payload.get('policy_type') or 'business protection'} coverage up to {payload.get('coverage_amount') or 'shared on review'} with a premium of {payload.get('premium_amount') or 'applicable'}."
                )
            elif decision == "manual_review":
                body = (
                    f"GrabOn update for {merchant_name}: your GrabInsurance profile is shortlisted and under final review. "
                    f"Indicative coverage up to {payload.get('coverage_amount') or 'shared after review'} is available subject to review."
                )
            else:
                body = f"GrabOn update for {merchant_name}: we are unable to issue a GrabInsurance pre-approved offer at this time based on the current underwriting review."
        else:
            if decision == "approved":
                body = (
                    f"GrabOn update for {merchant_name}: your pre-approved GrabCredit and GrabInsurance offers are ready. "
                    f"You are eligible for working capital up to {payload.get('credit_limit') or 'shared on review'} and insurance coverage up to {payload.get('coverage_amount') or 'shared on review'}."
                )
            elif decision == "manual_review":
                body = (
                    f"GrabOn update for {merchant_name}: your profile is shortlisted and under final review. "
                    f"Indicative credit and insurance terms are available subject to review."
                )
            else:
                body = f"GrabOn update for {merchant_name}: we are unable to issue a pre-approved offer at this time based on the current underwriting review."

        if support_sentence and decision != "rejected":
            body = f"{body} {support_sentence}"

        if decision == "approved":
            body = f"{body} Please review and accept the offer in your merchant dashboard."
        elif decision == "manual_review":
            body = f"{body} Our team will share the final outcome after review."

        return {
            "message_body": body,
            "cta_text": "Review offer",
            "tone_label": "business_notification",
        }

    def _build_offer_sentence(self, payload: dict, credit_offer: dict, insurance_offer: dict) -> str:
        decision = payload["decision"]
        if decision == "approved":
            credit_text = (
                f"credit up to Rs {self._money_short(credit_offer.get('final_limit'))}"
                if credit_offer.get("final_limit")
                else "credit terms"
            )
            coverage_text = (
                self._money_short(insurance_offer.get("coverage_amount")) or "shared coverage"
            )
            return (
                f"We are offering {credit_text} "
                f"and insurance coverage up to {coverage_text} "
                f"at {payload['risk_tier'].replace('_', ' ').title()} terms because the finalized underwriting signals support this offer."
            )
        if decision == "manual_review":
            return (
                f"We are recommending manual review because the profile needs an analyst check before finalizing credit and insurance terms."
            )
        return "We are unable to offer pre-approved terms because the merchant did not clear the core underwriting checks."

    @staticmethod
    def _money_short(value: str | None) -> str | None:
        if not value:
            return None
        try:
            amount = float(value)
        except ValueError:
            return value
        if amount >= 10000000:
            return f"{amount / 10000000:.1f}".rstrip("0").rstrip(".") + "Cr"
        if amount >= 100000:
            return f"{amount / 100000:.1f}".rstrip("0").rstrip(".") + "L"
        if amount >= 1000:
            return f"{amount / 1000:.1f}".rstrip("0").rstrip(".") + "K"
        return f"{amount:.1f}".rstrip("0").rstrip(".")
