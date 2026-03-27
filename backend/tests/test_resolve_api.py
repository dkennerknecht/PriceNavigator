from __future__ import annotations

from sqlalchemy import select

from app.models.entities import Product


def test_resolve_by_url_returns_candidate_and_source(client):
    response = client.post(
        "/api/products/resolve",
        json={"url": "https://catalog.mock/toolhub/milwaukee-m18fdd3-0"},
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["candidate"]["canonical_title"] == "Milwaukee M18 FUEL Drill Driver"
    assert payload["candidate"]["image_url"].startswith("data:image/svg+xml")
    assert payload["source_id"] > 0
    assert payload["resolver_type"] == "url"
    assert payload["match_strategy"] == "manual_review"
    assert payload["requires_manual_review"] is False


def test_resolve_by_ean_returns_hager_candidate(client):
    response = client.post("/api/products/resolve", json={"ean_gtin": "3250612668090"})
    assert response.status_code == 200

    payload = response.json()
    assert payload["candidate"]["canonical_title"] == "Hager univers Enclosure IP44 1400x550x205 mm"
    assert payload["candidate"]["manufacturer"] == "Hager"
    assert payload["candidate"]["brand"] == "Hager"
    assert payload["candidate"]["mpn"] == "FP92TN2"
    assert payload["candidate"]["ean_gtin"] == "3250612668090"
    assert payload["candidate"]["image_url"].endswith("FP92TN2.webp")
    assert payload["resolver_type"] == "ean"
    assert payload["confidence"] == 0.99
    assert payload["requires_manual_review"] is False


def test_resolve_by_ean_matches_existing_product(seeded_client, session):
    existing = session.scalar(select(Product).where(Product.mpn == "221-413"))
    assert existing is not None

    response = seeded_client.post("/api/products/resolve", json={"ean_gtin": existing.ean_gtin})
    assert response.status_code == 200

    payload = response.json()
    assert payload["candidate"]["canonical_title"] == existing.canonical_title
    assert payload["matched_product_id"] == existing.id
    assert payload["resolver_type"] == "ean"
    assert payload["match_strategy"] == "ean"
