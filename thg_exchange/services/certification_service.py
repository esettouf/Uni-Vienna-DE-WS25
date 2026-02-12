from __future__ import annotations
from typing import Any, Dict, Tuple, List
from datetime import datetime

from ..models.ids import new_id
from ..models import enums
from ..repositories import cert_repo
from ..repositories import user_repo
from ..repositories import idempotency_repo
from ..repositories import b2b_event_repo



def now_iso() -> str:
    return datetime.utcnow().isoformat()


def require_verified(user: Dict[str, Any]) -> bool:
    return user.get("verificationStatus") == enums.VERIF_VERIFIED


def _validate_registration_year(raw: str) -> Tuple[bool, str | int]:
    if not raw or not raw.isdigit():
        return False, "Registration year must be a number."
    year = int(raw)
    if year < 1900 or year > 2100:
        return False, "Registration year is not plausible."
    return True, year


def _validate_request_year(raw: str | None, fallback: int) -> Tuple[bool, str | int]:
    if raw:
        if not raw.isdigit():
            return False, "Request year must be a number."
        year = int(raw)
    else:
        year = fallback
    if year < 1900 or year > 2100:
        return False, "Request year is not plausible."
    return True, year


def submit_request(
    user_id: str,
    vehicle_type: str,
    vehicle_id: str | None,
    registration_year_raw: str,
    license_plate: str,
    vehicle_vin: str,
    evidence_url: str = "",
    request_year_raw: str | None = None,
) -> Tuple[bool, str, str | None]:
    user = user_repo.find_by_id(user_id)
    if not user:
        return False, "User not found.", None
    if not require_verified(user):
        return False, "Account must be verified before submitting a request.", None

    vehicle_type = (vehicle_type or "").strip()
    vehicle_id = (vehicle_id or "").strip() or new_id("veh")
    license_plate = (license_plate or "").strip()
    vehicle_vin = (vehicle_vin or "").strip().upper()
    evidence_url = (evidence_url or "").strip()

    if not vehicle_type:
        return False, "Vehicle type is required.", None
    if vehicle_type not in {"BEV", "PHEV", "OTHER"}:
        return False, "Vehicle type is invalid.", None
    if not license_plate:
        return False, "License plate is required.", None

    ok_reg, reg_year_or_msg = _validate_registration_year(registration_year_raw)
    if not ok_reg:
        return False, reg_year_or_msg, None
    registration_year = reg_year_or_msg  # type: ignore

    ok_req, req_year_or_msg = _validate_request_year(request_year_raw, registration_year)
    if not ok_req:
        return False, req_year_or_msg, None
    request_year = req_year_or_msg  # type: ignore

    if vehicle_vin and len(vehicle_vin) < 5:
        return False, "VIN must be at least 5 characters.", None
    if vehicle_vin and cert_repo.request_exists_by_vin(user_id, vehicle_vin, request_year):
        return False, "A request for this vehicle and year already exists.", None

    request_id = new_id("req")

    cert_repo.insert_request({
        "requestId": request_id,
        "userId": user_id,
        "vehicleType": vehicle_type,
        "vehicleId": vehicle_id,
        "requestYear": request_year,
        "registrationYear": registration_year,
        "licensePlate": license_plate,
        "vehicleVin": vehicle_vin,
        "evidenceUrl": evidence_url,
        "evidenceRef": evidence_url,
        "vehicle": {
            "vehicleId": vehicle_id,
            "licensePlate": license_plate,
            "vehicleType": vehicle_type,
            "registrationYear": registration_year,
            "vin": vehicle_vin,
        },
        "status": enums.REQ_SUBMITTED,
        "createdAt": now_iso(),
    })

    return True, "Certification request submitted.", request_id


