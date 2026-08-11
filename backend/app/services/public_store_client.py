import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import unquote, urlencode
from urllib.request import urlopen

from app.core.config import settings
from app.models.schemas import NearbyStore, NearbyStoresResponse
from app.services.store_matcher import haversine_distance_m


@dataclass(frozen=True)
class PublicStoreClient:
    service_key: str
    endpoint: str
    timeout_seconds: float

    def nearby(self, latitude: float, longitude: float, radius_m: int) -> NearbyStoresResponse:
        if not self.service_key:
            return _fixture_response(
                latitude, longitude, "공공데이터 API 키가 없어 샘플 매장을 표시합니다."
            )

        query = urlencode(
            {
                "serviceKey": unquote(self.service_key),
                "pageNo": 1,
                "numOfRows": 100,
                "radius": radius_m,
                "cx": longitude,
                "cy": latitude,
                "type": "json",
            }
        )
        try:
            with urlopen(f"{self.endpoint}?{query}", timeout=self.timeout_seconds) as response:
                payload = json.load(response)
            stores = _parse_stores(payload, latitude, longitude, radius_m)
            return NearbyStoresResponse(data_source="public_data", stores=stores)
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
            return _fixture_response(
                latitude, longitude, "공공데이터 호출에 실패해 샘플 매장을 표시합니다."
            )


def _parse_stores(
    payload: dict[str, Any], latitude: float, longitude: float, radius_m: int
) -> list[NearbyStore]:
    items: Any = payload.get("body", {}).get("items", [])
    if isinstance(items, dict):
        items = items.get("item", items.get("items", []))
    if isinstance(items, dict):
        items = [items]
    if not isinstance(items, list):
        return []

    stores: list[NearbyStore] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        try:
            store_latitude = float(item["lat"])
            store_longitude = float(item["lon"])
        except (KeyError, TypeError, ValueError):
            continue
        distance = haversine_distance_m(latitude, longitude, store_latitude, store_longitude)
        if distance > radius_m:
            continue
        stores.append(
            NearbyStore(
                store_id=str(item.get("bizesId") or f"public-{len(stores)}"),
                name=str(item.get("bizesNm") or "이름 없는 매장"),
                category=str(
                    item.get("indsSclsNm")
                    or item.get("indsMclsNm")
                    or item.get("indsLclsNm")
                    or "기타"
                ),
                address=str(item.get("rdnmAdr") or item.get("lnoAdr") or "주소 정보 없음"),
                latitude=store_latitude,
                longitude=store_longitude,
                distance_m=round(distance, 1),
            )
        )
    return sorted(stores, key=lambda store: store.distance_m)


def _fixture_response(latitude: float, longitude: float, notice: str) -> NearbyStoresResponse:
    fixtures = (
        ("fixture-cafe", "쿠폰콕 카페", "카페", "현재 위치 북동쪽", 0.00045, 0.00035),
        ("fixture-store", "쿠폰콕 편의점", "편의점", "현재 위치 서쪽", 0.00010, -0.00055),
        ("fixture-food", "쿠폰콕 식당", "음식점", "현재 위치 남동쪽", -0.00050, 0.00030),
    )
    stores = []
    for store_id, name, category, address, lat_offset, lon_offset in fixtures:
        store_latitude = latitude + lat_offset
        store_longitude = longitude + lon_offset
        stores.append(
            NearbyStore(
                store_id=store_id,
                name=name,
                category=category,
                address=address,
                latitude=store_latitude,
                longitude=store_longitude,
                distance_m=round(
                    haversine_distance_m(latitude, longitude, store_latitude, store_longitude), 1
                ),
            )
        )
    return NearbyStoresResponse(data_source="fixture", stores=stores, notice=notice)


public_store_client = PublicStoreClient(
    service_key=settings.public_data_service_key,
    endpoint=settings.public_data_store_url,
    timeout_seconds=settings.public_data_timeout_seconds,
)
