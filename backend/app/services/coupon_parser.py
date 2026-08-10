import re
from datetime import date

from app.models.schemas import Coupon

DATE_PATTERN = re.compile(r"(20\d{2})[./-](\d{1,2})[./-](\d{1,2})")
AMOUNT_PATTERN = re.compile(r"(\d{1,3}(?:,\d{3})+)\s*원")


def parse_coupon_placeholder(text: str) -> Coupon:
    """Safe local placeholder. Replace with a Vertex AI structured-output adapter."""
    date_match = DATE_PATTERN.search(text)
    amount_match = AMOUNT_PATTERN.search(text)
    expiry = None
    if date_match:
        try:
            expiry = date(*(int(part) for part in date_match.groups()))
        except ValueError:
            expiry = None
    face_value = int(amount_match.group(1).replace(",", "")) if amount_match else None
    return Coupon(
        coupon_type="fixed" if face_value is not None else "unknown",
        face_value=face_value,
        expiry_date=expiry,
        confidence=0.35,
        needs_review=True,
    )
