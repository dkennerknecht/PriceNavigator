from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Product


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    lowered = value.lower().strip()
    lowered = re.sub(r"[^a-z0-9]+", " ", lowered)
    return re.sub(r"\s+", " ", lowered).strip()


def normalize_identifier(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"[^a-zA-Z0-9]+", "", value).upper()


def build_search_tokens(parts: Iterable[str | None], attributes: dict[str, Any]) -> str:
    tokens = [normalize_text(part) for part in parts if part]
    tokens.extend(normalize_text(str(value)) for value in attributes.values())
    unique = sorted({token for token in tokens if token})
    return " ".join(unique)


def build_title_attr_signature(
    manufacturer: str | None,
    canonical_title: str | None,
    attributes_json: dict[str, Any] | None,
) -> str:
    attrs = attributes_json or {}
    relevant_parts = [normalize_text(manufacturer), normalize_text(canonical_title)]
    for key in sorted(attrs):
        relevant_parts.append(f"{normalize_text(key)}={normalize_text(str(attrs[key]))}")
    return "|".join(part for part in relevant_parts if part)


def build_fingerprint(payload: dict[str, Any]) -> str:
    ean = normalize_identifier(payload.get("ean_gtin"))
    if ean:
        return f"ean:{ean}"

    manufacturer = normalize_text(payload.get("manufacturer"))
    mpn = normalize_identifier(payload.get("mpn"))
    if manufacturer and mpn:
        return f"mpn:{manufacturer}:{mpn}"

    return f"title:{build_title_attr_signature(payload.get('manufacturer'), payload.get('canonical_title'), payload.get('attributes_json', {}))}"


def prepare_product_payload(payload: dict[str, Any]) -> dict[str, Any]:
    attributes = payload.get("attributes_json") or {}
    prepared = {**payload, "attributes_json": attributes}
    prepared["search_tokens"] = build_search_tokens(
        [
            prepared.get("canonical_title"),
            prepared.get("manufacturer"),
            prepared.get("brand"),
            prepared.get("mpn"),
            prepared.get("ean_gtin"),
            prepared.get("category"),
        ],
        attributes,
    )
    prepared["fingerprint"] = build_fingerprint(prepared)
    return prepared


def find_existing_product(
    session: Session, candidate: dict[str, Any]
) -> tuple[Product | None, str]:
    ean = normalize_identifier(candidate.get("ean_gtin"))
    if ean:
        statement = select(Product).where(Product.ean_gtin == candidate.get("ean_gtin"))
        product = session.scalar(statement)
        if product is not None:
            return product, "ean"

    manufacturer = normalize_text(candidate.get("manufacturer"))
    mpn = normalize_identifier(candidate.get("mpn"))
    if manufacturer and mpn:
        statement = select(Product).where(Product.mpn.is_not(None))
        for product in session.scalars(statement):
            if (
                normalize_text(product.manufacturer) == manufacturer
                and normalize_identifier(product.mpn) == mpn
            ):
                return product, "manufacturer_mpn"

    title_signature = build_title_attr_signature(
        candidate.get("manufacturer"),
        candidate.get("canonical_title"),
        candidate.get("attributes_json"),
    )
    if title_signature:
        statement = select(Product).where(Product.manufacturer.is_not(None))
        for product in session.scalars(statement):
            candidate_signature = build_title_attr_signature(
                product.manufacturer,
                product.canonical_title,
                product.attributes_json,
            )
            if candidate_signature == title_signature:
                return product, "manufacturer_title_attributes"

    return None, "manual_review"
