from __future__ import annotations

from app.models.entities import Product


def test_product_crud_flow(client):
    create_response = client.post(
        "/api/products",
        json={
            "canonical_title": "Test Product",
            "manufacturer": "Acme",
            "brand": "Acme",
            "mpn": "ACME-001",
            "ean_gtin": "1234567890123",
            "category": "Test",
            "description_short": "Created in API test",
            "attributes_json": {"size": "M"},
            "datasheet_url": None,
            "image_url": None,
            "notes": "note",
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()

    list_response = client.get("/api/products")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    update_response = client.put(
        f"/api/products/{created['id']}",
        json={
            "canonical_title": "Updated Product",
            "manufacturer": "Acme",
            "brand": "Acme Pro",
            "mpn": "ACME-001",
            "ean_gtin": "1234567890123",
            "category": "Updated",
            "description_short": "Updated description",
            "attributes_json": {"size": "L"},
            "datasheet_url": None,
            "image_url": None,
            "notes": "updated",
            "is_archived": False,
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["canonical_title"] == "Updated Product"

    delete_response = client.delete(f"/api/products/{created['id']}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Product archived"

    active_response = client.get("/api/products")
    assert active_response.status_code == 200
    assert active_response.json() == []

    archived_response = client.get("/api/products?include_archived=true")
    assert len(archived_response.json()) == 1
    assert archived_response.json()[0]["is_archived"] is True


def test_get_product_normalizes_non_image_catalog_url(client, session):
    product = Product(
        canonical_title="Hager univers Enclosure IP44 1400x550x205 mm",
        manufacturer="Hager",
        brand="Hager",
        mpn="FP92TN2",
        ean_gtin="3250612668090",
        category="Electrical Enclosure",
        description_short="Old product record with product page URL as image.",
        attributes_json={},
        datasheet_url="https://hager.com/ie/catalogue/products/fp92tn2-encl-univers-ip44-cl-1-1400x550x205mm",
        image_url="https://hager.com/ie/catalogue/products/fp92tn2-encl-univers-ip44-cl-1-1400x550x205mm",
        notes=None,
        search_tokens="fp92tn2 hager",
        fingerprint="ean:3250612668090",
    )
    session.add(product)
    session.commit()
    session.refresh(product)

    detail_response = client.get(f"/api/products/{product.id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["image_url"].endswith("FP92TN2.webp")
