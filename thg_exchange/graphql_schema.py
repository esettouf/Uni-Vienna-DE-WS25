import graphene
import json

from thg_exchange.models import enums
from thg_exchange.repositories import user_repo, cert_repo, trading_repo
from thg_exchange.services import auth_service, certification_service, trading_service, payout_service
from thg_exchange.auth_utils import create_access_token

class User(graphene.ObjectType):
    user_id = graphene.String()
    email = graphene.String()
    full_name = graphene.String()
    first_name = graphene.String()
    last_name = graphene.String()
    name = graphene.String()
    vat_number = graphene.String()
    address = graphene.String()
    kyc = graphene.String()
    role = graphene.String()
    verification_status = graphene.String()
    wallet_balance = graphene.Float()
    created_at = graphene.String()

    has_bank_details = graphene.Boolean()
    iban_masked = graphene.String()


class Certificate(graphene.ObjectType):
    certificate_id = graphene.String()
    owner_type = graphene.String()
    owner_id = graphene.String()
    vehicle_id = graphene.String()
    request_year = graphene.Int()
    status = graphene.String()
    amount_co2 = graphene.Float()
    blockchain_hash = graphene.String()
    created_at = graphene.String()

class CertificationRequest(graphene.ObjectType):
    request_id = graphene.String()
    user_id = graphene.String()
    vehicle_type = graphene.String()
    vehicle_id = graphene.String()
    registration_year = graphene.Int()
    license_plate = graphene.String()
    vehicle_vin = graphene.String()
    request_year = graphene.Int()
    evidence_url = graphene.String()
    status = graphene.String()
    created_at = graphene.String()
    decided_at = graphene.String()
    updated_at = graphene.String()
    can_submit = graphene.Boolean()

class SellOrder(graphene.ObjectType):
    sell_order_id = graphene.String()
    seller_type = graphene.String()
    seller_id = graphene.String()
    certificate_id = graphene.String()
    min_price = graphene.Float()
    status = graphene.String()
    trade_id = graphene.String()
    matched_at = graphene.String()
    created_at = graphene.String()
    expires_at = graphene.String()

class Bid(graphene.ObjectType):
    bid_id = graphene.String()
    company_id = graphene.String()
    max_price = graphene.Float()
    status = graphene.String()
    created_at = graphene.String()
    filled_at = graphene.String()

class Trade(graphene.ObjectType):
    trade_id = graphene.String()
    certificate_id = graphene.String()
    sell_order_id = graphene.String()
    bid_id = graphene.String()
    company_id = graphene.String()
    price = graphene.Float()
    fee = graphene.Float()
    net = graphene.Float()
    status = graphene.String()
    blockchain_hash = graphene.String()
    created_at = graphene.String()

class B2BCertDecisionEvent(graphene.ObjectType):
    event_id = graphene.String()
    event_type = graphene.String()
    correlation_id = graphene.String()
    request_id = graphene.String()
    decision = graphene.String()
    certificate_id = graphene.String()
    created_at = graphene.String()
    status = graphene.String()

class MarketSellOrder(graphene.ObjectType):
    sell_order_id = graphene.String()
    seller_id = graphene.String()
    certificate_id = graphene.String()
    min_price = graphene.Float()
    status = graphene.String()
    created_at = graphene.String()
    expires_at = graphene.String()

class Payout(graphene.ObjectType):
    payout_id = graphene.String()
    amount = graphene.Float()
    status = graphene.String()
    created_at = graphene.String()




# --- QUERIES ---

#Queries B2B 3

class EdiMetaInput(graphene.InputObjectType):
    message_id = graphene.String(required=True)
    timestamp = graphene.String(required=True)
    source_system = graphene.String(required=True)
    schema_version = graphene.String(required=True)

class B2BCertVehicleInput(graphene.InputObjectType):
    vehicle_type = graphene.String(required=True)
    registration_year = graphene.Int(required=True)
    license_plate = graphene.String(required=True)
    vin = graphene.String(required=True)
    evidence_ref = graphene.String(required=False)

