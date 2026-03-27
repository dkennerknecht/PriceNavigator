from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Offer, Product, ProductSource, Shop, ShoppingList, ShoppingListItem
from app.services.catalog import CATALOG_PRODUCTS, MOCK_OFFERS, MOCK_SHOPS
from app.services.product_matching import prepare_product_payload


def seed_database(session: Session) -> None:
    has_products = session.scalar(select(Product.id).limit(1))
    if has_products is not None:
        return

    shops_by_domain: dict[str, Shop] = {}
    for shop_payload in MOCK_SHOPS:
        shop = Shop(**shop_payload)
        session.add(shop)
        session.flush()
        shops_by_domain[shop.domain] = shop

    products_by_mpn: dict[str, Product] = {}
    for catalog_product in CATALOG_PRODUCTS:
        product = Product(
            **prepare_product_payload(
                {
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
                    "notes": "Seeded product",
                }
            )
        )
        session.add(product)
        session.flush()
        session.add(
            ProductSource(
                product_id=product.id,
                source_type="seed",
                source_value=catalog_product.source_url,
                raw_title=catalog_product.canonical_title,
                raw_payload_json={"seed": True},
                resolved_url=catalog_product.source_url,
                confidence=1.0,
            )
        )
        products_by_mpn[catalog_product.mpn] = product

    for offer_payload in MOCK_OFFERS:
        product = products_by_mpn[offer_payload["mpn"]]
        shop = shops_by_domain[offer_payload["shop_domain"]]
        session.add(
            Offer(
                product_id=product.id,
                shop_id=shop.id,
                source_url=offer_payload["source_url"],
                offer_title=offer_payload["offer_title"],
                manufacturer=product.manufacturer,
                brand=product.brand,
                mpn=product.mpn,
                ean_gtin=product.ean_gtin,
                pack_qty=1.0,
                pack_unit="unit",
                price=offer_payload["price"],
                currency="EUR",
                availability=offer_payload["availability"],
                shipping_cost=offer_payload["shipping_cost"],
                minimum_order_value=None,
                lead_time_days=offer_payload["lead_time_days"],
                attributes_json={"seed": True},
                matched_confidence=0.95,
            )
        )

    shopping_list = ShoppingList(
        name="Workshop Restock",
        description="Baseline seeded shopping list",
        status="draft",
        shop_penalty=12.0,
    )
    session.add(shopping_list)
    session.flush()
    session.add_all(
        [
            ShoppingListItem(
                shopping_list_id=shopping_list.id,
                product_id=products_by_mpn["M18FDD3-0"].id,
                required_qty=1,
                unit="pcs",
                notes="Cordless drill",
            ),
            ShoppingListItem(
                shopping_list_id=shopping_list.id,
                product_id=products_by_mpn["221-413"].id,
                required_qty=2,
                unit="packs",
                notes="Wiring connectors",
            ),
            ShoppingListItem(
                shopping_list_id=shopping_list.id,
                product_id=products_by_mpn["19300060447"].id,
                required_qty=4,
                unit="pcs",
                notes="Panel connectors",
            ),
        ]
    )
    session.commit()
