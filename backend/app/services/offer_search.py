from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.models.entities import Product, Shop
from app.repositories import offers as offer_repository
from app.repositories import product_sources as product_source_repository
from app.repositories import shops as shop_repository
from app.services.catalog import MOCK_OFFERS

MAX_OFFERS_PER_PRODUCT = 10


@dataclass
class ProviderSearchResult:
    offers: list[dict]
    warnings: list[str] = field(default_factory=list)
    stop: bool = False


class OfferSearchProvider(Protocol):
    def search(self, session: Session, product: Product) -> ProviderSearchResult: ...


def _coerce_float(value) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        stripped = value.replace("EUR", "").replace("€", "").replace(",", ".").strip()
        try:
            return float(stripped)
        except ValueError:
            return None
    return None


def _coerce_int(value) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(round(value))
    if isinstance(value, str):
        digits = "".join(character for character in value if character.isdigit())
        if digits:
            return int(digits)
    return None


def _extract_domain(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urlparse(url)
    domain = parsed.netloc.lower().strip()
    if domain.startswith("www."):
        domain = domain[4:]
    return domain or None


def _looks_like_http_url(value: str | None) -> bool:
    if not value:
        return False
    return value.startswith("http://") or value.startswith("https://")


def _effective_source_url(source) -> str | None:
    if _looks_like_http_url(source.resolved_url):
        return source.resolved_url
    if _looks_like_http_url(source.source_value):
        return source.source_value
    payload_url = source.raw_payload_json.get("source_url")
    if isinstance(payload_url, str) and _looks_like_http_url(payload_url):
        return payload_url
    return None


def _is_internal_source_url(url: str | None) -> bool:
    domain = _extract_domain(url)
    if domain is None:
        return True
    return domain.endswith(".mock")


def _is_explicit_offer_source(source) -> bool:
    source_type = (source.source_type or "").strip().lower()
    if "offer" in source_type:
        return True

    payload = source.raw_payload_json or {}
    return any(
        key in payload
        for key in (
            "price",
            "unit_price",
            "total_price",
            "shipping_cost",
            "currency",
            "availability",
            "shop_name",
            "shop_domain",
        )
    )


def _is_user_managed_external_source(source) -> bool:
    source_type = (source.source_type or "").strip().lower()
    if source_type in {"seed", "ean", "manufacturer_mpn", "manual"}:
        return False
    return not _is_internal_source_url(_effective_source_url(source))


def _shop_name_from_domain(domain: str) -> str:
    first_label = domain.split(".", 1)[0].replace("-", " ").strip()
    return first_label.title() if first_label else domain


class ProductSourceOfferProvider:
    def search(self, session: Session, product: Product) -> ProviderSearchResult:
        sources = product_source_repository.list_sources(session, product_id=product.id)
        candidate_sources = [source for source in sources if _is_user_managed_external_source(source)]
        if not candidate_sources:
            return ProviderSearchResult(offers=[], stop=False)
        offer_sources = [source for source in candidate_sources if _is_explicit_offer_source(source)]

        payloads: list[dict] = []
        incomplete_sources = len(candidate_sources) - len(offer_sources)

        for source in offer_sources:
            payload = source.raw_payload_json or {}
            source_url = _effective_source_url(source)
            price = (
                _coerce_float(payload.get("price"))
                or _coerce_float(payload.get("unit_price"))
                or _coerce_float(payload.get("total_price"))
            )
            if not source_url or price is None:
                incomplete_sources += 1
                continue

            domain = str(payload.get("shop_domain") or _extract_domain(source_url) or "").strip().lower()
            if not domain:
                incomplete_sources += 1
                continue

            shipping_cost = _coerce_float(payload.get("shipping_cost"))
            payloads.append(
                {
                    "product_id": product.id,
                    "source_url": source_url,
                    "offer_title": str(payload.get("offer_title") or payload.get("title") or source.raw_title or product.canonical_title),
                    "manufacturer": product.manufacturer,
                    "brand": product.brand,
                    "mpn": product.mpn,
                    "ean_gtin": product.ean_gtin,
                    "pack_qty": _coerce_float(payload.get("pack_qty")) or 1.0,
                    "pack_unit": str(payload.get("pack_unit") or "unit"),
                    "price": price,
                    "currency": str(payload.get("currency") or "EUR"),
                    "availability": str(payload.get("availability") or "unknown"),
                    "shipping_cost": shipping_cost,
                    "minimum_order_value": _coerce_float(payload.get("minimum_order_value")),
                    "lead_time_days": _coerce_int(payload.get("lead_time_days") or payload.get("delivery_days")),
                    "attributes_json": {
                        "provider": "product_source",
                        "product_source_id": source.id,
                    },
                    "matched_confidence": source.confidence,
                    "last_checked_at": datetime.now(UTC),
                    "is_active": True,
                    "shop_payload": {
                        "name": str(payload.get("shop_name") or _shop_name_from_domain(domain)),
                        "domain": domain,
                        "shipping_free_threshold": _coerce_float(payload.get("shipping_free_threshold")),
                        "default_shipping_cost": shipping_cost or 0.0,
                        "trusted": bool(payload.get("trusted", True)),
                        "penalty_score": _coerce_float(payload.get("penalty_score")) or 0.0,
                        "notes": str(payload.get("notes") or f"Imported from product source #{source.id}"),
                    },
                }
            )

        warnings: list[str] = []
        if incomplete_sources:
            warnings.append(
                f"{incomplete_sources} hinterlegte Quellen konnten nicht als Offers übernommen werden, weil Angebotsdaten wie Preis oder URL fehlen."
            )
        if not payloads:
            warnings.append(
                "Für dieses Produkt sind echte Quellen hinterlegt, aber keine davon enthält vollständige Angebotsdaten."
            )
            return ProviderSearchResult(offers=[], warnings=warnings, stop=True)

        return ProviderSearchResult(offers=payloads, warnings=warnings, stop=True)


class MockOfferProvider:
    def search(self, session: Session, product: Product) -> ProviderSearchResult:
        matching_offers = [offer for offer in MOCK_OFFERS if offer["mpn"] == product.mpn]
        payloads: list[dict] = []
        for offer in matching_offers:
            payloads.append(
                {
                    "product_id": product.id,
                    "source_url": offer["source_url"],
                    "offer_title": offer["offer_title"],
                    "manufacturer": product.manufacturer,
                    "brand": product.brand,
                    "mpn": product.mpn,
                    "ean_gtin": product.ean_gtin,
                    "pack_qty": 1.0,
                    "pack_unit": "unit",
                    "price": offer["price"],
                    "currency": "EUR",
                    "availability": offer["availability"],
                    "shipping_cost": offer["shipping_cost"],
                    "minimum_order_value": None,
                    "lead_time_days": offer["lead_time_days"],
                    "attributes_json": {"provider": "mock_offer"},
                    "matched_confidence": 0.92,
                    "last_checked_at": datetime.now(UTC),
                    "is_active": True,
                    "shop_payload": {
                        "name": offer["shop_domain"].split(".", 1)[0].replace("-", " ").title(),
                        "domain": offer["shop_domain"],
                        "shipping_free_threshold": None,
                        "default_shipping_cost": offer["shipping_cost"],
                        "trusted": True,
                        "penalty_score": 0.0,
                        "notes": "Imported from mock offer provider",
                    },
                }
            )
        return ProviderSearchResult(offers=payloads, stop=True)


@dataclass
class OfferSearchResult:
    offers: list
    created_count: int
    warnings: list[str] = field(default_factory=list)


def _offer_rank_key(payload: dict) -> tuple:
    availability_rank = 0 if payload.get("availability") == "in_stock" else 1
    shipping_cost = payload.get("shipping_cost") or 0.0
    lead_time_days = payload.get("lead_time_days")
    lead_time_rank = lead_time_days if lead_time_days is not None else 999999
    confidence = payload.get("matched_confidence") or 0.0
    total_landed_cost = payload["price"] + shipping_cost
    return (
        availability_rank,
        round(total_landed_cost, 4),
        round(payload["price"], 4),
        round(shipping_cost, 4),
        lead_time_rank,
        -confidence,
        payload["source_url"],
    )


def _select_best_offers(payloads: list[dict]) -> list[dict]:
    deduped_by_source: dict[tuple[str, str], dict] = {}
    for payload in payloads:
        shop_payload = payload.get("shop_payload") or {}
        dedupe_key = (str(shop_payload.get("domain") or ""), payload["source_url"])
        current = deduped_by_source.get(dedupe_key)
        if current is None or _offer_rank_key(payload) < _offer_rank_key(current):
            deduped_by_source[dedupe_key] = payload

    ranked_payloads = sorted(deduped_by_source.values(), key=_offer_rank_key)
    return ranked_payloads[:MAX_OFFERS_PER_PRODUCT]


def _materialize_shop(
    session: Session, shop_cache: dict[str, Shop], payload: dict
) -> Shop | None:
    shop_payload = payload.get("shop_payload")
    if not isinstance(shop_payload, dict):
        return None

    domain = str(shop_payload.get("domain") or "").strip().lower()
    if not domain:
        return None

    cached = shop_cache.get(domain)
    if cached is not None:
        return cached

    existing = shop_repository.get_shop_by_domain(session, domain)
    if existing is not None:
        shop_cache[domain] = existing
        return existing

    created = shop_repository.create_shop(session, shop_payload)
    shop_cache[domain] = created
    return created


class OfferSearchService:
    def __init__(self, providers: list[OfferSearchProvider] | None = None) -> None:
        self.providers = providers or [ProductSourceOfferProvider(), MockOfferProvider()]

    def search(self, session: Session, products: list[Product]) -> OfferSearchResult:
        saved_offers = []
        warnings: list[str] = []
        product_ids = [product.id for product in products]
        offer_repository.hard_delete_offers_for_products(session, product_ids)

        existing_shops = {shop.domain: shop for shop in shop_repository.list_shops(session)}

        for product in products:
            product_payloads: list[dict] = []
            for provider in self.providers:
                result = provider.search(session, product)
                warnings.extend(result.warnings)
                product_payloads.extend(result.offers)
                if result.offers or result.stop:
                    break

            for payload in _select_best_offers(product_payloads):
                shop = _materialize_shop(session, existing_shops, payload)
                if shop is None:
                    continue

                offer_payload = {
                    key: value for key, value in payload.items() if key != "shop_payload"
                }
                offer_payload["shop_id"] = shop.id
                offer = offer_repository.save_offer(session, offer_payload)
                saved_offers.append(offer)

        deduped_warnings = list(dict.fromkeys(warnings))
        return OfferSearchResult(
            offers=saved_offers,
            created_count=len(saved_offers),
            warnings=deduped_warnings,
        )