def update_request(
    user_id: str,
    request_id: str,
    vehicle_type: str,
    vehicle_id: str | None,
    registration_year_raw: str,
    license_plate: str,
    vehicle_vin: str,
    evidence_url: str = "",
    request_year_raw: str | None = None,
) -> Tuple[bool, str, str | None]:
    req = cert_repo.find_request_by_id_for_user(request_id, user_id)
    if not req:
        return False, "Request not found.", None
    if req.get("status") != enums.REQ_NEEDS_MORE_INFO:
        return False, "Only requests needing more info can be updated.", None

    vehicle_type = (vehicle_type or "").strip()
    vehicle_id = (vehicle_id or "").strip() or req.get("vehicleId") or new_id("veh")
    license_plate = (license_plate or "").strip()
    vehicle_vin = (vehicle_vin or "").strip().upper()
    evidence_url = (evidence_url or "").strip()

    if not vehicle_type:
        return False, "Vehicle type is required.", None
    if vehicle_type not in {"BEV", "PHEV", "OTHER"}:
        return False, "Vehicle type is invalid.", None
    if not license_plate:
        return False, "License plate is required.", None

    ok_reg, reg_year_or_msg = _validate_registration_year(registration_year_raw)
    if not ok_reg:
        return False, reg_year_or_msg, None
    registration_year = reg_year_or_msg  # type: ignore

    ok_req, req_year_or_msg = _validate_request_year(request_year_raw, registration_year)
    if not ok_req:
        return False, req_year_or_msg, None
    request_year = req_year_or_msg  # type: ignore

    if vehicle_vin and len(vehicle_vin) < 5:
        return False, "VIN must be at least 5 characters.", None
    if vehicle_vin and vehicle_vin != req.get("vehicleVin") and cert_repo.request_exists_by_vin_excluding_request(user_id, vehicle_vin, request_year, request_id):
        return False, "A request for this VIN and year already exists.", None

    cert_repo.update_request(req.get("requestId"), {
        "vehicleType": vehicle_type,
        "vehicleId": vehicle_id,
        "registrationYear": registration_year,
        "requestYear": request_year,
        "licensePlate": license_plate,
        "vehicleVin": vehicle_vin,
        "evidenceUrl": evidence_url,
        "evidenceRef": evidence_url,
        "vehicle": {
            "vehicleId": vehicle_id,
            "licensePlate": license_plate,
            "vehicleType": vehicle_type,
            "registrationYear": registration_year,
            "vin": vehicle_vin,
        },
        "status": enums.REQ_SUBMITTED,
        "updatedAt": now_iso(),
    })

    return True, "Request updated and resubmitted.", request_id


def list_requests(user_id: str) -> List[Dict[str, Any]]:
    return cert_repo.find_requests_by_user(user_id)


def get_request_detail(user_id: str, request_id: str) -> Dict[str, Any] | None:
    return cert_repo.find_request_by_id_for_user(request_id, user_id)


def admin_list_requests() -> List[Dict[str, Any]]:
    return cert_repo.find_all_requests()


def admin_decide_request(request_id: str, decision: str) -> Tuple[bool, str, str]:
    cert_id = ""

    if decision not in (enums.REQ_CONFIRMED, enums.REQ_REJECTED, enums.REQ_NEEDS_MORE_INFO, enums.REQ_ERROR):
        return False, cert_id, "Invalid decision."

    req = cert_repo.find_request_by_id(request_id)
    if not req:
        return False, cert_id, "Request not found."

    cert_repo.set_request_status(request_id, decision)    

    if decision == enums.REQ_CONFIRMED:
        cert_id = new_id("cert")
        cert_repo.insert_certificate({
            "certificateId": cert_id,
            "ownerType": "user",
            "ownerId": req["userId"],
            "vehicleId": req["vehicleId"],
            "requestYear": req["requestYear"],
            "status": enums.CERT_CERTIFIED,
            "amountCO2": 1.0,
            "blockchainHash": new_id("bch"),
            "createdAt": now_iso(),
        })

    return True, cert_id, "Decision saved."


def list_certificates(user_id: str) -> List[Dict[str, Any]]:
    return cert_repo.find_certificates_by_user(user_id)


