from app.services.calculator import DiscountRule, calculate_option, rank_options


def test_fixed_coupon_then_capped_percentage_discount() -> None:
    coupon = DiscountRule("coupon", "쿠폰", "coupon", "fixed", 5_000)
    card = DiscountRule("card", "카드", "card", "percentage", 10, max_discount=1_000)

    option = calculate_option(10_000, [coupon, card], "combined")

    assert option.final_price == 4_500
    assert option.saving == 5_500


def test_minimum_purchase_is_evaluated_at_application_time() -> None:
    rule = DiscountRule("card", "카드", "card", "fixed", 1_000, min_purchase=20_000)
    option = calculate_option(10_000, [rule], "card")
    assert option.final_price == 10_000


def test_rank_options_is_deterministic() -> None:
    first = calculate_option(10_000, [], "b")
    second = calculate_option(10_000, [], "a")
    assert [item.option_id for item in rank_options([first, second])] == ["a", "b"]
