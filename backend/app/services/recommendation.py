from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from app.models.schemas import (
    NearbyStoresResponse,
    RecommendationRequest,
    RecommendationResponse,
    RegisteredCoupon,
    Store,
)
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
) -> RecommendationResponse:
    """Build a deterministic recommendation from public stores and registered coupons."""
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
    options = rank_options(options)

    conditions = ["카드 혜택은 공식 혜택 RAG가 구축된 뒤 추가됩니다."]
    if nearby.data_source == "fixture":
        conditions.append(nearby.notice or "공공데이터 대신 샘플 매장을 사용했습니다.")
    if not coupons:
        conditions.append("이 매장과 브랜드가 일치하는 유효 쿠폰이 없습니다.")

    message = (
        "등록된 유효 쿠폰을 반영한 결과입니다."
        if coupons
        else "적용 가능한 등록 쿠폰이 없어 할인 없는 결제금액을 표시합니다."
    )
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
        sources=[],
        message=message,
    )
