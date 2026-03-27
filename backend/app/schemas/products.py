from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductBase(BaseModel):
    canonical_title: str
    manufacturer: str | None = None
    brand: str | None = None
    mpn: str | None = None
    ean_gtin: str | None = None
    category: str | None = None
    description_short: str | None = None
    attributes_json: dict[str, Any] = Field(default_factory=dict)
    datasheet_url: str | None = None
    image_url: str | None = None
    notes: str | None = None


class ProductCreate(ProductBase):
    source_id: int | None = None


class ProductUpdate(BaseModel):
    canonical_title: str
    manufacturer: str | None = None
    brand: str | None = None
    mpn: str | None = None
    ean_gtin: str | None = None
    category: str | None = None
    description_short: str | None = None
    attributes_json: dict[str, Any] = Field(default_factory=dict)
    datasheet_url: str | None = None
    image_url: str | None = None
    notes: str | None = None
    is_archived: bool = False


class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    search_tokens: str | None
    fingerprint: str | None
    created_at: datetime
    updated_at: datetime
    is_archived: bool


class ProductResolveInput(BaseModel):
    url: str | None = None
    manufacturer: str | None = None
    mpn: str | None = None
    ean_gtin: str | None = None

    @field_validator("url", mode="after")
    @classmethod
    def blank_url_to_none(cls, value: str | None) -> str | None:
        return value or None

    @field_validator("manufacturer", "mpn", "ean_gtin", mode="after")
    @classmethod
    def blank_to_none(cls, value: str | None) -> str | None:
        return value or None


class ProductResolveCandidate(BaseModel):
    canonical_title: str
    manufacturer: str | None = None
    brand: str | None = None
    mpn: str | None = None
    ean_gtin: str | None = None
    category: str | None = None
    description_short: str | None = None
    attributes_json: dict[str, Any] = Field(default_factory=dict)
    datasheet_url: str | None = None
    image_url: str | None = None
    search_tokens: str | None = None
    fingerprint: str | None = None


class ProductResolveResponse(BaseModel):
    candidate: ProductResolveCandidate
    source_id: int
    resolver_type: str
    match_strategy: str
    confidence: float
    matched_product_id: int | None = None
    requires_manual_review: bool = False


class ProductSourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int | None
    source_type: str
    source_value: str
    raw_title: str | None
    raw_payload_json: dict[str, Any]
    resolved_url: str | None
    confidence: float
    created_at: datetime


class ProductSourceUpdate(BaseModel):
    product_id: int | None = None
    source_type: str
    source_value: str
    raw_title: str | None = None
    raw_payload_json: dict[str, Any] = Field(default_factory=dict)
    resolved_url: str | None = None
    confidence: float = 0.0
