from dataclasses import dataclass
from decimal import ROUND_DOWN, Decimal
from typing import Literal

from app.models.schemas import PriceComponent, RecommendationOption


@dataclass(frozen=True)
class DiscountRule:
    rule_id: str
    name: str
    kind: Literal["coupon", "card", "telecom"]
    discount_type: Literal["fixed", "percentage"]
    value: int
    min_purchase: int = 0
    max_discount: int | None = None
    source_id: str | None = None
    stackable: bool = True


def _discount_amount(price: int, rule: DiscountRule) -> int:
    if price < rule.min_purchase:
        return 0
    if rule.discount_type == "fixed":
        amount = rule.value
    else:
        amount = int(
            (Decimal(price) * Decimal(rule.value) / Decimal(100)).quantize(
                Decimal(1), rounding=ROUND_DOWN
            )
        )
    if rule.max_discount is not None:
        amount = min(amount, rule.max_discount)
    return min(price, max(0, amount))


def calculate_option(
    purchase_amount: int, rules: list[DiscountRule], option_id: str
) -> RecommendationOption:
    price = purchase_amount
    components: list[PriceComponent] = []
    for rule in rules:
        amount = _discount_amount(price, rule)
        if amount == 0:
            continue
        price -= amount
        components.append(
            PriceComponent(
                kind=rule.kind,
                name=rule.name,
                discount_amount=amount,
                source_id=rule.source_id,
            )
        )
    return RecommendationOption(
        option_id=option_id,
        final_price=price,
        saving=purchase_amount - price,
        components=components,
    )


def rank_options(options: list[RecommendationOption]) -> list[RecommendationOption]:
    return sorted(options, key=lambda option: (option.final_price, option.option_id))
