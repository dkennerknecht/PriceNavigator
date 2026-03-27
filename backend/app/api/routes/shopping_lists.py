from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_session
from app.repositories import shopping_lists as shopping_list_repository
from app.schemas.common import DeleteResponse
from app.schemas.shopping_lists import (
    ShoppingListCreate,
    ShoppingListDetailRead,
    ShoppingListItemCreate,
    ShoppingListItemRead,
    ShoppingListItemUpdate,
    ShoppingListRead,
    ShoppingListUpdate,
)

router = APIRouter(prefix="/shopping-lists", tags=["shopping-lists"])
item_router = APIRouter(prefix="/shopping-list-items", tags=["shopping-lists"])


@router.get("", response_model=list[ShoppingListRead])
def get_shopping_lists(
    q: str | None = Query(default=None),
    session: Session = Depends(get_session),
) -> list[ShoppingListRead]:
    return [
        ShoppingListRead.model_validate(shopping_list)
        for shopping_list in shopping_list_repository.list_shopping_lists(session, q=q)
    ]


@router.post("", response_model=ShoppingListRead, status_code=status.HTTP_201_CREATED)
def create_shopping_list(
    payload: ShoppingListCreate,
    session: Session = Depends(get_session),
) -> ShoppingListRead:
    return ShoppingListRead.model_validate(
        shopping_list_repository.create_shopping_list(session, payload.model_dump())
    )


@router.get("/{shopping_list_id}", response_model=ShoppingListDetailRead)
def get_shopping_list(
    shopping_list_id: int,
    session: Session = Depends(get_session),
) -> ShoppingListDetailRead:
    shopping_list = shopping_list_repository.get_shopping_list(session, shopping_list_id)
    if shopping_list is None:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    return ShoppingListDetailRead.model_validate(shopping_list)


@router.put("/{shopping_list_id}", response_model=ShoppingListRead)
def update_shopping_list(
    shopping_list_id: int,
    payload: ShoppingListUpdate,
    session: Session = Depends(get_session),
) -> ShoppingListRead:
    shopping_list = shopping_list_repository.get_shopping_list(session, shopping_list_id)
    if shopping_list is None:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    return ShoppingListRead.model_validate(
        shopping_list_repository.update_shopping_list(session, shopping_list, payload.model_dump())
    )


@router.delete("/{shopping_list_id}", response_model=DeleteResponse)
def delete_shopping_list(
    shopping_list_id: int,
    session: Session = Depends(get_session),
) -> DeleteResponse:
    shopping_list = shopping_list_repository.get_shopping_list(session, shopping_list_id)
    if shopping_list is None:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    shopping_list_repository.delete_shopping_list(session, shopping_list)
    return DeleteResponse(message="Shopping list deleted")


@router.post(
    "/{shopping_list_id}/items",
    response_model=ShoppingListItemRead,
    status_code=status.HTTP_201_CREATED,
)
def add_shopping_list_item(
    shopping_list_id: int,
    payload: ShoppingListItemCreate,
    session: Session = Depends(get_session),
) -> ShoppingListItemRead:
    shopping_list = shopping_list_repository.get_shopping_list(session, shopping_list_id)
    if shopping_list is None:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    item = shopping_list_repository.add_item(session, shopping_list, payload.model_dump())
    return ShoppingListItemRead.model_validate(item)


@item_router.put("/{item_id}", response_model=ShoppingListItemRead)
def update_shopping_list_item(
    item_id: int,
    payload: ShoppingListItemUpdate,
    session: Session = Depends(get_session),
) -> ShoppingListItemRead:
    item = shopping_list_repository.get_shopping_list_item(session, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Shopping list item not found")
    updated = shopping_list_repository.update_item(session, item, payload.model_dump())
    return ShoppingListItemRead.model_validate(updated)


@item_router.delete("/{item_id}", response_model=DeleteResponse)
def delete_shopping_list_item(
    item_id: int, session: Session = Depends(get_session)
) -> DeleteResponse:
    item = shopping_list_repository.get_shopping_list_item(session, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Shopping list item not found")
    shopping_list_repository.delete_item(session, item)
    return DeleteResponse(message="Shopping list item deleted")
