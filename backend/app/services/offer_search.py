from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol

from sqlalchemy.orm import Session

from app.models.entities import Product, Shop
from app.repositories import offers as offer_repository
from app.repositories import shops as shop_repository
from app.services.catalog import MOCK_OFFERS

MAX_OFFERS_PER_PRODUCT = 10


@dataclass
class ProviderSearchResult:
    offers: list[dict]
    warnings: list[str] = field(default_factory=list)
    stop: bool = False


class OfferSearchProvider(Protocol):
    def search(self, product: Product) -> ProviderSearchResult: ...


class MockOfferProvider:
    def search(self, product: Product) -> ProviderSearchResult:
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
        self.providers = providers or [MockOfferProvider()]

    def search(self, session: Session, products: list[Product]) -> OfferSearchResult:
        saved_offers = []
        warnings: list[str] = []
        product_ids = [product.id for product in products]
        offer_repository.hard_delete_offers_for_products(session, product_ids)

        existing_shops = {shop.domain: shop for shop in shop_repository.list_shops(session)}

        for product in products:
            product_payloads: list[dict] = []
            for provider in self.providers:
                result = provider.search(product)
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
