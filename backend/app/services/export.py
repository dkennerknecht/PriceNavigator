from __future__ import annotations

import csv
import io

from app.models.entities import Offer, Product, ShoppingList


def products_to_csv(products: list[Product]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "id",
            "canonical_title",
            "manufacturer",
            "brand",
            "mpn",
            "ean_gtin",
            "category",
            "fingerprint",
            "is_archived",
        ]
    )
    for product in products:
        writer.writerow(
            [
                product.id,
                product.canonical_title,
                product.manufacturer,
                product.brand,
                product.mpn,
                product.ean_gtin,
                product.category,
                product.fingerprint,
                product.is_archived,
            ]
        )
    return output.getvalue()


def offers_to_csv(offers: list[Offer]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "id",
            "product_id",
            "shop_id",
            "offer_title",
            "price",
            "currency",
            "availability",
            "source_url",
            "is_active",
        ]
    )
    for offer in offers:
        writer.writerow(
            [
                offer.id,
                offer.product_id,
                offer.shop_id,
                offer.offer_title,
                offer.price,
                offer.currency,
                offer.availability,
                offer.source_url,
                offer.is_active,
            ]
        )
    return output.getvalue()


def shopping_list_to_csv(shopping_list: ShoppingList) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "shopping_list_id",
            "shopping_list_name",
            "item_id",
            "product_id",
            "product_title",
            "required_qty",
            "unit",
            "notes",
        ]
    )
    for item in shopping_list.items:
        writer.writerow(
            [
                shopping_list.id,
                shopping_list.name,
                item.id,
                item.product_id,
                item.product.canonical_title,
                item.required_qty,
                item.unit,
                item.notes,
            ]
        )
    return output.getvalue()
