from __future__ import annotations

from sqlalchemy import select

from app.models.entities import Offer, Product


def test_shop_offer_and_shopping_list_crud(seeded_client, session):
    shop_create = seeded_client.post(
        "/api/shops",
        json={
            "name": "New Shop",
            "domain": "newshop.example",
            "shipping_free_threshold": 99.0,
            "default_shipping_cost": 3.9,
            "trusted": True,
            "penalty_score": 0.5,
            "notes": "Test shop",
        },
    )
    assert shop_create.status_code == 201
    shop_id = shop_create.json()["id"]

    shop_update = seeded_client.put(
        f"/api/shops/{shop_id}",
        json={
            "name": "New Shop Updated",
            "domain": "newshop.example",
            "shipping_free_threshold": 120.0,
            "default_shipping_cost": 4.1,
            "trusted": False,
            "penalty_score": 0.8,
            "notes": "Updated",
        },
    )
    assert shop_update.status_code == 200
    assert shop_update.json()["name"] == "New Shop Updated"

    first_offer = session.scalar(select(Offer))
    assert first_offer is not None

    offer_update = seeded_client.put(
        f"/api/offers/{first_offer.id}",
        json={
            "product_id": first_offer.product_id,
            "shop_id": first_offer.shop_id,
            "source_url": first_offer.source_url,
            "offer_title": "Updated Offer Title",
            "manufacturer": first_offer.manufacturer,
            "brand": first_offer.brand,
            "mpn": first_offer.mpn,
            "ean_gtin": first_offer.ean_gtin,
            "pack_qty": first_offer.pack_qty,
            "pack_unit": first_offer.pack_unit,
            "price": 111.11,
            "currency": first_offer.currency,
            "availability": "in_stock",
            "shipping_cost": first_offer.shipping_cost,
            "minimum_order_value": first_offer.minimum_order_value,
            "lead_time_days": first_offer.lead_time_days,
            "attributes_json": first_offer.attributes_json,
            "matched_confidence": first_offer.matched_confidence,
            "is_active": True,
        },
    )
    assert offer_update.status_code == 200
    assert offer_update.json()["price"] == 111.11

    offer_delete = seeded_client.delete(f"/api/offers/{first_offer.id}")
    assert offer_delete.status_code == 200

    product = session.scalar(select(Product).where(Product.mpn == "2904601"))
    assert product is not None

    shopping_list_create = seeded_client.post(
        "/api/shopping-lists",
        json={
            "name": "Build Cabinet",
            "description": "Cabinet parts",
            "status": "draft",
            "shop_penalty": 8.0,
        },
    )
    assert shopping_list_create.status_code == 201
    shopping_list_id = shopping_list_create.json()["id"]

    add_item = seeded_client.post(
        f"/api/shopping-lists/{shopping_list_id}/items",
        json={"product_id": product.id, "required_qty": 2, "unit": "pcs", "notes": "Need backups"},
    )
    assert add_item.status_code == 201
    item_id = add_item.json()["id"]

    update_item = seeded_client.put(
        f"/api/shopping-list-items/{item_id}",
        json={"product_id": product.id, "required_qty": 3, "unit": "pcs", "notes": "Updated qty"},
    )
    assert update_item.status_code == 200
    assert update_item.json()["required_qty"] == 3

    detail_response = seeded_client.get(f"/api/shopping-lists/{shopping_list_id}")
    assert detail_response.status_code == 200
    assert len(detail_response.json()["items"]) == 1

    delete_item = seeded_client.delete(f"/api/shopping-list-items/{item_id}")
    assert delete_item.status_code == 200

    delete_list = seeded_client.delete(f"/api/shopping-lists/{shopping_list_id}")
    assert delete_list.status_code == 200

    delete_shop = seeded_client.delete(f"/api/shops/{shop_id}")
    assert delete_shop.status_code == 200
