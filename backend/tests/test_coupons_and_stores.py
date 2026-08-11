from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _register_active_coupon(user_id: str, brand: str = "쿠폰콕") -> None:
    response = client.post(
        "/api/coupons",
        json={
            "user_id": user_id,
            "brand": brand,
            "product_name": "테스트 금액권",
            "coupon_type": "fixed",
            "face_value": 1_000,
            "expiry_date": "2099-12-31",
        },
    )
    assert response.status_code == 201


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
    user_id = "nearby-fixture-user"
    _register_active_coupon(user_id)
    response = client.get(
        "/api/stores/nearby",
        params={
            "user_id": user_id,
            "latitude": 37.2822,
            "longitude": 127.0437,
            "radius_m": 1000,
        },
    )
    assert response.status_code == 200
    assert response.json()["data_source"] == "fixture"
    stores = response.json()["stores"]
    assert len(stores) == 5
    assert stores[0]["distance_m"] >= 0
    assert [store["distance_m"] for store in stores] == sorted(
        store["distance_m"] for store in stores
    )


def test_nearby_stores_rejects_excessive_radius() -> None:
    response = client.get(
        "/api/stores/nearby",
        params={
            "user_id": "radius-test-user",
            "latitude": 37.2822,
            "longitude": 127.0437,
            "radius_m": 10_000,
        },
    )
    assert response.status_code == 422


def test_nearby_stores_supports_smaller_limit() -> None:
    user_id = "nearby-limit-user"
    _register_active_coupon(user_id)
    response = client.get(
        "/api/stores/nearby",
        params={
            "user_id": user_id,
            "latitude": 37.2822,
            "longitude": 127.0437,
            "radius_m": 1000,
            "limit": 2,
        },
    )
    assert response.status_code == 200
    assert len(response.json()["stores"]) == 2


def test_nearby_stores_excludes_stores_without_registered_coupon() -> None:
    response = client.get(
        "/api/stores/nearby",
        params={
            "user_id": "user-without-coupons",
            "latitude": 37.2822,
            "longitude": 127.0437,
            "radius_m": 1000,
        },
    )

    assert response.status_code == 200
    assert response.json()["stores"] == []


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
