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
from app.services.coupon_parser import parse_coupon_placeholder
from app.services.coupon_registry import coupon_registry
from app.services.public_store_client import public_store_client
from app.services.recommendation import RecommendationUnavailableError, build_recommendation

router = APIRouter(prefix="/api")


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
    radius_m: int = 1000,
    limit: int = 5,
) -> NearbyStoresResponse:
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise HTTPException(status_code=422, detail="invalid coordinates")
    if not 100 <= radius_m <= 5000:
        raise HTTPException(status_code=422, detail="radius_m must be between 100 and 5000")
    if not 1 <= limit <= 20:
        raise HTTPException(status_code=422, detail="limit must be between 1 and 20")
    response = public_store_client.nearby(latitude, longitude, radius_m)
    closest = sorted(response.stores, key=lambda store: store.distance_m)[:limit]
    return response.model_copy(update={"stores": closest})


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