class B2BCertBatchDataInput(graphene.InputObjectType):
    request_year = graphene.Int(required=True)
    vehicles = graphene.List(B2BCertVehicleInput, required=True)

class B2BCertBatchSubmitInput(graphene.InputObjectType):
    meta = graphene.Argument(EdiMetaInput, required=True)
    data = graphene.Argument(B2BCertBatchDataInput, required=True)

class B2BCertBatchItem(graphene.ObjectType):
    vehicle_vin = graphene.String()
    license_plate = graphene.String()
    ok = graphene.Boolean()
    message = graphene.String()
    request_id = graphene.String()

class B2BCertBatchSubmitPayload(graphene.ObjectType):
    ok = graphene.Boolean()
    message = graphene.String()
    batch_id = graphene.String()
    items = graphene.List(B2BCertBatchItem)

class Query(graphene.ObjectType):
    # User queries
    users = graphene.List(User)
    user = graphene.Field(User, user_id=graphene.String(required=True))
    user_by_email = graphene.Field(User, email=graphene.String(required=True))
    current_user = graphene.Field(User)
    b2b_pending_cert_decision_events = graphene.List(B2BCertDecisionEvent)
    my_payouts = graphene.List(Payout)

    def resolve_my_payouts(root, info):
        user_id = info.context.get("user_id")
        if not user_id:
            return []
        from thg_exchange.repositories import payout_repo
        docs = payout_repo.find_payouts_by_user(user_id)
        return [Payout(
            payout_id=d.get("payoutId"),
            amount=d.get("amount"),
            status=d.get("status"),
            created_at=d.get("createdAt"),
        ) for d in docs]


    def resolve_users(root, info):
        docs = user_repo.find_all_users()
        return [User(
            user_id=d.get("userId"),
            email=d.get("email"),
            full_name=d.get("fullName"),
            first_name=d.get("firstName"),
            last_name=d.get("lastName"),
            name=d.get("name") or None,
            vat_number=d.get("vatNumber") or None,
            address=d.get("address") or None,
            kyc=json.dumps(d.get("kyc")) if d.get("kyc") else None,
            role=d.get("role"),
            verification_status=d.get("verificationStatus"),
            wallet_balance=d.get("walletBalance"),
            created_at=d.get("createdAt"),
        ) for d in docs]

    def resolve_user(root, info, user_id):
        doc = user_repo.find_by_id(user_id)
        if not doc:
            return None
        return User(
            user_id=doc.get("userId"),
            email=doc.get("email"),
            full_name=doc.get("fullName"),
            first_name=doc.get("firstName"),
            last_name=doc.get("lastName"),
            name=doc.get("name") or None,
            vat_number=doc.get("vatNumber") or None,
            address=doc.get("address") or None,
            kyc=json.dumps(doc.get("kyc")) if doc.get("kyc") else None,
            role=doc.get("role"),
            verification_status=doc.get("verificationStatus"),
            wallet_balance=doc.get("walletBalance"),
            created_at=doc.get("createdAt"),
        )

    def resolve_user_by_email(root, info, email):
        doc = user_repo.find_by_email(email)
        if not doc:
            return None
        return User(
            user_id=doc.get("userId"),
            email=doc.get("email"),
            full_name=doc.get("fullName"),
            first_name=doc.get("firstName"),
            last_name=doc.get("lastName"),
            name=doc.get("name") or None,
            vat_number=doc.get("vatNumber") or None,
            address=doc.get("address") or None,
            kyc=json.dumps(doc.get("kyc")) if doc.get("kyc") else None,
            role=doc.get("role"),
            verification_status=doc.get("verificationStatus"),
            wallet_balance=doc.get("walletBalance"),
            created_at=doc.get("createdAt"),
        )

    def resolve_current_user(root, info):
        user_id = info.context.get("user_id")
        if not user_id:
            return None

        doc = user_repo.find_by_id(user_id)
        if not doc:
            return None

        bank = doc.get("bank") or {}
        iban = bank.get("iban") or ""

        return User(
            user_id=doc.get("userId"),
            email=doc.get("email"),
            full_name=doc.get("fullName"),
            first_name=doc.get("firstName"),
            last_name=doc.get("lastName"),
            name=doc.get("name") or None,
            vat_number=doc.get("vatNumber") or None,
            address=doc.get("address") or None,
            kyc=json.dumps(doc.get("kyc")) if doc.get("kyc") else None,
            role=doc.get("role"),
            verification_status=doc.get("verificationStatus"),
            wallet_balance=doc.get("walletBalance"),
            created_at=doc.get("createdAt"),

            has_bank_details=user_repo.has_bank_details(user_id),
            iban_masked=user_repo.mask_iban(iban),
        )

    

    # Certificate queries
    certificate = graphene.Field(Certificate, certificate_id=graphene.String(required=True))
    my_certificates = graphene.List(Certificate)
    my_sellable_certificates = graphene.List(Certificate)

    def resolve_certificate(root, info, certificate_id):
        doc = trading_repo.find_certificate_for_user(info.context.get("user_id"), certificate_id)
        if not doc:
            return None
        return Certificate(
            certificate_id=doc.get("certificateId"),
            owner_type=doc.get("ownerType"),
            owner_id=doc.get("ownerId"),
            vehicle_id=doc.get("vehicleId"),
            request_year=doc.get("requestYear"),
            status=doc.get("status"),
            amount_co2=doc.get("amountCO2"),
            blockchain_hash=doc.get("blockchainHash"),
            created_at=doc.get("createdAt"),
        )

    def resolve_my_certificates(root, info):
        user_id = info.context.get("user_id")
        if not user_id:
            return []
        docs = trading_repo.find_user_certificates(user_id)
        return [Certificate(
            certificate_id=d.get("certificateId"),
            owner_type=d.get("ownerType"),
            owner_id=d.get("ownerId"),
            vehicle_id=d.get("vehicleId"),
            request_year=d.get("requestYear"),
            status=d.get("status"),
            amount_co2=d.get("amountCO2"),
            blockchain_hash=d.get("blockchainHash"),
            created_at=d.get("createdAt"),
        ) for d in docs]

    def resolve_my_sellable_certificates(root, info):
        user_id = info.context.get("user_id")
        if not user_id:
            return []
        docs = trading_repo.find_user_certified_certificates(user_id)
        return [Certificate(
            certificate_id=d.get("certificateId"),
            owner_type=d.get("ownerType"),
            owner_id=d.get("ownerId"),
            vehicle_id=d.get("vehicleId"),
            request_year=d.get("requestYear"),
            status=d.get("status"),
            amount_co2=d.get("amountCO2"),
            blockchain_hash=d.get("blockchainHash"),
            created_at=d.get("createdAt"),
        ) for d in docs]

    # Certification request queries
    my_cert_requests = graphene.List(CertificationRequest)
    cert_request = graphene.Field(CertificationRequest, request_id=graphene.String(required=True))
    admin_cert_requests = graphene.List(CertificationRequest)

    def resolve_my_cert_requests(root, info):
        user_id = info.context.get("user_id")
        if not user_id:
            return []
        docs = cert_repo.find_requests_by_user(user_id)
        return [CertificationRequest(
            request_id=d.get("requestId"),
            user_id=d.get("userId"),
            vehicle_type=d.get("vehicleType"),
            vehicle_id=d.get("vehicleId"),
            registration_year=d.get("registrationYear") or d.get("requestYear"),
            license_plate=d.get("licensePlate"),
            vehicle_vin=d.get("vehicleVin"),
            request_year=d.get("requestYear"),
            evidence_url=d.get("evidenceUrl") or d.get("evidenceRef"),
            status=d.get("status"),
            created_at=d.get("createdAt"),
            decided_at=d.get("decidedAt"),
            updated_at=d.get("updatedAt"),
            can_submit=d.get("status") == enums.REQ_NEEDS_MORE_INFO,
        ) for d in docs]

    def resolve_cert_request(root, info, request_id):
        user_id = info.context.get("user_id")
        if not user_id:
            return None
        doc = cert_repo.find_request_by_id_for_user(request_id, user_id)
        if not doc:
            return None
        return CertificationRequest(
            request_id=doc.get("requestId"),
            user_id=doc.get("userId"),
            vehicle_type=doc.get("vehicleType"),
            vehicle_id=doc.get("vehicleId"),
            registration_year=doc.get("registrationYear") or doc.get("requestYear"),
            license_plate=doc.get("licensePlate"),
            vehicle_vin=doc.get("vehicleVin"),
            request_year=doc.get("requestYear"),
            evidence_url=doc.get("evidenceUrl") or doc.get("evidenceRef"),
            status=doc.get("status"),
            created_at=doc.get("createdAt"),
            decided_at=doc.get("decidedAt"),
            updated_at=doc.get("updatedAt"),
            can_submit=doc.get("status") == enums.REQ_NEEDS_MORE_INFO,
        )

    def resolve_admin_cert_requests(root, info):
        docs = cert_repo.find_all_requests()
        return [CertificationRequest(
            request_id=d.get("requestId"),
            user_id=d.get("userId"),
            vehicle_type=d.get("vehicleType"),
            vehicle_id=d.get("vehicleId"),
            registration_year=d.get("registrationYear") or d.get("requestYear"),
            license_plate=d.get("licensePlate"),
            vehicle_vin=d.get("vehicleVin"),
            request_year=d.get("requestYear"),
            evidence_url=d.get("evidenceUrl") or d.get("evidenceRef"),
            status=d.get("status"),
            created_at=d.get("createdAt"),
            decided_at=d.get("decidedAt"),
            updated_at=d.get("updatedAt"),
            can_submit=d.get("status") == enums.REQ_NEEDS_MORE_INFO,
        ) for d in docs]
    
    def resolve_b2b_pending_cert_decision_events(root, info):
        user_id = info.context.get("user_id")
        if not user_id:
            return []

        docs = certification_service.list_pending_b2b_cert_decision_events()
        out = []
        for d in docs:
            payload = d.get("payload") or {}
            out.append(B2BCertDecisionEvent(
                event_id=d.get("eventId"),
                event_type=d.get("eventType"),
                correlation_id=d.get("correlationId"),
                request_id=payload.get("requestId"),
                decision=payload.get("decision"),
                certificate_id=payload.get("certificateId"),
                created_at=d.get("createdAt"),
                status=d.get("status"),
            ))
        return out


    # Sell order and trading queries
    my_sell_orders = graphene.List(SellOrder)
    all_bids = graphene.List(Bid)
    my_trades = graphene.List(Trade)
    market_sell_orders = graphene.List(MarketSellOrder)
    market_open_bids = graphene.List(Bid)
    admin_trades = graphene.List(Trade)
    market_open_bids = graphene.List(Bid)

    def resolve_market_open_bids(root, info):
        # any authenticated user can view open bids
        user_id = info.context.get("user_id")
        if not user_id:
            return []

        docs = trading_repo.list_open_bids()
        return [Bid(
            bid_id=d.get("bidId"),
            company_id=d.get("companyId"),
            max_price=d.get("maxPrice"),
            status=d.get("status"),
            created_at=d.get("createdAt"),
            filled_at=d.get("filledAt"),
        ) for d in docs]


    def resolve_market_open_bids(root, info):
        docs = trading_repo.list_open_bids()
        return [Bid(
            bid_id=d.get("bidId"),
            company_id=d.get("companyId"),
            max_price=d.get("maxPrice"),
            status=d.get("status"),
            created_at=d.get("createdAt"),
            filled_at=d.get("filledAt"),
        ) for d in docs]

    def resolve_my_sell_orders(root, info):
        user_id = info.context.get("user_id")
        if not user_id:
            return []
        trading_service.expire_open_orders_for_user(user_id)
        docs = trading_repo.find_sell_orders_by_user(user_id)
        return [SellOrder(
            sell_order_id=d.get("sellOrderId"),
            seller_type=d.get("sellerType"),
            seller_id=d.get("sellerId"),
            certificate_id=d.get("certificateId"),
            min_price=d.get("minPrice"),
            status=d.get("status"),
            trade_id=d.get("tradeId"),
            matched_at=d.get("matchedAt"),
            created_at=d.get("createdAt"),
            expires_at=d.get("expiresAt"),
        ) for d in docs]

    def resolve_all_bids(root, info):
        docs = trading_repo.list_bids()
        return [Bid(
            bid_id=d.get("bidId"),
            company_id=d.get("companyId"),
            max_price=d.get("maxPrice"),
            status=d.get("status"),
            created_at=d.get("createdAt"),
            filled_at=d.get("filledAt"),
        ) for d in docs]

    def resolve_my_trades(root, info):
        user_id = info.context.get("user_id")
        if not user_id:
            return []

        # all sell orders of this user (placed + matched + cancelled)
        orders = trading_repo.find_sell_orders_by_user(user_id)
        sell_order_ids = [o.get("sellOrderId") for o in orders if o.get("sellOrderId")]

        trades = trading_repo.find_trades_by_sell_order_ids(sell_order_ids)

        return [Trade(
            trade_id=t.get("tradeId"),
            certificate_id=t.get("certificateId"),
            sell_order_id=t.get("sellOrderId"),
            bid_id=t.get("bidId"),
            company_id=t.get("companyId"),
            price=t.get("price"),
            fee=t.get("fee"),
            net=t.get("net"),
            status=t.get("status"),
            blockchain_hash=t.get("blockchainHash"),
            created_at=t.get("createdAt"),
        ) for t in trades]
    
    def resolve_market_sell_orders(root, info):
        # optional role check: nur business
        # if info.context.get("role") != enums.USER_ROLE_BUSINESS: return []
        docs = trading_service.list_open_sell_orders_for_market()
        return [MarketSellOrder(
            sell_order_id=d.get("sellOrderId"),
            seller_id=d.get("sellerId"),
            certificate_id=d.get("certificateId"),
            min_price=d.get("minPrice"),
            status=d.get("status"),
            created_at=d.get("createdAt"),
            expires_at=d.get("expiresAt"),
        ) for d in docs]
    
    def resolve_admin_trades(root, info):
        role = info.context.get("role")
        if role != enums.USER_ROLE_ADMIN:
            return []
        docs = trading_repo.find_all_trades()
        return [Trade(
            trade_id=t.get("tradeId"),
            certificate_id=t.get("certificateId"),
            sell_order_id=t.get("sellOrderId"),
            bid_id=t.get("bidId"),
            company_id=t.get("companyId"),
            price=t.get("price"),
            fee=t.get("fee"),
            net=t.get("net"),
            status=t.get("status"),
            blockchain_hash=t.get("blockchainHash"),
            created_at=t.get("createdAt"),
        ) for t in docs]


