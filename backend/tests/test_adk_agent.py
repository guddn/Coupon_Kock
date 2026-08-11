from datetime import date

from app.agents.coupon_kock_agent import root_agent
from app.agents.coupon_kock_agent import tools as agent_tools
from app.agents.coupon_kock_agent.agent import AGENT_TOOL_NAMES
from app.agents.coupon_kock_agent.tools import (
    calculate_discount_options,
    load_user_benefit_context,
    match_nearby_store,
    retrieve_official_benefit_rules,
)
from app.models.schemas import CouponCreateRequest, NearbyStore, NearbyStoresResponse
from app.services.coupon_registry import MemoryCouponRegistry


class FakeStoreClient:
    def nearby(self, latitude: float, longitude: float, radius_m: int) -> NearbyStoresResponse:
        return NearbyStoresResponse(
            data_source="public_data",
            stores=[
                NearbyStore(
                    store_id="store-1",
                    name="스타카페 아주대점",
                    category="카페",
                    address="경기도 수원시",
                    latitude=latitude + 0.0001,
                    longitude=longitude + 0.0001,
                    distance_m=15,
                )
            ],
        )


def test_root_agent_exposes_expected_tools() -> None:
    assert root_agent.name == "coupon_kock_agent"
    assert AGENT_TOOL_NAMES == [
        "match_nearby_store",
        "load_user_benefit_context",
        "retrieve_official_benefit_rules",
        "calculate_discount_options",
    ]


def test_agent_tools_produce_deterministic_recommendation(monkeypatch) -> None:
    registry = MemoryCouponRegistry()
    registry.create(
        CouponCreateRequest(
            user_id="demo-user",
            brand="스타카페",
            product_name="모바일 금액권",
            coupon_type="fixed",
            face_value=5_000,
            expiry_date=date(2099, 12, 31),
        )
    )
    monkeypatch.setattr(agent_tools, "public_store_client", FakeStoreClient())
    monkeypatch.setattr(agent_tools, "coupon_registry", registry)

    store_result = match_nearby_store(37.2822, 127.0437, "store-1")
    assert store_result["status"] == "success"
    assert store_result["store"]["canonical_brand"] == "스타카페 아주대점"

    user_context = load_user_benefit_context("demo-user", "스타카페 아주대점")
    rules = retrieve_official_benefit_rules("스타카페 아주대점")
    result = calculate_discount_options(
        purchase_amount=10_000,
        coupon_face_value=user_context["coupons"][0]["face_value"],
    )

    assert rules["status"] == "no_evidence"
    assert result["status"] == "success"
    assert result["recommended_option"]["option_id"] == "coupon-only"
    assert result["recommended_option"]["final_price"] == 5_000


def test_store_tool_does_not_echo_exact_location(monkeypatch) -> None:
    monkeypatch.setattr(agent_tools, "public_store_client", FakeStoreClient())
    result = match_nearby_store(37.2822, 127.0437)
    assert "latitude" not in result["store"]
    assert "longitude" not in result["store"]
