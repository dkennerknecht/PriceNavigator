from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ShopBase(BaseModel):
    name: str
    domain: str
    shipping_free_threshold: float | None = None
    default_shipping_cost: float = 0.0
    trusted: bool = True
    penalty_score: float = 0.0
    notes: str | None = None


class ShopCreate(ShopBase):
    pass


class ShopUpdate(ShopBase):
    pass


class ShopRead(ShopBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
