from datetime import UTC, datetime
from typing import Any

from app.core.config import settings
from app.services.benefit_rag import benefit_rag_service
from app.services.brand_matcher import brand_matches_store
from app.services.calculator import DiscountRule, calculate_option, rank_options
from app.services.coupon_registry import coupon_registry
from app.services.public_store_client import public_store_client


def match_nearby_store(
    latitude: float,
    longitude: float,
    store_id: str = "",
    radius_m: int = 1_000,
) -> dict[str, Any]:
    """Finds the selected or nearest store through the public-data adapter.

    Args:
        latitude: User latitude between -90 and 90.
        longitude: User longitude between -180 and 180.
        store_id: Optional store identifier selected by the user.
        radius_m: Maximum matching distance in meters.

    Returns:
        A store match result without echoing the user's exact coordinates.
    """
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return {"status": "invalid_location", "message": "위치 좌표 범위가 올바르지 않습니다."}
    if not 100 <= radius_m <= 5_000:
        return {"status": "invalid_radius", "message": "검색 반경은 100~5000m여야 합니다."}

    nearby = public_store_client.nearby(latitude, longitude, radius_m)
    selected = (
        next(
            (store for store in nearby.stores if store.store_id == store_id),
            None,
        )
        if store_id
        else (nearby.stores[0] if nearby.stores else None)
    )
    if selected is None:
        return {
            "status": "not_found",
            "message": "현재 위치 주변에서 선택 가능한 매장을 찾지 못했습니다.",
            "data_source": nearby.data_source,
        }
    return {
        "status": "success",
        "store": {
            "store_id": selected.store_id,
            "name": selected.name,
            "canonical_brand": selected.name,
            "category": selected.category,
            "distance_m": selected.distance_m,
        },
        "data_source": nearby.data_source,
        "notice": nearby.notice,
    }


def load_user_benefit_context(
    user_id: str,
    canonical_brand: str,
    card_product: str = "",
) -> dict[str, Any]:
    """Loads active coupons and non-sensitive benefit profile fields for a user.

    Args:
        user_id: Application user identifier. Never a card number or coupon PIN.
        canonical_brand: Canonical brand returned by match_nearby_store.
        card_product: Card product selected in the request, never a card number.

    Returns:
        Active matching coupons from the configured registry and an empty benefit profile.
    """
    if not user_id.strip():
        return {"status": "invalid_user", "message": "user_id가 필요합니다."}

    today = datetime.now(UTC).date()
    coupons = [
        {
            "coupon_id": coupon.coupon_id,
            "brand": coupon.brand,
            "name": coupon.product_name,
            "face_value": coupon.face_value,
            "status": "active",
            "expires_on": coupon.expiry_date.isoformat(),
        }
        for coupon in coupon_registry.list_for_user(user_id)
        if coupon.expiry_date >= today and brand_matches_store(coupon.brand, canonical_brand)
    ]
    return {
        "status": "success",
        "coupons": coupons,
        "profile": {
            "card_product": card_product or settings.demo_card_product or None,
            "telecom_provider": None,
            "eligibility_confirmed": False,
        },
        "data_source": "configured_coupon_registry",
        "privacy": "카드번호, 쿠폰 PIN, 정확한 위치를 저장하거나 반환하지 않음",
    }


def retrieve_official_benefit_rules(
    canonical_brand: str,
    card_product: str = "",
    telecom_provider: str = "",
    merchant_category: str = "",
) -> dict[str, Any]:
    """Searches embedded official card documents for evidence-backed rules.

    Args:
        canonical_brand: Canonical merchant brand.
        card_product: User-selected card product name, never a card number.
        telecom_provider: User-selected telecom provider.
        merchant_category: Public-data merchant category when available.

    Returns:
        Matching rules, official sources, and vector retrieval metadata.
    """
    try:
        result = benefit_rag_service.search(
            canonical_brand=canonical_brand,
            card_product=card_product,
            merchant_category=merchant_category,
        )
    except Exception as error:  # noqa: BLE001 - tool must return a safe structured failure
        return {
            "status": "retrieval_error",
            "rules": [],
            "sources": [],
            "message": "공식 혜택 임베딩 검색에 실패했습니다.",
            "error_type": type(error).__name__,
        }
    result["query"] = {
        "canonical_brand": canonical_brand,
        "merchant_category": merchant_category,
        "card_product_configured": bool(card_product),
        "telecom_provider_configured": bool(telecom_provider),
    }
    return result


def calculate_discount_options(
    purchase_amount: int,
    coupon_face_value: int = 0,
    card_discount_percent: int = 0,
    card_max_discount: int = 0,
    card_stackable_with_coupon: bool = False,
    card_source_id: str = "",
) -> dict[str, Any]:
    """Enumerates and ranks payable-price options using deterministic Python code.

    Args:
        purchase_amount: Original purchase amount in KRW.
        coupon_face_value: Active coupon face value in KRW, or zero.
        card_discount_percent: Card percentage from retrieved evidence, or zero.
        card_max_discount: Maximum card discount in KRW, or zero for no card rule.
        card_stackable_with_coupon: Whether evidence explicitly allows coupon stacking.
        card_source_id: Evidence source identifier for the card rule.

    Returns:
        Ranked options. The first item is always the recommended lowest final price.
    """
    if not 0 <= purchase_amount <= 10_000_000:
        return {"status": "invalid_amount", "message": "결제금액 범위가 올바르지 않습니다."}
    if not 0 <= coupon_face_value <= 10_000_000:
        return {"status": "invalid_coupon", "message": "쿠폰 금액 범위가 올바르지 않습니다."}
    if not 0 <= card_discount_percent <= 100 or card_max_discount < 0:
        return {"status": "invalid_card_rule", "message": "카드 할인 규칙이 올바르지 않습니다."}

    coupon_rule = DiscountRule(
        rule_id="active-coupon",
        name="보유 쿠폰",
        kind="coupon",
        discount_type="fixed",
        value=coupon_face_value,
    )
    card_rule = DiscountRule(
        rule_id="retrieved-card-rule",
        name="카드 할인",
        kind="card",
        discount_type="percentage",
        value=card_discount_percent,
        max_discount=card_max_discount or None,
        source_id=card_source_id or None,
    )

    options = [calculate_option(purchase_amount, [], "no-benefit")]
    if coupon_face_value:
        options.append(calculate_option(purchase_amount, [coupon_rule], "coupon-only"))
    if card_discount_percent and card_source_id:
        options.append(calculate_option(purchase_amount, [card_rule], "card-only"))
        if coupon_face_value and card_stackable_with_coupon:
            options.append(
                calculate_option(purchase_amount, [coupon_rule, card_rule], "coupon-card")
            )

    ranked = rank_options(options)
    return {
        "status": "success",
        "recommended_option": ranked[0].model_dump(),
        "alternatives": [option.model_dump() for option in ranked[1:]],
        "calculation_policy": "deterministic; coupon then card when stacking is explicitly allowed",
    }
