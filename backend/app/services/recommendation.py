from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from app.core.config import settings
from app.models.schemas import (
    NearbyStoresResponse,
    RecommendationRequest,
    RecommendationResponse,
    RegisteredCoupon,
    Store,
)
from app.services.benefit_rag import BenefitRagService, benefit_rag_service
from app.services.brand_matcher import brand_matches_store
from app.services.calculator import DiscountRule, calculate_option, rank_options
from app.services.coupon_registry import CouponRegistry, coupon_registry
from app.services.public_store_client import public_store_client


class StoreClient(Protocol):
    def nearby(self, latitude: float, longitude: float, radius_m: int) -> NearbyStoresResponse: ...


class RecommendationUnavailableError(RuntimeError):
    """Raised when there is no public-data store that can anchor a recommendation."""


def _select_store(request: RecommendationRequest, store_client: StoreClient):
    nearby = store_client.nearby(request.latitude, request.longitude, 1_000)
    if request.store_id:
        selected = next(
            (store for store in nearby.stores if store.store_id == request.store_id),
            None,
        )
        if selected is None:
            raise RecommendationUnavailableError(
                "선택한 매장을 현재 위치 주변에서 찾지 못했습니다."
            )
    else:
        selected = nearby.stores[0] if nearby.stores else None
    if selected is None:
        raise RecommendationUnavailableError("현재 위치 반경 1km 안에서 매장을 찾지 못했습니다.")
    return nearby, selected


def _active_matching_coupons(
    coupons: list[RegisteredCoupon], store_name: str
) -> list[RegisteredCoupon]:
    today = datetime.now(UTC).date()
    return [
        coupon
        for coupon in coupons
        if coupon.expiry_date >= today and brand_matches_store(coupon.brand, store_name)
    ]


def build_recommendation(
    request: RecommendationRequest,
    registry: CouponRegistry = coupon_registry,
    store_client: StoreClient = public_store_client,
    rag_service: BenefitRagService = benefit_rag_service,
) -> RecommendationResponse:
    """Build a deterministic recommendation from coupons and official benefit RAG."""
    nearby, selected_store = _select_store(request, store_client)
    coupons = _active_matching_coupons(registry.list_for_user(request.user_id), selected_store.name)

    options = [calculate_option(request.purchase_amount, [], "no-benefit")]
    for coupon in coupons:
        rule = DiscountRule(
            rule_id=coupon.coupon_id,
            name=f"{coupon.brand} {coupon.product_name}",
            kind="coupon",
            discount_type="fixed",
            value=coupon.face_value,
        )
        options.append(
            calculate_option(
                request.purchase_amount,
                [rule],
                f"coupon-{coupon.coupon_id}",
            )
        )
    card_product = request.card_product or settings.demo_card_product
    try:
        rag_result = rag_service.search(
            canonical_brand=selected_store.name,
            card_product=card_product,
            merchant_category=selected_store.category,
        )
    except Exception:  # noqa: BLE001 - recommendation degrades safely when RAG is unavailable
        rag_result = {
            "status": "retrieval_error",
            "rules": [],
            "sources": [],
            "message": "공식 혜택 임베딩 검색에 실패했습니다.",
        }

    for card_benefit in rag_result["rules"]:
        card_rule = DiscountRule(
            rule_id=card_benefit["rule_id"],
            name=f"{card_benefit['card_product']} {card_benefit['name']}",
            kind="card",
            discount_type="percentage",
            value=card_benefit["discount_percent"],
            max_discount=card_benefit["max_discount"],
            source_id=card_benefit["source_id"],
        )
        options.append(
            calculate_option(
                request.purchase_amount,
                [card_rule],
                f"card-{card_benefit['rule_id']}",
            )
        )
    options = rank_options(options)

    conditions = [
        condition
        for card_benefit in rag_result["rules"]
        for condition in card_benefit.get("conditions", [])
    ]
    if rag_result["status"] != "success":
        conditions.append(rag_result["message"])
    if nearby.data_source == "fixture":
        conditions.append(nearby.notice or "공공데이터 대신 샘플 매장을 사용했습니다.")
    if not coupons:
        conditions.append("이 매장과 브랜드가 일치하는 유효 쿠폰이 없습니다.")

    message = "등록 쿠폰과 공식 카드 혜택 임베딩 검색 결과를 비교했습니다."
    return RecommendationResponse(
        request_id=str(uuid4()),
        store=Store(
            store_id=selected_store.store_id,
            name=selected_store.name,
            canonical_brand=selected_store.name,
            distance_m=selected_store.distance_m,
        ),
        candidate_options=options,
        recommended_option=options[0],
        conditions_to_check=conditions,
        sources=rag_result["sources"],
        message=message,
    )
