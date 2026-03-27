from __future__ import annotations

from sqlalchemy import select

from app.models.entities import ShoppingList
from app.services.optimization import OptimizationService


def test_optimization_prefers_single_shop_when_penalty_is_high(seeded_session):
    shopping_list = seeded_session.scalar(
        select(ShoppingList).where(ShoppingList.name == "Workshop Restock")
    )
    assert shopping_list is not None

    result = OptimizationService().optimize(seeded_session, shopping_list.id)

    assert result["shop_count"] == 1
    assert result["total_score"] == 196.1
    grouped_shops = result["summary_json"]["grouped_shops"]
    assert len(grouped_shops) == 1
    assert grouped_shops[0]["shop_name"] == "ElectroMax"
