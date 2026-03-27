from __future__ import annotations


def test_product_sources_can_be_filtered_by_source_id(client):
    first = client.post(
        "/api/products/resolve",
        json={"url": "https://catalog.mock/toolhub/milwaukee-m18fdd3-0"},
    )
    second = client.post(
        "/api/products/resolve",
        json={"ean_gtin": "3250612668090"},
    )

    assert first.status_code == 200
    assert second.status_code == 200

    first_source_id = first.json()["source_id"]
    second_source_id = second.json()["source_id"]

    response = client.get(f"/api/product-sources?source_id={second_source_id}")
    assert response.status_code == 200

    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["id"] == second_source_id
    assert payload[0]["id"] != first_source_id
