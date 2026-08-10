from app.agents.coupon_kock_agent import root_agent
from app.agents.coupon_kock_agent.agent import AGENT_TOOL_NAMES
from app.agents.coupon_kock_agent.tools import (
    calculate_discount_options,
    load_user_benefit_context,
    match_nearby_store,
    retrieve_official_benefit_rules,
)


def test_root_agent_exposes_expected_tools() -> None:
    assert root_agent.name == "coupon_kock_agent"
    assert AGENT_TOOL_NAMES == [
        "match_nearby_store",
        "load_user_benefit_context",
        "retrieve_official_benefit_rules",
        "calculate_discount_options",
    ]


def test_agent_tools_produce_deterministic_recommendation() -> None:
    store_result = match_nearby_store(37.2822, 127.0437, "demo-store")
    assert store_result["status"] == "success"
    assert store_result["store"]["canonical_brand"] == "스타카페"

    user_context = load_user_benefit_context("demo-user", "스타카페")
    rules = retrieve_official_benefit_rules("스타카페", "데모 카드")
    result = calculate_discount_options(
        purchase_amount=10_000,
        coupon_face_value=user_context["coupons"][0]["face_value"],
        card_discount_percent=rules["rules"][0]["value"],
        card_max_discount=rules["rules"][0]["max_discount"],
        card_stackable_with_coupon=rules["rules"][0]["stackable_with_coupon"],
        card_source_id=rules["rules"][0]["source_id"],
    )

    assert result["status"] == "success"
    assert result["recommended_option"]["option_id"] == "coupon-card"
    assert result["recommended_option"]["final_price"] == 4_500


def test_store_tool_does_not_echo_exact_location() -> None:
    result = match_nearby_store(37.2822, 127.0437)
    assert "latitude" not in result["store"]
    assert "longitude" not in result["store"]
