from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_session
from app.repositories import offers as offer_repository
from app.repositories.products import get_product
from app.schemas.common import DeleteResponse
from app.schemas.offers import OfferRead, OfferSearchRequest, OfferSearchResponse, OfferUpdate
from app.services.offer_search import OfferSearchService

router = APIRouter(prefix="/offers", tags=["offers"])
offer_search_service = OfferSearchService()


@router.post("/search", response_model=OfferSearchResponse)
def search_offers(
    payload: OfferSearchRequest, session: Session = Depends(get_session)
) -> OfferSearchResponse:
    product_ids = payload.product_ids or (
        [payload.product_id] if payload.product_id is not None else []
    )
    products = []
    for product_id in product_ids:
        product = get_product(session, product_id)
        if product is not None:
            products.append(product)
    if not products:
        raise HTTPException(status_code=400, detail="At least one valid product_id is required")
    result = offer_search_service.search(session, products)
    return OfferSearchResponse(
        offers=[OfferRead.model_validate(offer) for offer in result.offers],
        created_count=result.created_count,
        warnings=result.warnings,
    )


@router.get("", response_model=list[OfferRead])
def get_offers(
    q: str | None = Query(default=None),
    product_id: int | None = Query(default=None),
    shop_id: int | None = Query(default=None),
    include_inactive: bool = Query(default=False),
    session: Session = Depends(get_session),
) -> list[OfferRead]:
    offers = offer_repository.list_offers(
        session,
        q=q,
        product_id=product_id,
        shop_id=shop_id,
        include_inactive=include_inactive,
    )
    return [OfferRead.model_validate(offer) for offer in offers]


@router.get("/{offer_id}", response_model=OfferRead)
def get_offer(offer_id: int, session: Session = Depends(get_session)) -> OfferRead:
    offer = offer_repository.get_offer(session, offer_id)
    if offer is None:
        raise HTTPException(status_code=404, detail="Offer not found")
    return OfferRead.model_validate(offer)


@router.put("/{offer_id}", response_model=OfferRead)
def update_offer(
    offer_id: int, payload: OfferUpdate, session: Session = Depends(get_session)
) -> OfferRead:
    offer = offer_repository.get_offer(session, offer_id)
    if offer is None:
        raise HTTPException(status_code=404, detail="Offer not found")
    return OfferRead.model_validate(
        offer_repository.update_offer(session, offer, payload.model_dump())
    )


@router.delete("/{offer_id}", response_model=DeleteResponse)
def delete_offer(offer_id: int, session: Session = Depends(get_session)) -> DeleteResponse:
    offer = offer_repository.get_offer(session, offer_id)
    if offer is None:
        raise HTTPException(status_code=404, detail="Offer not found")
    offer_repository.deactivate_offer(session, offer)
    return DeleteResponse(message="Offer deactivated")
