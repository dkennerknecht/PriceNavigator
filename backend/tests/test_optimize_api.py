from __future__ import annotations

from sqlalchemy import select

from app.models.entities import ShoppingList


def test_optimize_endpoint_creates_run(seeded_client, session):
    shopping_list = session.scalar(
        select(ShoppingList).where(ShoppingList.name == "Workshop Restock")
    )
    assert shopping_list is not None

    response = seeded_client.post(f"/api/shopping-lists/{shopping_list.id}/optimize")
    assert response.status_code == 200

    payload = response.json()
    assert payload["shopping_list_id"] == shopping_list.id
    assert payload["shop_count"] == 1
    assert len(payload["items"]) == 3
    assert payload["summary_json"]["grouped_shops"][0]["shop_name"] == "ElectroMax"
