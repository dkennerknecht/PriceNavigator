from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class OfferSearchRequest(BaseModel):
    product_id: int | None = None
    product_ids: list[int] | None = None


class OfferBase(BaseModel):
    product_id: int
    shop_id: int
    source_url: str
    offer_title: str
    manufacturer: str | None = None
    brand: str | None = None
    mpn: str | None = None
    ean_gtin: str | None = None
    pack_qty: float = 1.0
    pack_unit: str = "unit"
    price: float
    currency: str = "EUR"
    availability: str = "unknown"
    shipping_cost: float | None = None
    minimum_order_value: float | None = None
    lead_time_days: int | None = None
    attributes_json: dict[str, Any] = Field(default_factory=dict)
    matched_confidence: float = 0.0
    is_active: bool = True


class OfferUpdate(OfferBase):
    pass


class OfferRead(OfferBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    last_checked_at: datetime
    created_at: datetime
    updated_at: datetime


class OfferSearchResponse(BaseModel):
    offers: list[OfferRead]
    created_count: int
    warnings: list[str] = Field(default_factory=list)
