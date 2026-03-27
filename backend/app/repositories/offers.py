from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload

from app.models.entities import Offer


def list_offers(
    session: Session,
    q: str | None = None,
    product_id: int | None = None,
    shop_id: int | None = None,
    include_inactive: bool = False,
) -> list[Offer]:
    statement = (
        select(Offer)
        .options(joinedload(Offer.shop), joinedload(Offer.product))
        .order_by(Offer.updated_at.desc())
    )
    if not include_inactive:
        statement = statement.where(Offer.is_active.is_(True))
    if product_id is not None:
        statement = statement.where(Offer.product_id == product_id)
    if shop_id is not None:
        statement = statement.where(Offer.shop_id == shop_id)
    if q:
        like_query = f"%{q}%"
        statement = statement.where(
            Offer.offer_title.ilike(like_query) | Offer.source_url.ilike(like_query)
        )
    return list(session.scalars(statement).unique().all())


def get_offer(session: Session, offer_id: int) -> Offer | None:
    return session.get(Offer, offer_id)


def find_offer_by_source(
    session: Session, product_id: int, shop_id: int, source_url: str
) -> Offer | None:
    statement = select(Offer).where(
        Offer.product_id == product_id,
        Offer.shop_id == shop_id,
        Offer.source_url == source_url,
    )
    return session.scalar(statement)


def hard_delete_offers_for_products(session: Session, product_ids: list[int]) -> int:
    if not product_ids:
        return 0

    statement = delete(Offer).where(Offer.product_id.in_(product_ids))
    result = session.execute(statement)
    session.commit()
    return result.rowcount or 0


def save_offer(session: Session, payload: dict) -> Offer:
    existing = find_offer_by_source(
        session, payload["product_id"], payload["shop_id"], payload["source_url"]
    )
    if existing is None:
        offer = Offer(**payload)
        session.add(offer)
    else:
        offer = existing
        for key, value in payload.items():
            setattr(offer, key, value)
        session.add(offer)
    session.commit()
    session.refresh(offer)
    return offer


def update_offer(session: Session, offer: Offer, payload: dict) -> Offer:
    for key, value in payload.items():
        setattr(offer, key, value)
    session.add(offer)
    session.commit()
    session.refresh(offer)
    return offer


def deactivate_offer(session: Session, offer: Offer) -> Offer:
    offer.is_active = False
    session.add(offer)
    session.commit()
    session.refresh(offer)
    return offer
