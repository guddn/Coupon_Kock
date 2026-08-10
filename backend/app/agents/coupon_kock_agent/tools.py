from typing import Any

from app.services.calculator import DiscountRule, calculate_option, rank_options
from app.services.store_matcher import haversine_distance_m

DEMO_STORES = (
    {
        "store_id": "demo-store",
        "name": "스타카페 아주대점",
        "canonical_brand": "스타카페",
        "latitude": 37.2822,
        "longitude": 127.0437,
    },
)


def match_nearby_store(
    latitude: float,
    longitude: float,
    store_id: str = "",
    radius_m: int = 100,
) -> dict[str, Any]:
    """Finds a supported store near a coordinate using deterministic distance math.

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
    if not 1 <= radius_m <= 1_000:
        return {"status": "invalid_radius", "message": "검색 반경은 1~1000m여야 합니다."}

    candidates = [item for item in DEMO_STORES if not store_id or item["store_id"] == store_id]
    if not candidates:
        return {"status": "not_found", "message": "선택한 매장은 현재 지원되지 않습니다."}

    nearest = min(
        candidates,
        key=lambda item: haversine_distance_m(
            latitude,
            longitude,
            float(item["latitude"]),
            float(item["longitude"]),
        ),
    )
    distance_m = round(
        haversine_distance_m(
            latitude,
            longitude,
            float(nearest["latitude"]),
            float(nearest["longitude"]),
        ),
        1,
    )
    if distance_m > radius_m:
        return {
            "status": "outside_radius",
            "nearest_distance_m": distance_m,
            "message": "설정 반경 안에 지원 매장이 없습니다.",
        }
    return {
        "status": "success",
        "store": {
            "store_id": nearest["store_id"],
            "name": nearest["name"],
            "canonical_brand": nearest["canonical_brand"],
            "distance_m": distance_m,
        },
        "data_source": "development_fixture",
    }


def load_user_benefit_context(user_id: str, canonical_brand: str) -> dict[str, Any]:
    """Loads active coupons and non-sensitive benefit profile fields for a user.

    Args:
        user_id: Application user identifier. Never a card number or coupon PIN.
        canonical_brand: Canonical brand returned by match_nearby_store.

    Returns:
        Active coupons and a minimal card/telecom profile. The MVP currently uses fixtures.
    """
    if not user_id.strip():
        return {"status": "invalid_user", "message": "user_id가 필요합니다."}

    coupons: list[dict[str, Any]] = []
    if canonical_brand == "스타카페":
        coupons.append(
            {
                "coupon_id": "demo-coupon",
                "brand": "스타카페",
                "name": "모바일 금액권",
                "face_value": 5_000,
                "status": "active",
                "expires_on": "2026-12-31",
            }
        )
    return {
        "status": "success",
        "coupons": coupons,
        "profile": {
            "card_product": "데모 카드",
            "telecom_provider": None,
            "eligibility_confirmed": False,
        },
        "data_source": "development_fixture",
        "privacy": "카드번호, 쿠폰 PIN, 정확한 위치를 저장하거나 반환하지 않음",
    }


def retrieve_official_benefit_rules(
    canonical_brand: str,
    card_product: str = "",
    telecom_provider: str = "",
) -> dict[str, Any]:
    """Retrieves benefit rules and their evidence for a store and user profile.

    Args:
        canonical_brand: Canonical merchant brand.
        card_product: User-selected card product name, never a card number.
        telecom_provider: User-selected telecom provider.

    Returns:
        Rule candidates and source metadata. Current entries are explicit demo fixtures,
        not official RAG evidence, and must be labelled as such in the final answer.
    """
    if canonical_brand != "스타카페" or card_product != "데모 카드":
        return {
            "status": "no_evidence",
            "rules": [],
            "sources": [],
            "message": "현재 프로필과 매장에 적용할 근거 문서가 없습니다.",
        }
    return {
        "status": "fixture_only",
        "rules": [
            {
                "rule_id": "demo-card-rule",
                "name": "카드 10% 할인 (데모)",
                "kind": "card",
                "discount_type": "percentage",
                "value": 10,
                "min_purchase": 0,
                "max_discount": 1_000,
                "stackable_with_coupon": True,
                "source_id": "demo-source",
                "eligibility": "needs_confirmation",
            }
        ],
        "sources": [
            {
                "source_id": "demo-source",
                "title": "개발용 혜택 fixture - 공식 RAG 문서 연결 필요",
                "url": "https://example.com/replace-with-official-source",
                "is_official": False,
            }
        ],
        "message": "공식 문서가 아직 적재되지 않아 데모 규칙만 반환했습니다.",
    }


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
