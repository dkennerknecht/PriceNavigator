from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.entities import ShoppingList, ShoppingListItem


def list_shopping_lists(session: Session, q: str | None = None) -> list[ShoppingList]:
    statement = select(ShoppingList).order_by(ShoppingList.updated_at.desc())
    if q:
        like_query = f"%{q}%"
        statement = statement.where(
            ShoppingList.name.ilike(like_query) | ShoppingList.description.ilike(like_query)
        )
    return list(session.scalars(statement).all())


def get_shopping_list(session: Session, shopping_list_id: int) -> ShoppingList | None:
    statement = (
        select(ShoppingList)
        .where(ShoppingList.id == shopping_list_id)
        .options(selectinload(ShoppingList.items).selectinload(ShoppingListItem.product))
    )
    return session.scalar(statement)


def create_shopping_list(session: Session, payload: dict) -> ShoppingList:
    shopping_list = ShoppingList(**payload)
    session.add(shopping_list)
    session.commit()
    session.refresh(shopping_list)
    return shopping_list


def update_shopping_list(
    session: Session, shopping_list: ShoppingList, payload: dict
) -> ShoppingList:
    for key, value in payload.items():
        setattr(shopping_list, key, value)
    session.add(shopping_list)
    session.commit()
    session.refresh(shopping_list)
    return shopping_list


def delete_shopping_list(session: Session, shopping_list: ShoppingList) -> None:
    session.delete(shopping_list)
    session.commit()


def get_shopping_list_item(session: Session, item_id: int) -> ShoppingListItem | None:
    statement = (
        select(ShoppingListItem)
        .where(ShoppingListItem.id == item_id)
        .options(selectinload(ShoppingListItem.product))
    )
    return session.scalar(statement)


def add_item(session: Session, shopping_list: ShoppingList, payload: dict) -> ShoppingListItem:
    item = ShoppingListItem(shopping_list_id=shopping_list.id, **payload)
    session.add(item)
    session.commit()
    statement = (
        select(ShoppingListItem)
        .where(ShoppingListItem.id == item.id)
        .options(selectinload(ShoppingListItem.product))
    )
    return session.scalar(statement)


def update_item(session: Session, item: ShoppingListItem, payload: dict) -> ShoppingListItem:
    for key, value in payload.items():
        setattr(item, key, value)
    session.add(item)
    session.commit()
    statement = (
        select(ShoppingListItem)
        .where(ShoppingListItem.id == item.id)
        .options(selectinload(ShoppingListItem.product))
    )
    return session.scalar(statement)


def delete_item(session: Session, item: ShoppingListItem) -> None:
    session.delete(item)
    session.commit()
