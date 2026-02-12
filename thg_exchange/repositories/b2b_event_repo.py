from __future__ import annotations
from typing import Any, Dict, List, Optional
from datetime import datetime
from .. import db

def now_iso() -> str:
    return datetime.utcnow().isoformat()

def insert_cert_decision_event(doc: Dict[str, Any]) -> None:
    db.b2b_cert_events.insert_one(doc)

def list_pending_cert_decision_events() -> List[Dict[str, Any]]:
    return list(db.b2b_cert_events.find({"status": "PENDING"}).sort("createdAt", 1))

def find_event_by_id(event_id: str) -> Optional[Dict[str, Any]]:
    return db.b2b_cert_events.find_one({"eventId": event_id})

def mark_event_acked(event_id: str) -> None:
    db.b2b_cert_events.update_one(
        {"eventId": event_id},
        {"$set": {"status": "ACKED", "ackedAt": now_iso()}}
    )
