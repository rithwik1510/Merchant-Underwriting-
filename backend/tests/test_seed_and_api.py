from app.seed_data import BENCHMARKS, MERCHANTS


def test_seed_init_populates_data(client) -> None:
    response = client.post("/api/seed/init")
    assert response.status_code == 200
    body = response.json()
    assert body["merchants_created"] == 10
    assert body["benchmarks_created"] == 6
    assert body["monthly_metrics_created"] == sum(len(m.monthly_metrics) for m in MERCHANTS)
    assert body["policy_created"] is True


def test_seed_init_is_idempotent(client) -> None:
    client.post("/api/seed/init")
    response = client.post("/api/seed/init")
    assert response.status_code == 200
    body = response.json()
    assert body["merchants_created"] == 0
    assert body["benchmarks_created"] == 0
    assert body["monthly_metrics_created"] == 0
    assert body["policy_created"] is False


def test_list_merchants_returns_seeded_merchants(client) -> None:
    client.post("/api/seed/init")
    response = client.get("/api/merchants")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 10
    assert any(merchant["merchant_name"] == "FreshBasket Grocers" for merchant in body)
    assert all(merchant["registered_whatsapp_number"].startswith("whatsapp:+91") for merchant in body)
    assert all(merchant["latest_run_id"] is None for merchant in body)


def test_merchant_detail_includes_monthly_metrics(client) -> None:
    client.post("/api/seed/init")
    response = client.get("/api/merchants/m_wanderdeals")
    assert response.status_code == 200
    body = response.json()
    assert body["merchant_name"] == "WanderDeals Travel"
    assert len(body["monthly_metrics"]) == 7
    assert body["registered_whatsapp_number"].startswith("whatsapp:+91")


def test_list_merchants_includes_latest_underwriting_snapshot(client) -> None:
    client.post("/api/seed/init")
    client.post("/api/underwriting/run/m_freshbasket")

    response = client.get("/api/merchants")
    assert response.status_code == 200
    freshbasket = next(merchant for merchant in response.json() if merchant["merchant_id"] == "m_freshbasket")
    assert freshbasket["latest_decision"] == "approved"
    assert freshbasket["latest_risk_tier"] == "tier_1"
    assert freshbasket["latest_credit_limit"] is not None


def test_benchmarks_and_policy_are_available(client) -> None:
    client.post("/api/seed/init")

    benchmarks_response = client.get("/api/benchmarks")
    assert benchmarks_response.status_code == 200
    assert len(benchmarks_response.json()) == len(BENCHMARKS)

    policy_response = client.get("/api/policies/active")
    assert policy_response.status_code == 200
    assert policy_response.json()["version_name"] == "phase1_policy_v1"
