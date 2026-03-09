EXPECTED_OUTCOMES = {
    "m_freshbasket": ("approved", "tier_1"),
    "m_trendvibe": ("approved", "tier_2"),
    "m_quickbyte": ("rejected", "rejected"),
    "m_wanderdeals": ("rejected", "rejected"),
    "m_glowup": ("manual_review", "tier_3"),
    "m_homenest": ("approved", "tier_1"),
    "m_fitkart": ("approved", "tier_2"),
    "m_streetstyle": ("manual_review", "tier_3"),
    "m_fooddash": ("approved", "tier_2"),
    "m_triptrail": ("manual_review", "tier_3"),
}


def test_underwriting_run_persists_and_returns_details(client) -> None:
    client.post("/api/seed/init")
    response = client.post("/api/underwriting/run/m_freshbasket")
    assert response.status_code == 200
    body = response.json()

    assert body["decision"] == "approved"
    assert body["risk_tier"] == "tier_1"
    assert body["features"]["annual_gmv_12m"] > 0
    assert body["credit_offer"]["offer_status"] == "eligible"
    assert body["insurance_offer"]["offer_status"] == "eligible"
    assert len(body["score_reasons"]) == 8


def test_seeded_merchants_match_expected_outcome_classes(client) -> None:
    client.post("/api/seed/init")

    for merchant_id, expected in EXPECTED_OUTCOMES.items():
        response = client.post(f"/api/underwriting/run/{merchant_id}")
        assert response.status_code == 200
        body = response.json()
        assert (body["decision"], body["risk_tier"]) == expected, merchant_id


def test_underwriting_runs_list_endpoint_returns_created_runs(client) -> None:
    client.post("/api/seed/init")
    client.post("/api/underwriting/run/m_freshbasket")
    client.post("/api/underwriting/run/m_quickbyte")

    response = client.get("/api/underwriting/runs")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert {item["merchant_id"] for item in body} == {"m_freshbasket", "m_quickbyte"}


def test_rejection_and_manual_review_reasons_are_grouped(client) -> None:
    client.post("/api/seed/init")

    rejected = client.post("/api/underwriting/run/m_quickbyte").json()
    assert rejected["hard_stop_triggered"] is True
    assert any(reason["reason_code"] == "refund_rate_too_high" for reason in rejected["hard_stop_reasons"])

    manual = client.post("/api/underwriting/run/m_glowup").json()
    assert manual["manual_review_triggered"] is True
    assert any(reason["reason_code"] == "high_gmv_volatility" for reason in manual["manual_review_reasons"])


def test_manual_review_uses_final_tier_for_credit_pricing(client) -> None:
    client.post("/api/seed/init")
    manual = client.post("/api/underwriting/run/m_glowup").json()

    assert manual["decision"] == "manual_review"
    assert manual["risk_tier"] == "tier_3"
    assert manual["credit_offer"]["offer_status"] == "manual_review"
    assert manual["credit_offer"]["interest_rate_min"] is None
    assert manual["credit_offer"]["interest_rate_max"] is None
    assert manual["credit_offer"]["tenure_options"] == [3, 6]
    # Tier-3 multiplier path should significantly reduce final limit vs base limit.
    assert manual["credit_offer"]["final_limit"] < manual["credit_offer"]["base_limit"]


def test_manual_review_uses_final_tier_for_insurance_pricing(client) -> None:
    client.post("/api/seed/init")
    manual = client.post("/api/underwriting/run/m_glowup").json()

    assert manual["decision"] == "manual_review"
    assert manual["risk_tier"] == "tier_3"
    assert manual["insurance_offer"]["offer_status"] == "manual_review"
    # Tier-3 pricing path should apply elevated premium logic, not tier-1 defaults.
    assert manual["insurance_offer"]["premium_rate"] == 0.018
