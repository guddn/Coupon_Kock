from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class CouponParseRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=128)
    sanitized_raw_text: str = Field(min_length=1, max_length=10_000)

    @field_validator("sanitized_raw_text")
    @classmethod
    def reject_probable_unmasked_codes(cls, value: str) -> str:
        compact_tokens = value.replace("-", " ").split()
        if any(token.isdigit() and len(token) >= 12 for token in compact_tokens):
            raise ValueError("probable coupon code is not masked")
        return value


class Coupon(BaseModel):
    coupon_id: str | None = None
    brand: str | None = None
    product_name: str | None = None
    coupon_type: Literal["fixed", "product", "unknown"] = "unknown"
    face_value: int | None = Field(default=None, ge=0)
    expiry_date: date | None = None
    confidence: float = Field(ge=0, le=1)
    needs_review: bool


class Store(BaseModel):
    store_id: str
    name: str
    canonical_brand: str | None = None
    distance_m: float = Field(ge=0)


class BenefitSource(BaseModel):
    source_id: str
    title: str
    url: str
    valid_from: date | None = None
    valid_to: date | None = None


class PriceComponent(BaseModel):
    kind: Literal["coupon", "card", "telecom"]
    name: str
    discount_amount: int = Field(ge=0)
    source_id: str | None = None


class RecommendationOption(BaseModel):
    option_id: str
    final_price: int = Field(ge=0)
    saving: int = Field(ge=0)
    components: list[PriceComponent] = Field(default_factory=list)


class RecommendationRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=128)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    purchase_amount: int = Field(default=10_000, ge=0, le=10_000_000)
    store_id: str | None = Field(default=None, max_length=256)


class RecommendationResponse(BaseModel):
    request_id: str
    store: Store
    candidate_options: list[RecommendationOption]
    recommended_option: RecommendationOption
    conditions_to_check: list[str] = Field(default_factory=list)
    sources: list[BenefitSource] = Field(default_factory=list)
    message: str


class AgentRecommendationRequest(RecommendationRequest):
    """Structured input converted to a single ADK user turn."""


class AgentRecommendationResponse(BaseModel):
    request_id: str
    session_id: str
    agent_name: str
    model: str
    answer: str
    tool_trace: list[str] = Field(default_factory=list)
    session_persistence: Literal["ephemeral"] = "ephemeral"


class AgentInfoResponse(BaseModel):
    agent_name: str
    model: str
    framework: str
    tools: list[str]
    run_endpoint: str
    session_persistence: Literal["ephemeral"] = "ephemeral"
