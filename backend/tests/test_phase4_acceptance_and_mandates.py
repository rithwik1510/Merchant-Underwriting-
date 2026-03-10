def _create_run(client, merchant_id: str = "m_freshbasket") -> int:
    client.post("/api/seed/init")
    response = client.post(f"/api/underwriting/run/{merchant_id}")
    return response.json()["run_id"]


def test_approved_run_can_be_accepted_and_complete_mandate_flow(client) -> None:
    run_id = _create_run(client, "m_freshbasket")

    accept_response = client.post(
        f"/api/offers/{run_id}/accept",
        json={
            "accepted_product_type": "combined",
            "accepted_by_name": "Amit Sharma",
            "accepted_phone": "919999999999",
            "accepted_via": "api",
            "acceptance_notes": "Proceeding after review",
        },
    )
    assert accept_response.status_code == 200
    assert accept_response.json()["mandate_can_start"] is True

    start_response = client.post(
        f"/api/mandates/{run_id}/start",
        json={"account_holder_name": "Amit Sharma", "mobile_number": "919999999999"},
    )
    assert start_response.status_code == 200
    assert start_response.json()["mandate_status"] == "initiated"

    bank_response = client.post(
        f"/api/mandates/{run_id}/select-bank",
        json={"bank_name": "HDFC Bank", "account_number": "12345678901234", "ifsc_code": "HDFC0001234"},
    )
    assert bank_response.status_code == 200
    assert bank_response.json()["mandate_status"] == "bank_selected"
    assert bank_response.json()["account_number_masked"].endswith("1234")

    otp_response = client.post(f"/api/mandates/{run_id}/send-otp")
    assert otp_response.status_code == 200
    body = otp_response.json()
    assert body["mandate_status"] == "otp_sent"
    assert body["demo_otp"] is not None

    verify_response = client.post(f"/api/mandates/{run_id}/verify-otp", json={"otp": body["demo_otp"]})
    assert verify_response.status_code == 200
    assert verify_response.json()["mandate_status"] == "otp_verified"

    complete_response = client.post(f"/api/mandates/{run_id}/complete")
    assert complete_response.status_code == 200
    complete_body = complete_response.json()
    assert complete_body["mandate_status"] == "completed"
    assert complete_body["umrn"].startswith("UMRN")
    assert complete_body["mandate_reference"].startswith("MNDT-")


def test_rejected_run_cannot_be_accepted(client) -> None:
    run_id = _create_run(client, "m_quickbyte")
    response = client.post(
        f"/api/offers/{run_id}/accept",
        json={
            "accepted_product_type": "credit",
            "accepted_by_name": "Neha",
            "accepted_phone": "919888888888",
            "accepted_via": "api",
        },
    )
    assert response.status_code == 400


def test_mandate_requires_acceptance_and_fails_after_three_wrong_otps(client) -> None:
    run_id = _create_run(client, "m_glowup")
    start_before_acceptance = client.post(
        f"/api/mandates/{run_id}/start",
        json={"account_holder_name": "Riya", "mobile_number": "919777777777"},
    )
    assert start_before_acceptance.status_code == 400

    client.post(
        f"/api/offers/{run_id}/accept",
        json={
            "accepted_product_type": "insurance",
            "accepted_by_name": "Riya",
            "accepted_phone": "919777777777",
            "accepted_via": "api",
        },
    )
    client.post(
        f"/api/mandates/{run_id}/start",
        json={"account_holder_name": "Riya", "mobile_number": "919777777777"},
    )
    client.post(
        f"/api/mandates/{run_id}/select-bank",
        json={"bank_name": "ICICI Bank", "account_number": "56789012345678", "ifsc_code": "ICIC0005678"},
    )
    client.post(f"/api/mandates/{run_id}/send-otp")

    for _ in range(3):
        response = client.post(f"/api/mandates/{run_id}/verify-otp", json={"otp": "000000"})
    assert response.status_code == 200
    assert response.json()["mandate_status"] == "failed"
    assert response.json()["failure_reason"] == "Maximum OTP attempts exceeded"


def test_acceptance_is_idempotent_and_mandate_can_be_fetched(client) -> None:
    run_id = _create_run(client, "m_homenest")
    first = client.post(
        f"/api/offers/{run_id}/accept",
        json={
            "accepted_product_type": "credit",
            "accepted_by_name": "Karan",
            "accepted_phone": "919666666666",
            "accepted_via": "dashboard",
        },
    )
    second = client.post(
        f"/api/offers/{run_id}/accept",
        json={
            "accepted_product_type": "credit",
            "accepted_by_name": "Karan",
            "accepted_phone": "919666666666",
            "accepted_via": "dashboard",
        },
    )
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]

    client.post(
        f"/api/mandates/{run_id}/start",
        json={"account_holder_name": "Karan", "mobile_number": "919666666666"},
    )
    mandate = client.get(f"/api/mandates/{run_id}")
    assert mandate.status_code == 200
    assert mandate.json()["mandate_status"] == "initiated"


def test_demo_phase4_can_be_reset_after_completion(client) -> None:
    run_id = _create_run(client, "m_freshbasket")
    client.post(
        f"/api/offers/{run_id}/accept",
        json={
            "accepted_product_type": "combined",
            "accepted_by_name": "Amit Sharma",
            "accepted_phone": "919999999999",
            "accepted_via": "dashboard",
        },
    )
    client.post(
        f"/api/mandates/{run_id}/start",
        json={"account_holder_name": "Amit Sharma", "mobile_number": "919999999999"},
    )
    client.post(
        f"/api/mandates/{run_id}/select-bank",
        json={"bank_name": "HDFC Bank", "account_number": "12345678901234", "ifsc_code": "HDFC0001234"},
    )
    otp_response = client.post(f"/api/mandates/{run_id}/send-otp")
    demo_otp = otp_response.json()["demo_otp"]
    client.post(f"/api/mandates/{run_id}/verify-otp", json={"otp": demo_otp})
    client.post(f"/api/mandates/{run_id}/complete")

    reset = client.post(f"/api/offers/{run_id}/reset-demo")
    assert reset.status_code == 200
    assert reset.json() == {"run_id": run_id, "reset": True}

    acceptance = client.get(f"/api/offers/{run_id}/acceptance")
    mandate = client.get(f"/api/mandates/{run_id}")
    assert acceptance.status_code == 404
    assert mandate.status_code == 404
