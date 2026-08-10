from fastapi import APIRouter

from app.models.schemas import (
    Coupon,
    CouponParseRequest,
    RecommendationRequest,
    RecommendationResponse,
)
from app.services.coupon_parser import parse_coupon_placeholder
from app.services.recommendation import build_demo_recommendation

router = APIRouter(prefix="/api")


@router.post("/coupons/parse", response_model=Coupon)
def parse_coupon(request: CouponParseRequest) -> Coupon:
    return parse_coupon_placeholder(request.sanitized_raw_text)


@router.post("/recommendations", response_model=RecommendationResponse)
def create_recommendation(request: RecommendationRequest) -> RecommendationResponse:
    return build_demo_recommendation(request)
