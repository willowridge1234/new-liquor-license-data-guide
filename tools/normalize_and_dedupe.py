#!/usr/bin/env python3
"""Normalize a canonical liquor-license CSV and remove deterministic duplicates."""

from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from pathlib import Path


REQUIRED = {
    "record_type", "jurisdiction", "license_id", "application_id", "license_type",
    "status", "legal_name", "trade_name", "address", "city", "region", "postal_code",
    "event_date", "source_url", "retrieved_at",
}


def comparison_key(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").casefold()
    value = value.replace("&", " and ")
    return " ".join(re.sub(r"[^\w]+", " ", value).split())


def identifier_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", unicodedata.normalize("NFKC", value or "").casefold())


def dedupe_key(row: dict[str, str]) -> str:
    jurisdiction = comparison_key(row["jurisdiction"])
    application_id = identifier_key(row["application_id"])
    license_id = identifier_key(row["license_id"])
    record_type = comparison_key(row["record_type"])
    name = comparison_key(row["trade_name"] or row["legal_name"])
    address = address_key(row)
    if application_id:
        return f"application:{jurisdiction}:{application_id}"
    if license_id:
        return f"license:{jurisdiction}:{license_id}:{record_type}"
    return f"premises:{jurisdiction}:{name}:{address}:{record_type}"


def address_key(row: dict[str, str]) -> str:
    return comparison_key(" ".join([
        row["address"], row["city"], row["region"], row["postal_code"]
    ]))


def normalize_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in rows:
        normalized = dict(row)
        normalized["name_key"] = comparison_key(row["trade_name"] or row["legal_name"])
        normalized["address_key"] = address_key(row)
        normalized["dedupe_key"] = dedupe_key(row)
        if normalized["dedupe_key"] in seen:
            continue
        seen.add(normalized["dedupe_key"])
        output.append(normalized)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    args = parser.parse_args()

    with args.input_csv.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        fields = set(reader.fieldnames or [])
        missing = sorted(REQUIRED - fields)
        if missing:
            parser.error(f"missing required columns: {', '.join(missing)}")
        rows = list(reader)

    normalized = normalize_rows(rows)
    fieldnames = list(reader.fieldnames or []) + ["name_key", "address_key", "dedupe_key"]
    with args.output_csv.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(normalized)

    print(f"wrote {len(normalized)} unique rows from {len(rows)} input rows")


if __name__ == "__main__":
    main()
