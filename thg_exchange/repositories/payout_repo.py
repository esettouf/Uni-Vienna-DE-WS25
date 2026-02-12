from __future__ import annotations
from typing import Any, Dict, List, Optional
from datetime import datetime
from .. import db

def now_iso() -> str:
    return datetime.utcnow().isoformat()

def insert_payout(doc: Dict[str, Any]) -> None:
    db.payouts.insert_one(doc)

def find_payouts_by_user(user_id: str) -> List[Dict[str, Any]]:
    return list(db.payouts.find({"userId": user_id}).sort("createdAt", -1))

def find_latest_pending_payout(user_id: str) -> Optional[Dict[str, Any]]:
    return db.payouts.find_one(
        {"userId": user_id, "status": "PENDING"},
        sort=[("createdAt", -1)]
    )
