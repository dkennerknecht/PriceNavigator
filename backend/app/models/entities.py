from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    canonical_title: Mapped[str] = mapped_column(String(255))
    manufacturer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    brand: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mpn: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    ean_gtin: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description_short: Mapped[str | None] = mapped_column(Text, nullable=True)
    attributes_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    datasheet_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    search_tokens: Mapped[str | None] = mapped_column(Text, nullable=True)
    fingerprint: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
    )
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    sources: Mapped[list[ProductSource]] = relationship(back_populates="product")
    offers: Mapped[list[Offer]] = relationship(back_populates="product")
    shopping_list_items: Mapped[list[ShoppingListItem]] = relationship(back_populates="product")
    optimization_run_items: Mapped[list[OptimizationRunItem]] = relationship(
        back_populates="product"
    )


class ProductSource(Base):
    __tablename__ = "product_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"), nullable=True)
    source_type: Mapped[str] = mapped_column(String(50))
    source_value: Mapped[str] = mapped_column(String(500))
    raw_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raw_payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    resolved_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    product: Mapped[Product | None] = relationship(back_populates="sources")


class Shop(Base):
    __tablename__ = "shops"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    domain: Mapped[str] = mapped_column(String(255), unique=True)
    shipping_free_threshold: Mapped[float | None] = mapped_column(Float, nullable=True)
    default_shipping_cost: Mapped[float] = mapped_column(Float, default=0.0)
    trusted: Mapped[bool] = mapped_column(Boolean, default=True)
    penalty_score: Mapped[float] = mapped_column(Float, default=0.0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
    )

    offers: Mapped[list[Offer]] = relationship(back_populates="shop")
    optimization_run_items: Mapped[list[OptimizationRunItem]] = relationship(back_populates="shop")


class Offer(Base):
    __tablename__ = "offers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.id"))
    source_url: Mapped[str] = mapped_column(String(500))
    offer_title: Mapped[str] = mapped_column(String(255))
    manufacturer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    brand: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mpn: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ean_gtin: Mapped[str | None] = mapped_column(String(64), nullable=True)
    pack_qty: Mapped[float] = mapped_column(Float, default=1.0)
    pack_unit: Mapped[str] = mapped_column(String(64), default="unit")
    price: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(8), default="EUR")
    availability: Mapped[str] = mapped_column(String(64), default="unknown")
    shipping_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    minimum_order_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    lead_time_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    attributes_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    matched_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    last_checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    product: Mapped[Product] = relationship(back_populates="offers")
    shop: Mapped[Shop] = relationship(back_populates="offers")
    optimization_run_items: Mapped[list[OptimizationRunItem]] = relationship(back_populates="offer")


class ShoppingList(Base):
    __tablename__ = "shopping_lists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    shop_penalty: Mapped[float] = mapped_column(Float, default=10.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
    )

    items: Mapped[list[ShoppingListItem]] = relationship(
        back_populates="shopping_list",
        cascade="all, delete-orphan",
    )
    optimization_runs: Mapped[list[OptimizationRun]] = relationship(
        back_populates="shopping_list",
        cascade="all, delete-orphan",
    )


class ShoppingListItem(Base):
    __tablename__ = "shopping_list_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    shopping_list_id: Mapped[int] = mapped_column(
        ForeignKey("shopping_lists.id", ondelete="CASCADE")
    )
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    required_qty: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(64), default="unit")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
    )

    shopping_list: Mapped[ShoppingList] = relationship(back_populates="items")
    product: Mapped[Product] = relationship(back_populates="shopping_list_items")
    optimization_run_items: Mapped[list[OptimizationRunItem]] = relationship(
        back_populates="shopping_list_item"
    )


class OptimizationRun(Base):
    __tablename__ = "optimization_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    shopping_list_id: Mapped[int] = mapped_column(
        ForeignKey("shopping_lists.id", ondelete="CASCADE")
    )
    status: Mapped[str] = mapped_column(String(50), default="completed")
    shop_penalty: Mapped[float] = mapped_column(Float)
    total_items_price: Mapped[float] = mapped_column(Float)
    total_shipping: Mapped[float] = mapped_column(Float)
    total_score: Mapped[float] = mapped_column(Float)
    shop_count: Mapped[int] = mapped_column(Integer)
    summary_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    shopping_list: Mapped[ShoppingList] = relationship(back_populates="optimization_runs")
    items: Mapped[list[OptimizationRunItem]] = relationship(
        back_populates="optimization_run",
        cascade="all, delete-orphan",
    )


class OptimizationRunItem(Base):
    __tablename__ = "optimization_run_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    optimization_run_id: Mapped[int] = mapped_column(
        ForeignKey("optimization_runs.id", ondelete="CASCADE")
    )
    shopping_list_item_id: Mapped[int] = mapped_column(ForeignKey("shopping_list_items.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    offer_id: Mapped[int] = mapped_column(ForeignKey("offers.id"))
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.id"))
    quantity: Mapped[float] = mapped_column(Float)
    unit_price: Mapped[float] = mapped_column(Float)
    line_total: Mapped[float] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    optimization_run: Mapped[OptimizationRun] = relationship(back_populates="items")
    shopping_list_item: Mapped[ShoppingListItem] = relationship(
        back_populates="optimization_run_items"
    )
    product: Mapped[Product] = relationship(back_populates="optimization_run_items")
    offer: Mapped[Offer] = relationship(back_populates="optimization_run_items")
    shop: Mapped[Shop] = relationship(back_populates="optimization_run_items")
