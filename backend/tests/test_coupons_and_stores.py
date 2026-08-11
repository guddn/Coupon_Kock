from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_register_and_list_coupon() -> None:
    user_id = "coupon-api-test-user"
    created = client.post(
        "/api/coupons",
        json={
            "user_id": user_id,
            "brand": "스타카페",
            "product_name": "모바일 금액권",
            "coupon_type": "fixed",
            "face_value": 5_000,
            "expiry_date": "2027-12-31",
        },
    )
    assert created.status_code == 201
    assert created.json()["brand"] == "스타카페"

    listed = client.get("/api/coupons", params={"user_id": user_id})
    assert listed.status_code == 200
    assert any(item["coupon_id"] == created.json()["coupon_id"] for item in listed.json())


def test_nearby_stores_falls_back_to_fixture_without_service_key() -> None:
    response = client.get(
        "/api/stores/nearby",
        params={"latitude": 37.2822, "longitude": 127.0437, "radius_m": 1000},
    )
    assert response.status_code == 200
    assert response.json()["data_source"] == "fixture"
    assert len(response.json()["stores"]) == 3
    assert response.json()["stores"][0]["distance_m"] >= 0


def test_nearby_stores_rejects_excessive_radius() -> None:
    response = client.get(
        "/api/stores/nearby",
        params={"latitude": 37.2822, "longitude": 127.0437, "radius_m": 10_000},
    )
    assert response.status_code == 422


def test_recommendation_uses_registered_matching_coupon() -> None:
    user_id = "recommendation-integration-user"
    created = client.post(
        "/api/coupons",
        json={
            "user_id": user_id,
            "brand": "쿠폰콕",
            "product_name": "카페 금액권",
            "coupon_type": "fixed",
            "face_value": 4_000,
            "expiry_date": "2099-12-31",
        },
    )
    assert created.status_code == 201

    response = client.post(
        "/api/recommendations",
        json={
            "user_id": user_id,
            "latitude": 37.2822,
            "longitude": 127.0437,
            "purchase_amount": 10_000,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["store"]["store_id"] == "fixture-cafe"
    assert payload["recommended_option"]["final_price"] == 6_000
    assert payload["recommended_option"]["components"][0]["kind"] == "coupon"
    assert payload["sources"] == []
