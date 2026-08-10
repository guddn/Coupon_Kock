from fastapi.testclient import TestClient

from app.api.router import agent_service
from app.main import app
from app.models.schemas import AgentRecommendationResponse


def test_agent_info_endpoint() -> None:
    response = TestClient(app).get("/api/agent")

    assert response.status_code == 200
    assert response.json()["agent_name"] == "coupon_kock_agent"
    assert response.json()["run_endpoint"] == "POST /api/agent/recommendations"


def test_agent_run_endpoint(monkeypatch) -> None:
    async def fake_run(_request):
        return AgentRecommendationResponse(
            request_id="request-1",
            session_id="session-1",
            agent_name="coupon_kock_agent",
            model="gemini-2.5-flash",
            answer="예상 결제금액은 4,500원입니다.",
            tool_trace=["calculate_discount_options:completed"],
        )

    monkeypatch.setattr(agent_service, "run", fake_run)
    response = TestClient(app).post(
        "/api/agent/recommendations",
        json={
            "user_id": "demo-user",
            "latitude": 37.2822,
            "longitude": 127.0437,
            "purchase_amount": 10_000,
            "store_id": "demo-store",
        },
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "예상 결제금액은 4,500원입니다."
    assert response.json()["session_persistence"] == "ephemeral"