def submit_b2b_batch(
    user_id: str,
    message_id: str,
    source_system: str,
    request_year: int,
    vehicles: List[Dict[str, Any]],
) -> Dict[str, Any]:
    existing = idempotency_repo.find_response(message_id)
    if existing:
        return existing.get("response") or {
            "ok": False,
            "message": "Idempotency record invalid",
            "batchId": None,
            "items": [],
        }

    user = user_repo.find_by_id(user_id)
    if not user:
        resp = {"ok": False, "message": "User not found", "batchId": None, "items": []}
        idempotency_repo.store_response(message_id, "UC3_BATCH_SUBMIT", resp)
        return resp

    if not require_verified(user):
        resp = {"ok": False, "message": "Account must be verified", "batchId": None, "items": []}
        idempotency_repo.store_response(message_id, "UC3_BATCH_SUBMIT", resp)
        return resp

    batch_id = new_id("batch")
    results: List[Dict[str, Any]] = []

    for v in vehicles:
        vehicle_type = (v.get("vehicleType") or "").strip()
        registration_year_raw = str(v.get("registrationYear") or "")
        license_plate = (v.get("licensePlate") or "").strip()
        vin = (v.get("vin") or "").strip().upper()
        evidence_ref = (v.get("evidenceRef") or "").strip()

        ok, msg, request_id = submit_request(
            user_id=user_id,
            vehicle_type=vehicle_type,
            vehicle_id=None,
            registration_year_raw=registration_year_raw,
            license_plate=license_plate,
            vehicle_vin=vin,
            evidence_url=evidence_ref,
            request_year_raw=str(request_year),
        )

        results.append({
            "vehicleVin": vin,
            "licensePlate": license_plate,
            "ok": ok,
            "message": msg,
            "requestId": request_id,
        })

    resp = {
        "ok": True,
        "message": "Batch processed",
        "batchId": batch_id,
        "items": results,
    }

    idempotency_repo.store_response(message_id, "UC3_BATCH_SUBMIT", resp)
    return resp


def admin_decide_request_and_emit_b2b_event(request_id: str, decision: str) -> Dict[bool, str, str | None]:
    """
    Entscheidet einen Request und schreibt danach ein B2B Decision Event in Mongo (Outbox).
    Returns: (ok, message, event_id)
    """
    # TODO Check ob cert_id rihctig returned
    ok, cert_id, msg = admin_decide_request(request_id, decision)
    if not ok:
        return False, msg, None

    req = cert_repo.find_request_by_id(request_id)
    if not req:
        return False, "Request not found after decision.", None

    # Optional: certificateId bei CONFIRMED finden
    certificate_id = None
    if decision == enums.REQ_CONFIRMED:
        cert = cert_repo.find_certificate_by_owner_vehicle_year(
            owner_type="user",
            owner_id=req.get("userId"),
            vehicle_id=req.get("vehicleId"),
            request_year=req.get("requestYear"),
        )
        if cert:
            certificate_id = cert.get("certificateId")

    event_id = new_id("evt")

    event_doc = {
        "eventId": event_id,
        "eventType": "CERT_DECISION_EVENT",
        "correlationId": request_id,
        "payload": {
            "requestId": request_id,
            "decision": decision,
            "certificateId": certificate_id,
            "userId": req.get("userId"),
        },
        "status": "PENDING",
        "createdAt": now_iso(),
    }

    b2b_event_repo.insert_cert_decision_event(event_doc)
    return True, "Decision saved and event emitted.", event_id


def list_pending_b2b_cert_decision_events() -> List[Dict[str, Any]]:
    return b2b_event_repo.list_pending_cert_decision_events()


def ack_b2b_cert_decision_event(event_id: str) -> Tuple[bool, str]:
    ev = b2b_event_repo.find_event_by_id(event_id)
    if not ev:
        return False, "Event not found."
    if ev.get("status") == "ACKED":
        return True, "Already acknowledged."
    b2b_event_repo.mark_event_acked(event_id)
    return True, "Acknowledged."

