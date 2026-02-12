from __future__ import annotations
from typing import Any, Dict, Tuple, List
from datetime import datetime

from ..models.ids import new_id
from ..models import enums
from ..repositories import trading_repo

def now_iso() -> str:
    return datetime.utcnow().isoformat()

def list_my_certificates(user_id: str) -> List[Dict[str, Any]]:
    return trading_repo.find_user_certificates(user_id)

def list_sellable_certificates(user_id: str) -> List[Dict[str, Any]]:
    return trading_repo.find_user_certified_certificates(user_id)

def create_sell_order(user_id: str, certificate_id: str, min_price_raw: str, valid_until_raw: str = "") -> Tuple[bool, str]:
    cert = trading_repo.find_certificate_for_user(user_id, certificate_id)
    if not cert:
        return False, "Certificate not found."

    if cert.get("status") != enums.CERT_CERTIFIED and cert.get("status") != "CERTIFIED":
        return False, "Certificate is not available for selling."

    try:
        min_price = float(min_price_raw) if min_price_raw else 0.0
    except Exception:
        min_price = 0.0

    if min_price < 0:
        return False, "Minimum price must be 0 or greater."

    valid_until_raw = (valid_until_raw or "").strip()
    if not valid_until_raw:
        return False, "Valid until date is required."

    # valid_until expected as YYYY-MM-DD, store end of day UTC
    try:
        expires_at = datetime.strptime(valid_until_raw, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    except Exception:
        return False, "Valid until must be a date in format YYYY-MM-DD."

    if expires_at <= datetime.utcnow():
        return False, "Valid until must be in the future."

    trading_repo.reserve_certificate(certificate_id)

    order_id = new_id("sell")
    trading_repo.insert_sell_order({
        "sellOrderId": order_id,
        "sellerType": "user",
        "sellerId": user_id,
        "certificateId": certificate_id,
        "minPrice": float(min_price),
        "status": enums.ORDER_PLACED,
        "expiresAt": expires_at.isoformat(),
        "createdAt": now_iso(),
    })

    matched, match_msg = try_match_order(user_id, order_id, certificate_id, min_price)
    if matched:
        return True, match_msg

    return True, "Sell order placed. No matching bid found."


def update_sell_order(user_id: str, order_id: str, min_price_raw: str, valid_until_raw: str) -> Tuple[bool, str]:
    order = trading_repo.find_sell_order_for_user(user_id, order_id)
    if not order:
        return False, "Sell order not found."

    if order.get("status") != enums.ORDER_PLACED:
        return False, "Only open sell orders can be updated."

    # block editing if already expired
    if order.get("expiresAt") and order["expiresAt"] < now_iso():
        trading_repo.cancel_sell_order(order_id)
        trading_repo.unreserve_certificate(order["certificateId"])
        return False, "Sell order expired and was cancelled."

    try:
        min_price = float(min_price_raw) if min_price_raw else 0.0
    except Exception:
        min_price = 0.0

    if min_price < 0:
        return False, "Minimum price must be 0 or greater."

    valid_until_raw = (valid_until_raw or "").strip()
    if not valid_until_raw:
        return False, "Valid until date is required."

    try:
        expires_at = datetime.strptime(valid_until_raw, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    except Exception:
        return False, "Valid until must be a date in format YYYY-MM-DD."

    if expires_at <= datetime.utcnow():
        return False, "Valid until must be in the future."

    trading_repo.update_sell_order_min_price(order_id, float(min_price))
    trading_repo.set_sell_order_status(order_id, enums.ORDER_PLACED, {"expiresAt": expires_at.isoformat()})

    matched, match_msg = try_match_order(
        user_id=user_id,
        sell_order_id=order_id,
        certificate_id=order["certificateId"],
        min_price=float(min_price),
    )
    if matched:
        return True, match_msg

    return True, "Sell order updated. No matching bid found."


def cancel_sell_order(user_id: str, order_id: str) -> Tuple[bool, str]:
    order = trading_repo.find_sell_order_for_user(user_id, order_id)
    if not order:
        return False, "Sell order not found."

    if order.get("status") != enums.ORDER_PLACED:
        return False, "Only open sell orders can be cancelled."

    trading_repo.cancel_sell_order(order_id)
    trading_repo.unreserve_certificate(order["certificateId"])

    return True, "Sell order cancelled. Certificate is available again."


def try_match_order(user_id: str, sell_order_id: str, certificate_id: str, min_price: float) -> Tuple[bool, str]:
    bid = trading_repo.find_best_matching_bid(min_price)
    if not bid:
        return False, "No match."

    price = float(bid["maxPrice"])
    fee = round(price * 0.02, 2)
    net = round(price - fee, 2)

    trade_id = new_id("trd")
    trading_repo.insert_trade({
        "tradeId": trade_id,
        "certificateId": certificate_id,
        "sellOrderId": sell_order_id,
        "bidId": bid["bidId"],
        "companyId": bid["companyId"],
        "price": price,
        "fee": fee,
        "net": net,
        "status": enums.TRADE_CREATED,
        "blockchainHash": new_id("bch"),
        "createdAt": now_iso(),
    })

    trading_repo.set_certificate_sold_to_company(certificate_id, bid["companyId"])
    trading_repo.set_sell_order_status(sell_order_id, enums.ORDER_MATCHED, {"tradeId": trade_id, "matchedAt": now_iso()})
    trading_repo.set_bid_filled(bid["bidId"])
    trading_repo.credit_wallet(user_id, net)

    return True, "Sell order matched. Wallet credited."

def expire_open_orders_for_user(user_id: str) -> int:
    now = now_iso()
    expired = trading_repo.find_expired_open_sell_orders(now)

    count = 0
    for o in expired:
        # only touch orders of this user
        if o.get("sellerType") == "user" and o.get("sellerId") == user_id:
            trading_repo.cancel_sell_order(o["sellOrderId"])
            trading_repo.unreserve_certificate(o["certificateId"])
            count += 1
    return count


def list_my_orders_with_trades(user_id: str) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    orders = trading_repo.find_sell_orders_by_user(user_id)
    trade_ids = [o.get("tradeId") for o in orders if o.get("tradeId")]
    trades = {t["tradeId"]: t for t in trading_repo.find_trades_by_ids(trade_ids)}
    return orders, trades

def admin_create_bid(company_id: str, max_price_raw: str) -> Tuple[bool, str]:
    company_id = (company_id or "").strip() or "company_demo"
    try:
        max_price = float(max_price_raw) if max_price_raw else 100.0
    except Exception:
        max_price = 100.0

    if max_price <= 0:
        return False, "Max price must be greater than 0."

    bid_id = new_id("bid")
    trading_repo.insert_bid({
        "bidId": bid_id,
        "companyId": company_id,
        "maxPrice": float(max_price),
        "status": enums.BID_OPEN,
        "createdAt": now_iso(),
    })
    return True, "Bid created."

def admin_list_bids() -> List[Dict[str, Any]]:
    return trading_repo.list_bids()

def list_open_sell_orders_for_market() -> List[Dict[str, Any]]:
    now = now_iso()
    return trading_repo.list_open_sell_orders(now)

def create_bid_for_business(company_id: str, max_price_raw: str) -> Tuple[bool, str, str | None, str | None]:
    """
    Business erstellt ein Kaufgebot (Bid).
    Return: ok, message, bid_id, trade_id
    """
    company_id = (company_id or "").strip()
    try:
        max_price = float(max_price_raw) if max_price_raw else 100.0
    except Exception:
        max_price = 100.0

    if max_price <= 0:
        return False, "Max price must be greater than 0.", None, None

    bid_id = new_id("bid")
    trading_repo.insert_bid({
        "bidId": bid_id,
        "companyId": company_id,
        "maxPrice": float(max_price),
        "status": enums.BID_OPEN,
        "createdAt": now_iso(),
    })

    matched, msg, trade_id = try_match_bid(bid_id, company_id, max_price)
    if matched:
        return True, msg, bid_id, trade_id

    return True, "Bid created. No matching sell order found.", bid_id, None

def try_match_bid(bid_id: str, company_id: str, max_price: float) -> Tuple[bool, str, str | None]:
    now = now_iso()

    # finde die beste passende Sell Order
    sell_order = trading_repo.find_best_matching_sell_order(max_price, now)
    if not sell_order:
        return False, "No match.", None

    sell_order_id = sell_order["sellOrderId"]
    certificate_id = sell_order["certificateId"]

    # certificate holen um sellerId zu ermitteln
    cert = trading_repo.find_certificate_by_id(certificate_id)
    if not cert:
        return False, "Certificate not found for sell order.", None

    seller_id = sell_order.get("sellerId")
    if not seller_id:
        return False, "Sell order has no seller.", None

    price = float(sell_order.get("minPrice") or 0.0)
    if price <= 0:
        # falls minPrice 0, nimm bid max price als trade price oder 0
        price = float(max_price)

    fee = round(price * 0.02, 2)
    net = round(price - fee, 2)

    trade_id = new_id("trd")
    trading_repo.insert_trade({
        "tradeId": trade_id,
        "certificateId": certificate_id,
        "sellOrderId": sell_order_id,
        "bidId": bid_id,
        "companyId": company_id,
        "price": price,
        "fee": fee,
        "net": net,
        "status": enums.TRADE_CREATED,
        "blockchainHash": new_id("bch"),
        "createdAt": now_iso(),
    })

    trading_repo.set_certificate_sold_to_company(certificate_id, company_id)
    trading_repo.set_sell_order_status(sell_order_id, enums.ORDER_MATCHED, {"tradeId": trade_id, "matchedAt": now_iso()})
    trading_repo.set_bid_filled(bid_id)
    trading_repo.credit_wallet(seller_id, net)

    return True, "Bid matched with sell order. Seller wallet credited.", trade_id

def cancel_bid_for_business(company_id: str, bid_id: str) -> Tuple[bool, str]:
    bid = trading_repo.find_bid_by_id(bid_id)
    if not bid:
        return False, "Bid not found."
    if bid.get("companyId") != company_id:
        return False, "Forbidden."
    if bid.get("status") != enums.BID_OPEN:
        return False, "Only open bids can be cancelled."

    trading_repo.set_bid_cancelled(bid_id)
    return True, "Bid cancelled."
