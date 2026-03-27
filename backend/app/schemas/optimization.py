from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class OptimizationRunItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    optimization_run_id: int
    shopping_list_item_id: int
    product_id: int
    offer_id: int
    shop_id: int
    quantity: float
    unit_price: float
    line_total: float
    notes: str | None = None


class OptimizationRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    shopping_list_id: int
    status: str
    shop_penalty: float
    total_items_price: float
    total_shipping: float
    total_score: float
    shop_count: int
    summary_json: dict[str, Any]
    created_at: datetime
    items: list[OptimizationRunItemRead]
