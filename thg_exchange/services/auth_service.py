from __future__ import annotations

import re

from typing import Any, Dict, Tuple
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from ..models.ids import new_id
from ..models.validators import is_email
from ..models import enums
from ..repositories import user_repo

def now_iso() -> str:
    return datetime.utcnow().isoformat()

ALLOWED_SIGNUP_ROLES = {enums.USER_ROLE_CUSTOMER, enums.USER_ROLE_BUSINESS}


def register_user(email: str, password: str, password_repeat: str, first_name: str, last_name: str, role: str | None = None):
    email_norm = (email or "").strip().lower()

    if not is_email(email_norm):
        return False, "Invalid email address.", {}

    first = (first_name or "").strip()
    last = (last_name or "").strip()
    if not first or not last:
        return False, "First name and last name are required.", {}

    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters.", {}

    if password != (password_repeat or ""):
        return False, "Passwords do not match.", {}

    # stronger rules like UI
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain an uppercase letter.", {}
    if not re.search(r"[a-z]", password):
        return False, "Password must contain a lowercase letter.", {}
    if not re.search(r"[0-9]", password):
        return False, "Password must contain a number.", {}
    if not re.search(r"[^A-Za-z0-9]", password):
        return False, "Password must contain a special character.", {}

    if user_repo.find_by_email(email_norm):
        return False, "Email already registered. Please log in.", {}

    role_norm = (role or enums.USER_ROLE_CUSTOMER).strip().lower()
    if role_norm not in ALLOWED_SIGNUP_ROLES:
        role_norm = enums.USER_ROLE_CUSTOMER

    user_id = new_id("usr")
    token = new_id("verify")

    doc = {
        "userId": user_id,
        "email": email_norm,
        "passwordHash": generate_password_hash(password),
        "fullName": f"{first} {last}",
        "firstName": first,
        "lastName": last,
        "role": role_norm,
        "verificationStatus": enums.VERIF_EMAIL_PENDING,
        "emailVerifyToken": token,
        "createdAt": now_iso(),
    }

    user_repo.insert_user(doc)
    return True, "Registered. Please verify your email.", {"verifyToken": token, "userId": user_id}


def register_business(email: str, password: str, password_repeat: str, name: str, vat_number: str, address: str):
    email_norm = (email or "").strip().lower()

    if not is_email(email_norm):
        return False, "Invalid email address.", {}

    company_name = (name or "").strip()
    if not company_name:
        return False, "Company name is required.", {}

    if not vat_number or not str(vat_number).strip():
        return False, "VAT number is required.", {}

    if not address or not str(address).strip():
        return False, "Address is required.", {}

    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters.", {}

    if password != (password_repeat or ""):
        return False, "Passwords do not match.", {}

    # reuse same password strength rules
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain an uppercase letter.", {}
    if not re.search(r"[a-z]", password):
        return False, "Password must contain a lowercase letter.", {}
    if not re.search(r"[0-9]", password):
        return False, "Password must contain a number.", {}
    if not re.search(r"[^A-Za-z0-9]", password):
        return False, "Password must contain a special character.", {}

    if user_repo.find_by_email(email_norm):
        return False, "Email already registered. Please log in.", {}

    user_id = new_id("usr")
    token = new_id("verify")

    doc = {
        "userId": user_id,
        "email": email_norm,
        "passwordHash": generate_password_hash(password),
        "name": company_name,
        "vatNumber": str(vat_number).strip(),
        "address": str(address).strip(),
        "role": enums.USER_ROLE_BUSINESS,
        "verificationStatus": enums.VERIF_EMAIL_PENDING,
        "emailVerifyToken": token,
        "createdAt": now_iso(),
    }

    user_repo.insert_user(doc)
    return True, "Registered. Please verify your email.", {"verifyToken": token, "userId": user_id}


def verify_email_token(token: str) -> Tuple[bool, str]:
    user = user_repo.find_by_email_token(token)
    if not user:
        return False, "Invalid verification token."
    user_repo.verify_email(user["userId"])
    return True, "Email verified. Please submit your identity documents."

def authenticate(email: str, password: str) -> Tuple[bool, str, Dict[str, Any]]:
    email_norm = (email or "").strip().lower()
    user = user_repo.find_by_email(email_norm)
    if not user:
        return False, "Invalid credentials.", {}

    if not check_password_hash(user.get("passwordHash", ""), password or ""):
        return False, "Invalid credentials.", {}

    return True, "Login successful.", {"userId": user["userId"], "role": user.get("role", enums.USER_ROLE_CUSTOMER)}

def submit_identity(user_id: str, doc_type: str, doc_ref: str) -> Tuple[bool, str]:
    if not doc_type or not doc_ref:
        return False, "Please provide document type and reference."

    kyc_doc = {
        "docType": doc_type.strip(),
        "docRef": doc_ref.strip(),
        "submittedAt": now_iso(),
    }
    user_repo.set_kyc_submitted(user_id, kyc_doc)
    return True, "KYC submitted. Waiting for decision."
