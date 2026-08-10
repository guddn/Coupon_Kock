from datetime import date
from uuid import uuid4

from app.models.schemas import (
    BenefitSource,
    RecommendationRequest,
    RecommendationResponse,
    Store,
)
from app.services.calculator import DiscountRule, calculate_option, rank_options


def build_demo_recommendation(request: RecommendationRequest) -> RecommendationResponse:
    """Development fixture; production adapters must supply Firestore/RAG evidence."""
    coupon = DiscountRule(
        rule_id="demo-coupon",
        name="보유 쿠폰",
        kind="coupon",
        discount_type="fixed",
        value=5_000,
    )
    card = DiscountRule(
        rule_id="demo-card",
        name="공식 문서 기반 카드 할인 (데모)",
        kind="card",
        discount_type="percentage",
        value=10,
        max_discount=1_000,
        source_id="demo-source",
    )
    options = rank_options(
        [
            calculate_option(request.purchase_amount, [coupon], "coupon-only"),
            calculate_option(request.purchase_amount, [coupon, card], "coupon-card"),
        ]
    )
    source = BenefitSource(
        source_id="demo-source",
        title="개발용 공식 혜택 fixture - 실제 배포 전 교체",
        url="https://example.com/replace-with-official-source",
        valid_from=date(2026, 1, 1),
        valid_to=date(2026, 12, 31),
    )
    return RecommendationResponse(
        request_id=str(uuid4()),
        store=Store(
            store_id=request.store_id or "demo-store",
            name="데모 매장",
            canonical_brand="demo-brand",
            distance_m=0,
        ),
        candidate_options=options,
        recommended_option=options[0],
        conditions_to_check=["카드 전월 실적과 월 할인 한도는 사용자가 확인해야 합니다."],
        sources=[source],
        message="개발용 fixture 결과입니다. 실제 추천에는 Firestore/RAG 공식 근거를 연결하세요.",
    )
