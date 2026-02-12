from __future__ import annotations
from typing import Tuple, Dict, Any, Optional
from datetime import datetime

from ..models.ids import new_id
from ..models import enums
from ..repositories import user_repo, payout_repo

def now_iso() -> str:
    return datetime.utcnow().isoformat()

def set_bank_details(user_id: str, iban: str, bic: str, holder: str) -> Tuple[bool, str]:
    iban = (iban or "").strip()
    bic = (bic or "").strip()
    holder = (holder or "").strip()

    if not iban:
        return False, "IBAN is required."
    if len(iban.replace(" ", "")) < 10:
        return False, "IBAN looks too short."
    if not holder:
        return False, "Account holder is required."

    user_repo.set_bank_details(user_id, iban, bic, holder)
    return True, "Bank details saved."

def request_payout(user_id: str) -> Tuple[bool, str, Optional[str]]:
    user = user_repo.find_by_id(user_id)
    if not user:
        return False, "User not found.", None

    if user.get("verificationStatus") != enums.VERIF_VERIFIED:
        return False, "Account must be VERIFIED to request a payout.", None

    if not user_repo.has_bank_details(user_id):
        return False, "Bank details are missing.", None

    balance = float(user.get("walletBalance") or 0.0)
    if balance <= 0:
        return False, "Wallet balance is 0.", None

    existing = payout_repo.find_latest_pending_payout(user_id)
    if existing:
        return False, "A payout is already pending.", existing.get("payoutId")

    payout_id = new_id("pay")

    payout_repo.insert_payout({
        "payoutId": payout_id,
        "userId": user_id,
        "amount": balance,
        "status": "PENDING",
        "createdAt": now_iso(),
    })

    user_repo.update_wallet_balance(user_id, 0.0)

    return True, "Payout requested.", payout_id
