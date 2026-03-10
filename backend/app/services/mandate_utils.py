from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timezone


def mask_account_number(account_number: str) -> str:
    visible = account_number[-4:]
    masked = "*" * max(0, len(account_number) - 4)
    return f"{masked}{visible}"


def mask_ifsc(ifsc_code: str) -> str:
    if len(ifsc_code) <= 6:
        return ifsc_code[0:2] + "*" * max(0, len(ifsc_code) - 4) + ifsc_code[-2:]
    middle = "*" * (len(ifsc_code) - 6)
    return f"{ifsc_code[:4]}{middle}{ifsc_code[-2:]}"


def mask_mobile(mobile_number: str) -> str:
    digits = mobile_number[-2:]
    return "*" * max(0, len(mobile_number) - 2) + digits


def generate_demo_otp() -> str:
    return f"{secrets.randbelow(900000) + 100000}"


def hash_otp(otp: str) -> str:
    return hashlib.sha256(otp.encode()).hexdigest()


def verify_otp(otp: str, hashed_otp: str | None) -> bool:
    if not hashed_otp:
        return False
    return hash_otp(otp) == hashed_otp


def generate_umrn(run_id: int) -> str:
    stamp = datetime.now(timezone.utc).strftime("%d%m%y")
    suffix = f"{secrets.randbelow(900000) + 100000}"
    return f"UMRN{stamp}{run_id:03d}{suffix}"


def generate_mandate_reference(run_id: int, acceptance_id: int) -> str:
    stamp = datetime.now(timezone.utc).strftime("%H%M%S")
    return f"MNDT-{run_id}-{acceptance_id}-{stamp}"
