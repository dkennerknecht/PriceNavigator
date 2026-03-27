from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_session
from app.repositories import shops as shop_repository
from app.schemas.common import DeleteResponse
from app.schemas.shops import ShopCreate, ShopRead, ShopUpdate

router = APIRouter(prefix="/shops", tags=["shops"])


@router.get("", response_model=list[ShopRead])
def get_shops(
    q: str | None = Query(default=None), session: Session = Depends(get_session)
) -> list[ShopRead]:
    return [ShopRead.model_validate(shop) for shop in shop_repository.list_shops(session, q=q)]


@router.post("", response_model=ShopRead, status_code=status.HTTP_201_CREATED)
def create_shop(payload: ShopCreate, session: Session = Depends(get_session)) -> ShopRead:
    return ShopRead.model_validate(shop_repository.create_shop(session, payload.model_dump()))


@router.put("/{shop_id}", response_model=ShopRead)
def update_shop(
    shop_id: int, payload: ShopUpdate, session: Session = Depends(get_session)
) -> ShopRead:
    shop = shop_repository.get_shop(session, shop_id)
    if shop is None:
        raise HTTPException(status_code=404, detail="Shop not found")
    return ShopRead.model_validate(shop_repository.update_shop(session, shop, payload.model_dump()))


@router.delete("/{shop_id}", response_model=DeleteResponse)
def delete_shop(shop_id: int, session: Session = Depends(get_session)) -> DeleteResponse:
    shop = shop_repository.get_shop(session, shop_id)
    if shop is None:
        raise HTTPException(status_code=404, detail="Shop not found")
    shop_repository.delete_shop(session, shop)
    return DeleteResponse(message="Shop deleted")
