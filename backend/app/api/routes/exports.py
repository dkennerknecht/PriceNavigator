from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.api.deps import get_session
from app.repositories import offers as offer_repository
from app.repositories import products as product_repository
from app.repositories import shopping_lists as shopping_list_repository
from app.services.export import offers_to_csv, products_to_csv, shopping_list_to_csv

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/products.csv", response_class=PlainTextResponse)
def export_products(session: Session = Depends(get_session)) -> str:
    return products_to_csv(product_repository.list_products(session, include_archived=True))


@router.get("/offers.csv", response_class=PlainTextResponse)
def export_offers(session: Session = Depends(get_session)) -> str:
    return offers_to_csv(offer_repository.list_offers(session, include_inactive=True))


@router.get("/shopping-list/{shopping_list_id}.csv", response_class=PlainTextResponse)
def export_shopping_list(shopping_list_id: int, session: Session = Depends(get_session)) -> str:
    shopping_list = shopping_list_repository.get_shopping_list(session, shopping_list_id)
    if shopping_list is None:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    return shopping_list_to_csv(shopping_list)
