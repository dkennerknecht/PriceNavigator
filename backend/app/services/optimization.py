from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import product as cartesian_product

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.entities import Offer, Shop, ShoppingList, ShoppingListItem
from app.repositories.optimization_runs import create_run


@dataclass(frozen=True)
class SelectedOffer:
    shopping_list_item: ShoppingListItem
    offer: Offer


def _shipping_cost_for_shop(shop: Shop, selections: list[SelectedOffer]) -> float:
    subtotal = sum(
        selection.offer.price * selection.shopping_list_item.required_qty
        for selection in selections
    )
    if shop.shipping_free_threshold is not None and subtotal >= shop.shipping_free_threshold:
        return 0.0

    shipping_candidates = [
        selection.offer.shipping_cost
        for selection in selections
        if selection.offer.shipping_cost is not None
    ]
    if shipping_candidates:
        return max(shipping_candidates)
    return shop.default_shipping_cost


def evaluate_selection(selected_offers: list[SelectedOffer], shop_penalty: float) -> dict:
    by_shop: dict[int, list[SelectedOffer]] = defaultdict(list)
    item_sum = 0.0

    for selection in selected_offers:
        by_shop[selection.offer.shop_id].append(selection)
        item_sum += selection.offer.price * selection.shopping_list_item.required_qty

    grouped_shops = []
    total_shipping = 0.0
    for selections in by_shop.values():
        shop = selections[0].offer.shop
        shipping_cost = _shipping_cost_for_shop(shop, selections)
        subtotal = sum(
            selection.offer.price * selection.shopping_list_item.required_qty
            for selection in selections
        )
        total_shipping += shipping_cost
        grouped_shops.append(
            {
                "shop_id": shop.id,
                "shop_name": shop.name,
                "shop_domain": shop.domain,
                "subtotal": round(subtotal, 2),
                "shipping_cost": round(shipping_cost, 2),
                "items": [
                    {
                        "shopping_list_item_id": selection.shopping_list_item.id,
                        "product_id": selection.shopping_list_item.product_id,
                        "product_title": selection.shopping_list_item.product.canonical_title,
                        "offer_id": selection.offer.id,
                        "offer_title": selection.offer.offer_title,
                        "offer_url": selection.offer.source_url,
                        "quantity": selection.shopping_list_item.required_qty,
                        "unit_price": round(selection.offer.price, 2),
                        "line_total": round(
                            selection.offer.price * selection.shopping_list_item.required_qty,
                            2,
                        ),
                    }
                    for selection in selections
                ],
            }
        )

    grouped_shops.sort(key=lambda group: group["shop_name"])
    shop_count = len(grouped_shops)
    total_score = item_sum + total_shipping + max(shop_count - 1, 0) * shop_penalty
    return {
        "grouped_shops": grouped_shops,
        "item_sum": round(item_sum, 2),
        "shipping_sum": round(total_shipping, 2),
        "shop_count": shop_count,
        "total_score": round(total_score, 2),
    }


class OptimizationService:
    def optimize(self, session: Session, shopping_list_id: int) -> dict:
        shopping_list = session.scalar(
            select(ShoppingList)
            .where(ShoppingList.id == shopping_list_id)
            .options(selectinload(ShoppingList.items).selectinload(ShoppingListItem.product))
        )
        if shopping_list is None:
            raise ValueError("Shopping list not found")
        if not shopping_list.items:
            raise ValueError("Shopping list has no items")

        offer_matrix: list[list[Offer]] = []
        for item in shopping_list.items:
            offers = list(
                session.scalars(
                    select(Offer)
                    .where(Offer.product_id == item.product_id, Offer.is_active.is_(True))
                    .options(joinedload(Offer.shop), joinedload(Offer.product))
                    .order_by(Offer.price.asc())
                ).unique()
            )
            if not offers:
                raise ValueError(f"No active offers available for product {item.product_id}")

            best_offer_per_shop: dict[int, Offer] = {}
            for offer in offers:
                current = best_offer_per_shop.get(offer.shop_id)
                if current is None or offer.price < current.price:
                    best_offer_per_shop[offer.shop_id] = offer
            offer_matrix.append(list(best_offer_per_shop.values())[:4])

        best_result: dict | None = None
        best_selection: list[SelectedOffer] | None = None

        for combination in cartesian_product(*offer_matrix):
            selected = [
                SelectedOffer(shopping_list_item=item, offer=offer)
                for item, offer in zip(shopping_list.items, combination, strict=True)
            ]
            current = evaluate_selection(selected, shopping_list.shop_penalty)
            if best_result is None or current["total_score"] < best_result["total_score"]:
                best_result = current
                best_selection = selected

        assert best_result is not None and best_selection is not None

        run = create_run(
            session,
            payload={
                "shopping_list_id": shopping_list.id,
                "status": "completed",
                "shop_penalty": shopping_list.shop_penalty,
                "total_items_price": best_result["item_sum"],
                "total_shipping": best_result["shipping_sum"],
                "total_score": best_result["total_score"],
                "shop_count": best_result["shop_count"],
                "summary_json": {
                    **best_result,
                    "shopping_list_name": shopping_list.name,
                },
            },
            items=[
                {
                    "shopping_list_item_id": selection.shopping_list_item.id,
                    "product_id": selection.offer.product_id,
                    "offer_id": selection.offer.id,
                    "shop_id": selection.offer.shop_id,
                    "quantity": selection.shopping_list_item.required_qty,
                    "unit_price": selection.offer.price,
                    "line_total": selection.offer.price * selection.shopping_list_item.required_qty,
                    "notes": selection.offer.source_url,
                }
                for selection in best_selection
            ],
        )
        return {
            "id": run.id,
            "shopping_list_id": run.shopping_list_id,
            "status": run.status,
            "shop_penalty": run.shop_penalty,
            "total_items_price": run.total_items_price,
            "total_shipping": run.total_shipping,
            "total_score": run.total_score,
            "shop_count": run.shop_count,
            "summary_json": run.summary_json,
            "created_at": run.created_at,
            "items": run.items,
        }
