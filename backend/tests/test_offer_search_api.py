from __future__ import annotations

from sqlalchemy import select

from app.models.entities import Offer, Product, Shop
from app.services.offer_search import (
    MAX_OFFERS_PER_PRODUCT,
    OfferSearchService,
    ProviderSearchResult,
)


def test_offer_search_replaces_existing_offers_for_product(seeded_client, session):
    product = session.scalar(select(Product).where(Product.mpn == "M18FDD3-0"))
    shop = session.scalar(select(Shop).where(Shop.domain == "industrialhub.example"))
    assert product is not None
    assert shop is not None

    session.add(
        Offer(
            product_id=product.id,
            shop_id=shop.id,
            source_url="https://industrialhub.example/obsolete-milwaukee-offer",
            offer_title="Obsolete Milwaukee Offer",
            manufacturer=product.manufacturer,
            brand=product.brand,
            mpn=product.mpn,
            ean_gtin=product.ean_gtin,
            pack_qty=1.0,
            pack_unit="unit",
            price=999.0,
            currency="EUR",
            availability="discontinued",
            shipping_cost=12.0,
            minimum_order_value=None,
            lead_time_days=30,
            attributes_json={"provider": "legacy"},
            matched_confidence=0.1,
        )
    )
    session.commit()

    before = seeded_client.get(f"/api/offers?product_id={product.id}&include_inactive=true")
    assert before.status_code == 200
    assert len(before.json()) == 3

    response = seeded_client.post("/api/offers/search", json={"product_id": product.id})
    assert response.status_code == 200
    payload = response.json()
    assert payload["created_count"] == 2
    assert len(payload["offers"]) == 2

    after = seeded_client.get(f"/api/offers?product_id={product.id}&include_inactive=true")
    assert after.status_code == 200
    offers = after.json()
    assert len(offers) == 2
    assert {offer["source_url"] for offer in offers} == {
        "https://toolsource.example/milwaukee-m18fdd3-0",
        "https://electromax.example/milwaukee-m18fdd3-0",
    }


def test_offer_search_persists_only_top_10_ranked_results(seeded_session, session):
    product = session.scalar(select(Product).where(Product.mpn == "M18FDD3-0"))
    shops = list(session.scalars(select(Shop).order_by(Shop.id)))
    assert product is not None
    assert len(shops) >= 3

    class ManyOffersProvider:
        def search(self, product: Product) -> ProviderSearchResult:
            payloads = []
            for index in range(12):
                shop = shops[index % len(shops)]
                payloads.append(
                    {
                        "product_id": product.id,
                        "source_url": f"https://offers.example/{product.mpn}/{index}",
                        "offer_title": f"Candidate {index}",
                        "manufacturer": product.manufacturer,
                        "brand": product.brand,
                        "mpn": product.mpn,
                        "ean_gtin": product.ean_gtin,
                        "pack_qty": 1.0,
                        "pack_unit": "unit",
                        "price": float(index + 1),
                        "currency": "EUR",
                        "availability": "in_stock",
                        "shipping_cost": 0.0,
                        "minimum_order_value": None,
                        "lead_time_days": index % 4,
                        "attributes_json": {"provider": "many"},
                        "matched_confidence": 0.9 - index * 0.01,
                        "is_active": True,
                        "shop_payload": {
                            "name": shop.name,
                            "domain": shop.domain,
                            "shipping_free_threshold": shop.shipping_free_threshold,
                            "default_shipping_cost": shop.default_shipping_cost,
                            "trusted": shop.trusted,
                            "penalty_score": shop.penalty_score,
                            "notes": shop.notes,
                        },
                    }
                )
            return ProviderSearchResult(offers=payloads, stop=True)

    service = OfferSearchService(providers=[ManyOffersProvider()])
    result = service.search(session, [product])

    assert result.created_count == MAX_OFFERS_PER_PRODUCT
    assert len(result.offers) == MAX_OFFERS_PER_PRODUCT
    assert [offer.offer_title for offer in result.offers] == [
        f"Candidate {index}" for index in range(MAX_OFFERS_PER_PRODUCT)
    ]

    persisted = session.scalars(
        select(Offer)
        .where(Offer.product_id == product.id)
        .order_by(Offer.price.asc(), Offer.source_url.asc())
    ).all()
    assert len(persisted) == MAX_OFFERS_PER_PRODUCT
    assert [offer.offer_title for offer in persisted] == [
        f"Candidate {index}" for index in range(MAX_OFFERS_PER_PRODUCT)
    ]


def test_offer_search_returns_mock_offers_for_hager_product(seeded_client, session):
    product = session.scalar(select(Product).where(Product.mpn == "FP92TN2"))
    assert product is not None

    response = seeded_client.post("/api/offers/search", json={"product_id": product.id})
    assert response.status_code == 200

    payload = response.json()
    assert payload["created_count"] == 3
    assert {offer["source_url"] for offer in payload["offers"]} == {
        "https://electromax.example/hager-fp92tn2",
        "https://industrialhub.example/hager-fp92tn2",
        "https://toolsource.example/hager-fp92tn2",
    }


def test_offer_search_creates_shop_records_for_external_results(seeded_session, session):
    product = session.scalar(select(Product).where(Product.mpn == "FP92TN2"))
    assert product is not None

    class ExternalProvider:
        def search(self, product: Product) -> ProviderSearchResult:
            return ProviderSearchResult(
                offers=[
                    {
                        "product_id": product.id,
                        "source_url": "https://shop.example/hager-fp92tn2",
                        "offer_title": "Hager univers enclosure FP92TN2",
                        "manufacturer": product.manufacturer,
                        "brand": product.brand,
                        "mpn": product.mpn,
                        "ean_gtin": product.ean_gtin,
                        "pack_qty": 1.0,
                        "pack_unit": "unit",
                        "price": 412.0,
                        "currency": "EUR",
                        "availability": "in_stock",
                        "shipping_cost": 7.9,
                        "minimum_order_value": None,
                        "lead_time_days": 2,
                        "attributes_json": {"provider": "external"},
                        "matched_confidence": 0.84,
                        "is_active": True,
                        "shop_payload": {
                            "name": "Shop Example",
                            "domain": "shop.example",
                            "shipping_free_threshold": None,
                            "default_shipping_cost": 7.9,
                            "trusted": True,
                            "penalty_score": 0.0,
                            "notes": "Imported from external provider",
                        },
                    }
                ],
                stop=True,
            )

    service = OfferSearchService(providers=[ExternalProvider()])
    result = service.search(session, [product])

    assert result.created_count == 1
    created_shop = session.scalar(select(Shop).where(Shop.domain == "shop.example"))
    assert created_shop is not None
    assert created_shop.name == "Shop Example"
    assert result.offers[0].shop_id == created_shop.id
