from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import ProductSource


def list_sources(
    session: Session,
    q: str | None = None,
    product_id: int | None = None,
    source_id: int | None = None,
) -> list[ProductSource]:
    statement = select(ProductSource).order_by(ProductSource.created_at.desc())
    if source_id is not None:
        statement = statement.where(ProductSource.id == source_id)
    if product_id is not None:
        statement = statement.where(ProductSource.product_id == product_id)
    if q:
        like_query = f"%{q}%"
        statement = statement.where(
            ProductSource.source_value.ilike(like_query)
            | ProductSource.source_type.ilike(like_query)
            | ProductSource.raw_title.ilike(like_query)
        )
    return list(session.scalars(statement).all())


def get_source(session: Session, source_id: int) -> ProductSource | None:
    return session.get(ProductSource, source_id)


def update_source(session: Session, source: ProductSource, payload: dict) -> ProductSource:
    for key, value in payload.items():
        setattr(source, key, value)
    session.add(source)
    session.commit()
    session.refresh(source)
    return source


def delete_source(session: Session, source: ProductSource) -> None:
    session.delete(source)
    session.commit()
