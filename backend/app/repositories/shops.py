from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Shop


def list_shops(session: Session, q: str | None = None) -> list[Shop]:
    statement = select(Shop).order_by(Shop.name.asc())
    if q:
        like_query = f"%{q}%"
        statement = statement.where(Shop.name.ilike(like_query) | Shop.domain.ilike(like_query))
    return list(session.scalars(statement).all())


def get_shop(session: Session, shop_id: int) -> Shop | None:
    return session.get(Shop, shop_id)


def get_shop_by_domain(session: Session, domain: str) -> Shop | None:
    statement = select(Shop).where(Shop.domain == domain)
    return session.scalar(statement)


def create_shop(session: Session, payload: dict) -> Shop:
    shop = Shop(**payload)
    session.add(shop)
    session.commit()
    session.refresh(shop)
    return shop


def update_shop(session: Session, shop: Shop, payload: dict) -> Shop:
    for key, value in payload.items():
        setattr(shop, key, value)
    session.add(shop)
    session.commit()
    session.refresh(shop)
    return shop


def delete_shop(session: Session, shop: Shop) -> None:
    session.delete(shop)
    session.commit()