# --- MUTATIONS ---

# Authentication Mutations
class AuthLogin(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    access_token = graphene.String()
    user_id = graphene.String()
    role = graphene.String()

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(root, info, email, password):
        ok, msg, data = auth_service.authenticate(email, password)
        if ok:
            user_id = data.get("userId")
            access_token = create_access_token(user_id, data.get("role"))
            return AuthLogin(
                ok=True,
                message=msg,
                access_token=access_token,
                user_id=user_id,
                role=data.get("role")
            )
        return AuthLogin(ok=False, message=msg, access_token=None, user_id=None, role=None)

# User Mutations
class RegisterUser(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    user_id = graphene.String()
    
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        password_repeat = graphene.String(required=True)
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        role = graphene.String(required=False)

    def mutate(root, info, email, password, password_repeat, first_name, last_name, role=None):
        ok, msg, data = auth_service.register_user(email, password, password_repeat, first_name, last_name, role)
        return RegisterUser(ok=ok, message=msg, user_id=data.get("userId"))


class RegisterBusiness(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    user_id = graphene.String()

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        password_repeat = graphene.String(required=True)
        name = graphene.String(required=True)
        vat_number = graphene.String(required=True)
        address = graphene.String(required=True)

    def mutate(root, info, email, password, password_repeat, name, vat_number, address):
        ok, msg, data = auth_service.register_business(email, password, password_repeat, name, vat_number, address)
        return RegisterBusiness(ok=ok, message=msg, user_id=data.get("userId"))

class VerifyEmail(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        token = graphene.String(required=True)

    def mutate(root, info, token):
        ok, msg = auth_service.verify_email_token(token)
        return VerifyEmail(ok=ok, message=msg)

class SubmitIdentity(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        doc_type = graphene.String(required=True)
        doc_ref = graphene.String(required=True)

    def mutate(root, info, doc_type, doc_ref):
        user_id = info.context.get("user_id")
        if not user_id:
            return SubmitIdentity(ok=False, message="Not authenticated")
        ok, msg = auth_service.submit_identity(user_id, doc_type, doc_ref)
        return SubmitIdentity(ok=ok, message=msg)

class UpdateVerificationStatus(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        user_id = graphene.String(required=True)
        status = graphene.String(required=True)

    def mutate(root, info, user_id, status):
        user_repo.set_verification_status(user_id, status)
        return UpdateVerificationStatus(ok=True, message="Verification status updated")

class DeleteUser(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        user_id = graphene.String(required=True)

    def mutate(root, info, user_id):
        user_repo.delete_user(user_id)
        return DeleteUser(ok=True, message="User deleted")
    
# Payout
class SetBankDetails(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        iban = graphene.String(required=True)
        bic = graphene.String(required=False)
        holder = graphene.String(required=True)

    def mutate(root, info, iban, holder, bic=""):
        user_id = info.context.get("user_id")
        if not user_id:
            return SetBankDetails(ok=False, message="Not authenticated")
        ok, msg = payout_service.set_bank_details(user_id, iban, bic, holder)
        return SetBankDetails(ok=ok, message=msg)

class RequestPayout(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    payout_id = graphene.String()

    def mutate(root, info):
        user_id = info.context.get("user_id")
        if not user_id:
            return RequestPayout(ok=False, message="Not authenticated", payout_id=None)
        ok, msg, payout_id = payout_service.request_payout(user_id)
        return RequestPayout(ok=ok, message=msg, payout_id=payout_id)


# Certification Mutations
class SubmitCertificationRequest(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    request_id = graphene.String()

    class Arguments:
        vehicle_type = graphene.String(required=True)
        vehicle_id = graphene.String(required=False)
        registration_year = graphene.String(required=True)
        license_plate = graphene.String(required=True)
        request_year = graphene.String(required=False)
        vehicle_vin = graphene.String(required=False)
        evidence_url = graphene.String(required=False)

    def mutate(root, info, vehicle_type, registration_year, license_plate, vehicle_id=None, request_year=None, vehicle_vin="", evidence_url=""):
        user_id = info.context.get("user_id")
        if not user_id:
            return SubmitCertificationRequest(ok=False, message="Not authenticated", request_id=None)
        ok, msg, request_id = certification_service.submit_request(
            user_id,
            vehicle_type,
            vehicle_id,
            registration_year,
            license_plate,
            vehicle_vin,
            evidence_url,
            request_year,
        )
        return SubmitCertificationRequest(ok=ok, message=msg, request_id=request_id)


class UpdateCertificationRequest(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    request_id = graphene.String()

    class Arguments:
        request_id = graphene.String(required=True)
        vehicle_type = graphene.String(required=True)
        vehicle_id = graphene.String(required=False)
        registration_year = graphene.String(required=True)
        license_plate = graphene.String(required=True)
        request_year = graphene.String(required=False)
        vehicle_vin = graphene.String(required=False)
        evidence_url = graphene.String(required=False)

    def mutate(root, info, request_id, vehicle_type, registration_year, license_plate, vehicle_id=None, request_year=None, vehicle_vin="", evidence_url=""):
        user_id = info.context.get("user_id")
        if not user_id:
            return UpdateCertificationRequest(ok=False, message="Not authenticated", request_id=None)
        ok, msg, updated_request_id = certification_service.update_request(
            user_id,
            request_id,
            vehicle_type,
            vehicle_id,
            registration_year,
            license_plate,
            vehicle_vin,
            evidence_url,
            request_year,
        )
        return UpdateCertificationRequest(ok=ok, message=msg, request_id=updated_request_id if ok else None)

class DecideCertificationRequest(graphene.Mutation):
    ok = graphene.Boolean()
    cert_id = graphene.String()
    message = graphene.String()

    class Arguments:
        request_id = graphene.String(required=True)
        decision = graphene.String(required=True)

    def mutate(root, info, request_id, decision):
        ok, msg, cert_id = certification_service.admin_decide_request(request_id, decision)
        return DecideCertificationRequest(ok=ok, message=msg)

# Trading Mutations
class CreateSellOrder(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    sell_order_id = graphene.String()

    class Arguments:
        certificate_id = graphene.String(required=True)
        min_price = graphene.String(required=False)
        valid_until = graphene.String(required=True)

    def mutate(root, info, certificate_id, min_price="0.0", valid_until=""):
        user_id = info.context.get("user_id")
        if not user_id:
            return CreateSellOrder(ok=False, message="Not authenticated", sell_order_id=None)
        ok, msg = trading_service.create_sell_order(user_id, certificate_id, min_price, valid_until)
        sell_order_id = None
        if ok:
            docs = trading_repo.find_sell_orders_by_user(user_id)
            if docs:
                sell_order_id = docs[0].get("sellOrderId")
        return CreateSellOrder(ok=ok, message=msg, sell_order_id=sell_order_id)


class UpdateSellOrder(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    sell_order_id = graphene.String()

    class Arguments:
        sell_order_id = graphene.String(required=True)
        min_price = graphene.String(required=False)
        valid_until = graphene.String(required=True)

    def mutate(root, info, sell_order_id, valid_until, min_price="0.0"):
        user_id = info.context.get("user_id")
        if not user_id:
            return UpdateSellOrder(ok=False, message="Not authenticated", sell_order_id=None)
        ok, msg = trading_service.update_sell_order(user_id, sell_order_id, min_price, valid_until)
        return UpdateSellOrder(ok=ok, message=msg, sell_order_id=sell_order_id if ok else None)


class CancelSellOrder(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    sell_order_id = graphene.String()

    class Arguments:
        sell_order_id = graphene.String(required=True)

    def mutate(root, info, sell_order_id):
        user_id = info.context.get("user_id")
        if not user_id:
            return CancelSellOrder(ok=False, message="Not authenticated", sell_order_id=None)
        ok, msg = trading_service.cancel_sell_order(user_id, sell_order_id)
        return CancelSellOrder(ok=ok, message=msg, sell_order_id=sell_order_id if ok else None)

class CreateBid(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    bid_id = graphene.String()

    class Arguments:
        company_id = graphene.String(required=False)
        max_price = graphene.String(required=True)

    def mutate(root, info, max_price, company_id=None):
        ok, msg = trading_service.admin_create_bid(company_id or "company_demo", max_price)
        bid_id = None
        if ok:
            docs = trading_repo.list_bids()
            if docs:
                bid_id = docs[0].get("bidId")
        return CreateBid(ok=ok, message=msg, bid_id=bid_id)
    
class B2BCreateBid(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    bid_id = graphene.String()
    trade_id = graphene.String()

    class Arguments:
        max_price = graphene.String(required=True)

    def mutate(root, info, max_price):
        user_id = info.context.get("user_id")
        role = info.context.get("role")
        if not user_id:
            return B2BCreateBid(ok=False, message="Not authenticated", bid_id=None, trade_id=None)
        if role != enums.USER_ROLE_BUSINESS:
            return B2BCreateBid(ok=False, message="Forbidden", bid_id=None, trade_id=None)

        ok, msg, bid_id, trade_id = trading_service.create_bid_for_business(user_id, max_price)
        return B2BCreateBid(ok=ok, message=msg, bid_id=bid_id, trade_id=trade_id)

class B2BCancelBid(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        bid_id = graphene.String(required=True)

    def mutate(root, info, bid_id):
        user_id = info.context.get("user_id")
        role = info.context.get("role")
        if not user_id:
            return B2BCancelBid(ok=False, message="Not authenticated")
        if role != enums.USER_ROLE_BUSINESS:
            return B2BCancelBid(ok=False, message="Forbidden")

        ok, msg = trading_service.cancel_bid_for_business(user_id, bid_id)
        return B2BCancelBid(ok=ok, message=msg)


# B2B UC3 Mutations
class B2BSubmitCertBatch(graphene.Mutation):
    Output = B2BCertBatchSubmitPayload

    class Arguments:
        input = B2BCertBatchSubmitInput(required=True)

    def mutate(root, info, input):
        user_id = info.context.get("user_id")
        if not user_id:
            return B2BCertBatchSubmitPayload(ok=False, message="Not authenticated", batch_id=None, items=[])

        meta = input.get("meta") or {}
        data = input.get("data") or {}

        message_id = meta.get("message_id")
        source_system = meta.get("source_system")
        request_year = data.get("request_year")
        vehicles_in = data.get("vehicles") or []

        vehicles = []
        for v in vehicles_in:
            vehicles.append({
                "vehicleType": v.get("vehicle_type"),
                "registrationYear": v.get("registration_year"),
                "licensePlate": v.get("license_plate"),
                "vin": v.get("vin"),
                "evidenceRef": v.get("evidence_ref") or "",
            })

        resp = certification_service.submit_b2b_batch(
            user_id=user_id,
            message_id=message_id,
            source_system=source_system,
            request_year=request_year,
            vehicles=vehicles,
        )

        items = [
            B2BCertBatchItem(
                vehicle_vin=i.get("vehicleVin"),
                license_plate=i.get("licensePlate"),
                ok=i.get("ok"),
                message=i.get("message"),
                request_id=i.get("requestId"),
            )
            for i in resp.get("items") or []
        ]

        return B2BCertBatchSubmitPayload(
            ok=resp.get("ok"),
            message=resp.get("message"),
            batch_id=resp.get("batchId"),
            items=items,
        )
    
class AdminDecideCertRequestEmitEvent(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    event_id = graphene.String()

    class Arguments:
        request_id = graphene.String(required=True)
        decision = graphene.String(required=True)

    def mutate(root, info, request_id, decision):
        role = info.context.get("role")
        if role != enums.USER_ROLE_ADMIN:
            return AdminDecideCertRequestEmitEvent(ok=False, message="Forbidden", event_id=None)

        ok, msg, event_id = certification_service.admin_decide_request_and_emit_b2b_event(request_id, decision)
        return AdminDecideCertRequestEmitEvent(ok=ok, message=msg, event_id=event_id)
    
class B2BAckCertDecisionEvent(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        event_id = graphene.String(required=True)

    def mutate(root, info, event_id):
        user_id = info.context.get("user_id")
        if not user_id:
            return B2BAckCertDecisionEvent(ok=False, message="Not authenticated")

        ok, msg = certification_service.ack_b2b_cert_decision_event(event_id)
        return B2BAckCertDecisionEvent(ok=ok, message=msg)




class Mutation(graphene.ObjectType):
    # Authentication Mutations
    auth_login = AuthLogin.Field()
    
    # User Mutations
    register_user = RegisterUser.Field()
    register_business = RegisterBusiness.Field()
    verify_email = VerifyEmail.Field()
    submit_identity = SubmitIdentity.Field()
    update_verification_status = UpdateVerificationStatus.Field()
    delete_user = DeleteUser.Field()

    # Payout Mutations
    set_bank_details = SetBankDetails.Field()
    request_payout = RequestPayout.Field()

    
    # Certification Mutations
    submit_certification_request = SubmitCertificationRequest.Field()
    update_certification_request = UpdateCertificationRequest.Field()
    decide_certification_request = DecideCertificationRequest.Field()
    # B2B UC3
    b2b_submit_cert_batch = B2BSubmitCertBatch.Field()
    admin_decide_cert_request_emit_event = AdminDecideCertRequestEmitEvent.Field()
    b2b_ack_cert_decision_event = B2BAckCertDecisionEvent.Field()


    
    # Trading Mutations
    create_sell_order = CreateSellOrder.Field()
    update_sell_order = UpdateSellOrder.Field()
    cancel_sell_order = CancelSellOrder.Field()
    create_bid = CreateBid.Field()
    b2b_create_bid = B2BCreateBid.Field()
    b2b_cancel_bid = B2BCancelBid.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)

