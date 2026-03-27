from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from sqlalchemy.orm import Session

from app.models.entities import ProductSource
from app.services.catalog import CATALOG_PRODUCTS
from app.services.product_matching import find_existing_product, prepare_product_payload


class ProductResolver(Protocol):
    source_type: str

    def supports(self, payload: dict) -> bool: ...

    def resolve(self, payload: dict) -> dict | None: ...


def _catalog_product_payload(catalog_product) -> dict:
    return {
        "canonical_title": catalog_product.canonical_title,
        "manufacturer": catalog_product.manufacturer,
        "brand": catalog_product.brand,
        "mpn": catalog_product.mpn,
        "ean_gtin": catalog_product.ean_gtin,
        "category": catalog_product.category,
        "description_short": catalog_product.description_short,
        "attributes_json": catalog_product.attributes_json,
        "datasheet_url": catalog_product.datasheet_url,
        "image_url": catalog_product.image_url,
    }


class MockUrlResolver:
    source_type = "url"

    def supports(self, payload: dict) -> bool:
        return bool(payload.get("url"))

    def resolve(self, payload: dict) -> dict | None:
        url = payload.get("url")
        for catalog_product in CATALOG_PRODUCTS:
            if catalog_product.source_url == url:
                return {
                    **_catalog_product_payload(catalog_product),
                    "confidence": 0.95,
                    "source_value": url,
                    "raw_title": catalog_product.canonical_title,
                    "resolved_url": url,
                    "raw_payload_json": {"resolver": "mock_url", "url": url},
                }
        return None


class MockManufacturerMpnResolver:
    source_type = "manufacturer_mpn"

    def supports(self, payload: dict) -> bool:
        return bool(payload.get("manufacturer") and payload.get("mpn"))

    def resolve(self, payload: dict) -> dict | None:
        manufacturer = (payload.get("manufacturer") or "").strip().lower()
        mpn = (payload.get("mpn") or "").strip().upper()
        for catalog_product in CATALOG_PRODUCTS:
            if (
                catalog_product.manufacturer.lower() == manufacturer
                and catalog_product.mpn.upper() == mpn
            ):
                return {
                    **_catalog_product_payload(catalog_product),
                    "confidence": 0.98,
                    "source_value": f"{catalog_product.manufacturer}:{catalog_product.mpn}",
                    "raw_title": catalog_product.canonical_title,
                    "resolved_url": catalog_product.source_url,
                    "raw_payload_json": {
                        "resolver": "mock_manufacturer_mpn",
                        "mpn": catalog_product.mpn,
                    },
                }
        return None


class MockEanResolver:
    source_type = "ean"

    def supports(self, payload: dict) -> bool:
        return bool(payload.get("ean_gtin"))

    def resolve(self, payload: dict) -> dict | None:
        ean = (payload.get("ean_gtin") or "").strip()
        for catalog_product in CATALOG_PRODUCTS:
            if catalog_product.ean_gtin == ean:
                return {
                    **_catalog_product_payload(catalog_product),
                    "confidence": 0.99,
                    "source_value": ean,
                    "raw_title": catalog_product.canonical_title,
                    "resolved_url": catalog_product.source_url,
                    "raw_payload_json": {"resolver": "mock_ean", "ean": ean},
                }
        return None


@dataclass
class ResolutionResult:
    candidate: dict
    source_id: int
    resolver_type: str
    match_strategy: str
    confidence: float
    matched_product_id: int | None
    requires_manual_review: bool


class ProductResolutionService:
    def __init__(self, resolvers: list[ProductResolver] | None = None) -> None:
        self.resolvers = resolvers or [
            MockEanResolver(),
            MockManufacturerMpnResolver(),
            MockUrlResolver(),
        ]

    def resolve(self, session: Session, payload: dict) -> ResolutionResult:
        resolved_candidate = None
        resolver_source_type = "manual"
        resolver_found_candidate = False
        for resolver in self.resolvers:
            if resolver.supports(payload):
                resolved_candidate = resolver.resolve(payload)
                if resolved_candidate is not None:
                    resolver_source_type = resolver.source_type
                    resolver_found_candidate = True
                    break

        if resolved_candidate is None:
            identifier_label = (
                f"EAN {payload.get('ean_gtin')}"
                if payload.get("ean_gtin")
                else f"{payload.get('manufacturer', '')} {payload.get('mpn', '')}".strip()
                if payload.get("manufacturer") or payload.get("mpn")
                else payload.get("url")
                or "den übergebenen Daten"
            )
            resolved_candidate = {
                "canonical_title": payload.get("mpn")
                or payload.get("ean_gtin")
                or "Manual Review Candidate",
                "manufacturer": payload.get("manufacturer"),
                "brand": payload.get("manufacturer"),
                "mpn": payload.get("mpn"),
                "ean_gtin": payload.get("ean_gtin"),
                "category": "Needs Review",
                "description_short": f"Keine Mock-Auflösung für {identifier_label} gefunden. Bitte Stammdaten manuell ergänzen.",
                "attributes_json": {},
                "datasheet_url": None,
                "image_url": None,
                "confidence": 0.25,
                "source_value": payload.get("url")
                or payload.get("ean_gtin")
                or f"{payload.get('manufacturer', '')}:{payload.get('mpn', '')}",
                "raw_title": None,
                "resolved_url": payload.get("url"),
                "raw_payload_json": {"resolver": "manual_fallback"},
            }

        candidate = prepare_product_payload(resolved_candidate)
        matched_product, match_strategy = find_existing_product(session, candidate)

        source = ProductSource(
            product_id=matched_product.id if matched_product is not None else None,
            source_type=resolver_source_type,
            source_value=resolved_candidate["source_value"],
            raw_title=resolved_candidate.get("raw_title"),
            raw_payload_json=resolved_candidate.get("raw_payload_json") or {},
            resolved_url=resolved_candidate.get("resolved_url"),
            confidence=resolved_candidate.get("confidence", 0.0),
        )
        session.add(source)
        session.commit()
        session.refresh(source)

        return ResolutionResult(
            candidate=candidate,
            source_id=source.id,
            resolver_type=resolver_source_type,
            match_strategy=match_strategy,
            confidence=resolved_candidate.get("confidence", 0.0),
            matched_product_id=matched_product.id if matched_product is not None else None,
            requires_manual_review=not resolver_found_candidate,
        )
