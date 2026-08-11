import re


def normalize_brand(value: str) -> str:
    """Normalize a Korean/Latin merchant label for conservative substring matching."""
    return re.sub(r"[^0-9a-z가-힣]", "", value.casefold())


def brand_matches_store(brand: str, store_name: str) -> bool:
    normalized_brand = normalize_brand(brand)
    normalized_store = normalize_brand(store_name)
    if len(normalized_brand) < 2 or len(normalized_store) < 2:
        return False
    return normalized_brand in normalized_store or normalized_store in normalized_brand
