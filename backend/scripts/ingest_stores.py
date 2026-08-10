import csv
import json
import re
import unicodedata
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path

FIELD_ALIASES = {
    "name": ("상호명", "상호명칭"),
    "category_code": ("상권업종중분류코드", "상권업종소분류코드"),
    "category_name": ("상권업종소분류명", "상권업종중분류명"),
    "road_address": ("도로명주소",),
    "longitude": ("경도", "lon"),
    "latitude": ("위도", "lat"),
    "source_key": ("상가업소번호",),
}


def pick(row: dict[str, str], logical_name: str) -> str:
    for candidate in FIELD_ALIASES[logical_name]:
        if candidate in row and row[candidate] is not None:
            return row[candidate].strip()
    return ""


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).lower()
    normalized = re.sub(r"\([^)]*\)", " ", normalized)
    normalized = re.sub(r"[^0-9a-z가-힣]+", " ", normalized)
    return " ".join(normalized.split())


def stable_store_id(name: str, address: str, latitude: float, longitude: float) -> str:
    raw = f"{name}|{address}|{latitude:.6f}|{longitude:.6f}".encode()
    return sha256(raw).hexdigest()[:24]


def transform(row: dict[str, str]) -> dict[str, object] | None:
    name = pick(row, "name")
    address = pick(row, "road_address")
    try:
        latitude = float(pick(row, "latitude"))
        longitude = float(pick(row, "longitude"))
    except ValueError:
        return None
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return None
    return {
        "store_id": stable_store_id(name, address, latitude, longitude),
        "store_name": name,
        "normalized_name": normalize_text(name),
        "category_code": pick(row, "category_code"),
        "category_name": pick(row, "category_name"),
        "road_address": address,
        "latitude": latitude,
        "longitude": longitude,
        "canonical_brand": None,
        "brand_match_confidence": 0,
        "source": "data-go-kr-15083033",
        "source_key": pick(row, "source_key"),
    }


def main() -> None:
    parser = ArgumentParser(description="Normalize public store CSV into JSONL")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--encoding", default="utf-8-sig")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with (
        args.input.open("r", encoding=args.encoding, newline="") as source,
        args.output.open("w", encoding="utf-8", newline="") as destination,
    ):
        for row in csv.DictReader(source):
            record = transform(row)
            if record is None:
                continue
            destination.write(json.dumps(record, ensure_ascii=False) + "\n")
            written += 1
            if args.limit and written >= args.limit:
                break
    print(f"wrote {written} records to {args.output}")


if __name__ == "__main__":
    main()
