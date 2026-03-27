from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ShoppingListBase(BaseModel):
    name: str
    description: str | None = None
    status: str = "draft"
    shop_penalty: float = 10.0


class ShoppingListCreate(ShoppingListBase):
    pass


class ShoppingListUpdate(ShoppingListBase):
    pass


class ProductSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    canonical_title: str
    manufacturer: str | None = None
    mpn: str | None = None


class ShoppingListItemBase(BaseModel):
    product_id: int
    required_qty: float
    unit: str = "unit"
    notes: str | None = None


class ShoppingListItemCreate(ShoppingListItemBase):
    pass


class ShoppingListItemUpdate(ShoppingListItemBase):
    pass


class ShoppingListItemRead(ShoppingListItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    product: ProductSummary


class ShoppingListRead(ShoppingListBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class ShoppingListDetailRead(ShoppingListRead):
    items: list[ShoppingListItemRead]
