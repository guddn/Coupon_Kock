from datetime import UTC, datetime
from threading import Lock
from typing import Protocol
from uuid import uuid4

from app.core.config import settings
from app.models.schemas import CouponCreateRequest, RegisteredCoupon


class CouponRegistry(Protocol):
    def create(self, request: CouponCreateRequest) -> RegisteredCoupon: ...

    def list_for_user(self, user_id: str) -> list[RegisteredCoupon]: ...


class MemoryCouponRegistry:
    """Local/test adapter. Cloud Run should use the Firestore adapter."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._coupons: dict[str, RegisteredCoupon] = {}

    def create(self, request: CouponCreateRequest) -> RegisteredCoupon:
        coupon = RegisteredCoupon(
            coupon_id=f"coupon-{uuid4().hex}",
            user_id=request.user_id,
            brand=request.brand.strip(),
            product_name=request.product_name.strip(),
            coupon_type=request.coupon_type,
            face_value=request.face_value,
            expiry_date=request.expiry_date,
            created_at=datetime.now(UTC),
        )
        with self._lock:
            self._coupons[coupon.coupon_id] = coupon
        return coupon

    def list_for_user(self, user_id: str) -> list[RegisteredCoupon]:
        with self._lock:
            coupons = [coupon for coupon in self._coupons.values() if coupon.user_id == user_id]
        return sorted(coupons, key=lambda coupon: (coupon.expiry_date, coupon.created_at))


class FirestoreCouponRegistry:
    def __init__(self) -> None:
        from google.cloud import firestore

        self._collection = firestore.Client(
            project=settings.gcp_project_id or None,
            database=settings.firestore_database,
        ).collection("coupons")

    def create(self, request: CouponCreateRequest) -> RegisteredCoupon:
        coupon = RegisteredCoupon(
            coupon_id=f"coupon-{uuid4().hex}",
            user_id=request.user_id,
            brand=request.brand.strip(),
            product_name=request.product_name.strip(),
            coupon_type=request.coupon_type,
            face_value=request.face_value,
            expiry_date=request.expiry_date,
            created_at=datetime.now(UTC),
        )
        self._collection.document(coupon.coupon_id).set(coupon.model_dump(mode="json"))
        return coupon

    def list_for_user(self, user_id: str) -> list[RegisteredCoupon]:
        from google.cloud.firestore_v1.base_query import FieldFilter

        snapshots = self._collection.where(filter=FieldFilter("user_id", "==", user_id)).stream()
        coupons = [RegisteredCoupon.model_validate(snapshot.to_dict()) for snapshot in snapshots]
        return sorted(coupons, key=lambda coupon: (coupon.expiry_date, coupon.created_at))


def _build_registry() -> CouponRegistry:
    if settings.coupon_storage_backend == "firestore":
        return FirestoreCouponRegistry()
    return MemoryCouponRegistry()


coupon_registry = _build_registry()
