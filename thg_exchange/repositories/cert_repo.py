from __future__ import annotations
from typing import Any, Dict, Optional, List
from datetime import datetime
from .. import db

def now_iso() -> str:
    return datetime.utcnow().isoformat()

def request_exists(user_id: str, vehicle_id: str, request_year: int) -> bool:
    return db.cert_requests.find_one(
        {"userId": user_id, "vehicleId": vehicle_id, "requestYear": request_year}
    ) is not None


def vin_exists(vehicle_vin: str) -> bool:
    return db.cert_requests.find_one({
        "$or": [
            {"vehicleVin": vehicle_vin},
            {"vehicle.vin": vehicle_vin},
        ]
    }) is not None

def insert_request(doc: Dict[str, Any]) -> None:
    db.cert_requests.insert_one(doc)


def update_request(request_id: str, updates: Dict[str, Any]) -> None:
    db.cert_requests.update_one({"requestId": request_id}, {"$set": updates})

def find_requests_by_user(user_id: str) -> List[Dict[str, Any]]:
    return list(db.cert_requests.find({"userId": user_id}).sort("createdAt", -1))

def find_request_by_id_for_user(request_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    return db.cert_requests.find_one({"requestId": request_id, "userId": user_id})

def find_request_by_id(request_id: str) -> Optional[Dict[str, Any]]:
    return db.cert_requests.find_one({"requestId": request_id})

def find_all_requests() -> List[Dict[str, Any]]:
    return list(db.cert_requests.find({}).sort("createdAt", -1))

def set_request_status(request_id: str, status: str) -> None:
    db.cert_requests.update_one(
        {"requestId": request_id},
        {"$set": {"status": status, "decidedAt": now_iso()}}
    )

def insert_certificate(doc: Dict[str, Any]) -> None:
    db.certificates.insert_one(doc)

def find_certificates_by_user(user_id: str) -> List[Dict[str, Any]]:
    return list(db.certificates.find({"ownerType": "user", "ownerId": user_id}).sort("createdAt", -1))

def request_exists_by_vin(user_id: str, vin: str, request_year: int) -> bool:
    return db.cert_requests.find_one(
        {
            "userId": user_id,
            "requestYear": request_year,
            "$or": [
                {"vehicleVin": vin},
                {"vehicle.vin": vin},
            ],
        }
    ) is not None

def request_exists_by_vin_excluding_request(user_id: str, vin: str, request_year: int, request_id: str) -> bool:
    return db.cert_requests.find_one(
        {
            "userId": user_id,
            "requestYear": request_year,
            "requestId": {"$ne": request_id},
            "$or": [
                {"vehicleVin": vin},
                {"vehicle.vin": vin},
            ],
        }
    ) is not None


def update_request_fields(
    request_id: str,
    user_id: str,
    request_year: int,
    evidence_ref: str,
    license_plate: str,
    vehicle_type: str,
    registration_year: int,
    vin: str,
    status: str,
) -> None:
    db.cert_requests.update_one(
        {"requestId": request_id, "userId": user_id},
        {"$set": {
            "requestYear": request_year,
            "evidenceRef": evidence_ref,
            "evidenceUrl": evidence_ref,
            "licensePlate": license_plate,
            "vehicleType": vehicle_type,
            "registrationYear": registration_year,
            "vehicleVin": vin,
            "vehicle.licensePlate": license_plate,
            "vehicle.vehicleType": vehicle_type,
            "vehicle.registrationYear": registration_year,
            "vehicle.vin": vin,
            "status": status,
            "updatedAt": now_iso(),
        }}
    )

def find_certificate_by_owner_vehicle_year(owner_type: str, owner_id: str, vehicle_id: str, request_year: int) -> Optional[Dict[str, Any]]:
    return db.certificates.find_one({
        "ownerType": owner_type,
        "ownerId": owner_id,
        "vehicleId": vehicle_id,
        "requestYear": request_year,
    })

