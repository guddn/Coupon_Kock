from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status

from app.agents.coupon_kock_agent import root_agent
from app.agents.coupon_kock_agent.agent import AGENT_TOOL_NAMES
from app.core.config import settings
from app.models.schemas import (
    AgentInfoResponse,
    AgentRecommendationRequest,
    AgentRecommendationResponse,
    Coupon,
    CouponCreateRequest,
    CouponParseRequest,
    NearbyStoresResponse,
    RecommendationRequest,
    RecommendationResponse,
    RegisteredCoupon,
)
from app.services.adk_agent import AgentExecutionError, agent_service
from app.services.benefit_rag import benefit_rag_service
from app.services.brand_matcher import brand_matches_store
from app.services.coupon_parser import parse_coupon_placeholder
from app.services.coupon_registry import coupon_registry
from app.services.public_store_client import public_store_client
from app.services.recommendation import RecommendationUnavailableError, build_recommendation

router = APIRouter(prefix="/api")


@router.get("/benefits/status")
def get_benefit_rag_status() -> dict:
    try:
        return benefit_rag_service.status()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"RAG 저장소를 확인할 수 없습니다: {type(error).__name__}",
        ) from error


@router.get("/benefits/search")
def search_official_benefits(
    canonical_brand: str,
    card_product: str,
    merchant_category: str = "",
    limit: int = 3,
) -> dict:
    if not 1 <= limit <= 5:
        raise HTTPException(status_code=422, detail="limit must be between 1 and 5")
    try:
        return benefit_rag_service.search(
            canonical_brand=canonical_brand,
            card_product=card_product,
            merchant_category=merchant_category,
            limit=limit,
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"RAG 검색에 실패했습니다: {type(error).__name__}",
        ) from error


@router.post("/coupons/parse", response_model=Coupon)
def parse_coupon(request: CouponParseRequest) -> Coupon:
    return parse_coupon_placeholder(request.sanitized_raw_text)


@router.post("/coupons", response_model=RegisteredCoupon, status_code=status.HTTP_201_CREATED)
def create_coupon(request: CouponCreateRequest) -> RegisteredCoupon:
    return coupon_registry.create(request)


@router.get("/coupons", response_model=list[RegisteredCoupon])
def list_coupons(user_id: str) -> list[RegisteredCoupon]:
    return coupon_registry.list_for_user(user_id)


@router.get("/stores/nearby", response_model=NearbyStoresResponse)
def list_nearby_stores(
    latitude: float,
    longitude: float,
    user_id: str = "demo-user",
    radius_m: int = 1000,
    limit: int = 5,
) -> NearbyStoresResponse:
    if not user_id.strip() or len(user_id) > 128:
        raise HTTPException(status_code=422, detail="invalid user_id")
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise HTTPException(status_code=422, detail="invalid coordinates")
    if not 100 <= radius_m <= 5000:
        raise HTTPException(status_code=422, detail="radius_m must be between 100 and 5000")
    if not 1 <= limit <= 20:
        raise HTTPException(status_code=422, detail="limit must be between 1 and 20")

    today = datetime.now(UTC).date()
    active_coupons = [
        coupon for coupon in coupon_registry.list_for_user(user_id) if coupon.expiry_date >= today
    ]
    response = public_store_client.nearby(latitude, longitude, radius_m)
    eligible_stores = [
        store
        for store in response.stores
        if any(brand_matches_store(coupon.brand, store.name) for coupon in active_coupons)
    ]
    closest = sorted(eligible_stores, key=lambda store: store.distance_m)[:limit]

    notice = response.notice
    if notice is None and not active_coupons:
        notice = "유효한 등록 쿠폰이 없어 표시할 매장이 없습니다."
    elif notice is None and not closest:
        notice = "반경 안에 등록 쿠폰을 사용할 수 있는 매장이 없습니다."
    return response.model_copy(update={"stores": closest, "notice": notice})


@router.post("/recommendations", response_model=RecommendationResponse)
def create_recommendation(request: RecommendationRequest) -> RecommendationResponse:
    try:
        return build_recommendation(request)
    except RecommendationUnavailableError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.get("/agent", response_model=AgentInfoResponse)
def get_agent_info() -> AgentInfoResponse:
    return AgentInfoResponse(
        agent_name=root_agent.name,
        model=settings.gemini_model,
        framework="Google ADK 2.6.3",
        tools=AGENT_TOOL_NAMES,
        run_endpoint="POST /api/agent/recommendations",
    )


@router.post("/agent/recommendations", response_model=AgentRecommendationResponse)
async def run_recommendation_agent(
    request: AgentRecommendationRequest,
) -> AgentRecommendationResponse:
    try:
        return await agent_service.run(request)
    except AgentExecutionError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error
