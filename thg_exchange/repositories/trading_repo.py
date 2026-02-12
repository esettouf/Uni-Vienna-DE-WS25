from __future__ import annotations
from typing import Any, Dict, List, Optional
from datetime import datetime
from .. import db
from thg_exchange.models import enums

def now_iso() -> str:
    return datetime.utcnow().isoformat()

def find_user_certificates(user_id: str) -> List[Dict[str, Any]]:
    return list(db.certificates.find({"ownerType": "user", "ownerId": user_id}).sort("createdAt", -1))

def find_user_certified_certificates(user_id: str) -> List[Dict[str, Any]]:
    return list(db.certificates.find({"ownerType": "user", "ownerId": user_id, "status": "CERTIFIED"}).sort("createdAt", -1))

def find_certificate_for_user(user_id: str, certificate_id: str) -> Optional[Dict[str, Any]]:
    return db.certificates.find_one({"certificateId": certificate_id, "ownerType": "user", "ownerId": user_id})

def reserve_certificate(certificate_id: str) -> None:
    db.certificates.update_one(
        {"certificateId": certificate_id},
        {"$set": {"status": "RESERVED", "reservedAt": now_iso()}}
    )

def set_certificate_sold_to_company(certificate_id: str, company_id: str) -> None:
    db.certificates.update_one(
        {"certificateId": certificate_id},
        {"$set": {"ownerType": "company", "ownerId": company_id, "status": "SOLD", "soldAt": now_iso()}}
    )

def set_certificate_certified(certificate_id: str) -> None:
    db.certificates.update_one(
        {"certificateId": certificate_id},
        {"$set": {"status": "CERTIFIED"}}
    )

def insert_sell_order(doc: Dict[str, Any]) -> None:
    db.sell_orders.insert_one(doc)

def find_sell_orders_by_user(user_id: str) -> List[Dict[str, Any]]:
    return list(db.sell_orders.find({"sellerType": "user", "sellerId": user_id}).sort("createdAt", -1))

def set_sell_order_status(order_id: str, status: str, extra: Dict[str, Any] | None = None) -> None:
    payload = {"status": status}
    if extra:
        payload.update(extra)
    db.sell_orders.update_one({"sellOrderId": order_id}, {"$set": payload})

def insert_trade(doc: Dict[str, Any]) -> None:
    db.trades.insert_one(doc)

def find_trades_by_ids(trade_ids: List[str]) -> List[Dict[str, Any]]:
    if not trade_ids:
        return []
    return list(db.trades.find({"tradeId": {"$in": trade_ids}}))

def find_best_matching_bid(min_price: float) -> Optional[Dict[str, Any]]:
    return db.bids.find_one(
        {"status": "OPEN", "maxPrice": {"$gte": min_price}},
        sort=[("maxPrice", -1), ("createdAt", 1)]
    )

def insert_bid(doc: Dict[str, Any]) -> None:
    db.bids.insert_one(doc)

def list_bids() -> List[Dict[str, Any]]:
    return list(db.bids.find({}).sort("createdAt", -1))

def list_open_sell_orders(now_iso: str) -> List[Dict[str, Any]]:
    return list(db.sell_orders.find({
        "status": enums.ORDER_PLACED,
        "expiresAt": {"$gt": now_iso},
    }).sort("createdAt", 1))

def find_best_matching_sell_order(max_price: float, now_iso: str) -> Optional[Dict[str, Any]]:
    # niedrigster Preis zuerst, dann ältestes Angebot
    return db.sell_orders.find_one(
        {
            "status": enums.ORDER_PLACED,
            "expiresAt": {"$gt": now_iso},
            "minPrice": {"$lte": max_price},
        },
        sort=[("minPrice", 1), ("createdAt", 1)]
    )

def insert_bid(doc: Dict[str, Any]) -> None:
    db.bids.insert_one(doc)

def find_bid_by_id(bid_id: str) -> Optional[Dict[str, Any]]:
    return db.bids.find_one({"bidId": bid_id})

def set_bid_filled(bid_id: str) -> None:
    db.bids.update_one({"bidId": bid_id}, {"$set": {"status": enums.BID_FILLED}})

def set_bid_cancelled(bid_id: str) -> None:
    db.bids.update_one({"bidId": bid_id}, {"$set": {"status": "CANCELLED"}})

def list_bids_by_company(company_id: str) -> List[Dict[str, Any]]:
    return list(db.bids.find({"companyId": company_id}).sort("createdAt", -1))

def find_certificate_by_id(certificate_id: str) -> Optional[Dict[str, Any]]:
    return db.certificates.find_one({"certificateId": certificate_id})

def credit_wallet(user_id: str, amount: float) -> None:
    db.users.update_one({"userId": user_id}, {"$inc": {"walletBalance": float(amount)}})

def find_sell_order_for_user(user_id: str, order_id: str) -> Optional[Dict[str, Any]]:
    return db.sell_orders.find_one({"sellOrderId": order_id, "sellerType": "user", "sellerId": user_id})

def update_sell_order_min_price(order_id: str, min_price: float) -> None:
    db.sell_orders.update_one(
        {"sellOrderId": order_id},
        {"$set": {"minPrice": float(min_price), "updatedAt": now_iso()}}
    )

def unreserve_certificate(certificate_id: str) -> None:
    db.certificates.update_one(
        {"certificateId": certificate_id, "status": "RESERVED"},
        {"$set": {"status": "CERTIFIED", "unreservedAt": now_iso()}}
    )

def cancel_sell_order(order_id: str) -> None:
    db.sell_orders.update_one(
        {"sellOrderId": order_id},
        {"$set": {"status": "CANCELLED", "cancelledAt": now_iso()}}
    )

def find_expired_open_sell_orders(now_iso_str: str) -> List[Dict[str, Any]]:
    return list(db.sell_orders.find(
        {"status": "PLACED", "expiresAt": {"$lt": now_iso_str}}
    ))

def find_trades_by_company(company_id: str) -> List[Dict[str, Any]]:
    return list(db.trades.find({"companyId": company_id}).sort("createdAt", -1))

def list_open_bids() -> List[Dict[str, Any]]:
    return list(db.bids.find({"status": enums.BID_OPEN}).sort("createdAt", -1))

def find_all_trades() -> List[Dict[str, Any]]:
    return list(db.trades.find({}).sort("createdAt", -1))

def list_open_bids() -> List[Dict[str, Any]]:
    return list(db.bids.find({"status": enums.BID_OPEN}).sort("createdAt", -1))

def find_trades_by_sell_order_ids(sell_order_ids: List[str]) -> List[Dict[str, Any]]:
    if not sell_order_ids:
        return []
    return list(db.trades.find({"sellOrderId": {"$in": sell_order_ids}}).sort("createdAt", -1))


