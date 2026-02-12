from __future__ import annotations
from typing import Any, Dict, Optional
from datetime import datetime
from .. import db

def now_iso() -> str:
    return datetime.utcnow().isoformat()

def find_response(message_id: str) -> Optional[Dict[str, Any]]:
    return db.b2b_idempotency.find_one({"messageId": message_id})

def store_response(message_id: str, operation: str, response: Dict[str, Any]) -> None:
    db.b2b_idempotency.insert_one({
        "messageId": message_id,
        "operation": operation,
        "response": response,
        "createdAt": now_iso(),
    })
