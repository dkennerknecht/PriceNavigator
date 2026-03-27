from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Product, ProductSource
from app.services.product_assets import apply_catalog_asset_fallbacks
from app.services.product_matching import prepare_product_payload


def list_products(
    session: Session, q: str | None = None, include_archived: bool = False
) -> list[Product]:
    statement = select(Product).order_by(Product.updated_at.desc())
    if not include_archived:
        statement = statement.where(Product.is_archived.is_(False))
    if q:
        like_query = f"%{q.lower()}%"
        statement = statement.where(
            Product.search_tokens.is_not(None),
            Product.search_tokens.ilike(like_query),
        )
    products = list(session.scalars(statement).all())
    changed = False
    for product in products:
        if apply_catalog_asset_fallbacks(product):
            session.add(product)
            changed = True
    if changed:
        session.commit()
    return products


def get_product(session: Session, product_id: int) -> Product | None:
    product = session.get(Product, product_id)
    if product is None:
        return None
    if apply_catalog_asset_fallbacks(product):
        session.add(product)
        session.commit()
        session.refresh(product)
    return product


def create_product(session: Session, payload: dict) -> Product:
    product = Product(**prepare_product_payload(payload))
    apply_catalog_asset_fallbacks(product)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def update_product(session: Session, product: Product, payload: dict) -> Product:
    prepared = prepare_product_payload(payload)
    for key, value in prepared.items():
        setattr(product, key, value)
    apply_catalog_asset_fallbacks(product)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def archive_product(session: Session, product: Product) -> Product:
    product.is_archived = True
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def attach_source(session: Session, product: Product, source_id: int) -> None:
    source = session.get(ProductSource, source_id)
    if source is None:
        return
    source.product_id = product.id
    session.add(source)
    session.commit()
