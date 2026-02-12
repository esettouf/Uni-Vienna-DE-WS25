from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime

from .. import db

def now_iso() -> str:
    return datetime.utcnow().isoformat()

def find_all_users() -> List[Dict[str, Any]]:
    return list(db.users.find({}).sort("createdAt", -1))

def find_by_email(email: str) -> Optional[Dict[str, Any]]:
    return db.users.find_one({"email": email})

def find_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    return db.users.find_one({"userId": user_id})

def find_by_email_token(token: str) -> Optional[Dict[str, Any]]:
    return db.users.find_one({"emailVerifyToken": token})

def insert_user(doc: Dict[str, Any]) -> None:
    db.users.insert_one(doc)

def set_verification_status(user_id: str, status: str) -> None:
    db.users.update_one({"userId": user_id}, {"$set": {"verificationStatus": status, "kyc": {"status": status}}})


def verify_email(user_id: str) -> None:
    db.users.update_one(
        {"userId": user_id},
        {"$set": {"verificationStatus": "IDENTITY_PENDING", "emailVerifiedAt": now_iso(), "kyc": {"status": "IDENTITY_PENDING"}},
         "$unset": {"emailVerifyToken": ""}}
    )

def set_kyc_submitted(user_id: str, kyc_doc: Dict[str, Any]) -> None:
    db.users.update_one(
        {"userId": user_id},
        {"$set": {"verificationStatus": "KYC_SUBMITTED", "kyc": kyc_doc}}
    )

def find_all_customers():
    return list(db.users.find({"role": "customer"}))


def admin_mark_email_verified(user_id: str) -> None:
    db.users.update_one(
        {"userId": user_id},
        {"$set": {"verificationStatus": "IDENTITY_PENDING"}}
    )

def update_user_admin(user_id: str, updates: Dict[str, Any]) -> None:
    db.users.update_one({"userId": user_id}, {"$set": updates})

def delete_user(user_id: str) -> None:
    db.users.delete_one({"userId": user_id})

def set_bank_details(user_id: str, iban: str, bic: str, holder: str) -> None:
    db.users.update_one(
        {"userId": user_id},
        {"$set": {
            "bank": {
                "iban": iban,
                "bic": bic,
                "holder": holder,
                "updatedAt": now_iso(),
            }
        }}
    )
    
def get_bank_details(user_id: str) -> Optional[Dict[str, Any]]:
    u = db.users.find_one({"userId": user_id}, {"bank": 1})
    if not u:
        return None
    return u.get("bank")

def has_bank_details(user_id: str) -> bool:
    bank = get_bank_details(user_id) or {}
    iban = (bank.get("iban") or "").strip()
    holder = (bank.get("holder") or "").strip()
    return bool(iban and holder)

def mask_iban(iban: str) -> str:
    iban = (iban or "").replace(" ", "").strip()
    if len(iban) < 8:
        return "—"
    return f"{iban[:4]}••••••••••{iban[-4:]}"

def update_wallet_balance(user_id: str, new_balance: float) -> None:
    db.users.update_one(
        {"userId": user_id},
        {"$set": {"walletBalance": float(new_balance)}}
    )

def increment_wallet_balance(user_id: str, delta: float) -> None:
    db.users.update_one(
        {"userId": user_id},
        {"$inc": {"walletBalance": float(delta)}}
    )
