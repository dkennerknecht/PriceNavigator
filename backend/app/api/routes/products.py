from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_session
from app.repositories import product_sources as product_source_repository
from app.repositories import products as product_repository
from app.schemas.common import DeleteResponse
from app.schemas.products import (
    ProductCreate,
    ProductRead,
    ProductResolveInput,
    ProductResolveResponse,
    ProductSourceRead,
    ProductSourceUpdate,
    ProductUpdate,
)
from app.services.product_resolver import ProductResolutionService

router = APIRouter(prefix="/products", tags=["products"])
source_router = APIRouter(prefix="/product-sources", tags=["product-sources"])
resolution_service = ProductResolutionService()


@router.post("/resolve", response_model=ProductResolveResponse)
def resolve_product(
    payload: ProductResolveInput, session: Session = Depends(get_session)
) -> ProductResolveResponse:
    result = resolution_service.resolve(session, payload.model_dump())
    return ProductResolveResponse(
        candidate=result.candidate,
        source_id=result.source_id,
        resolver_type=result.resolver_type,
        match_strategy=result.match_strategy,
        confidence=result.confidence,
        matched_product_id=result.matched_product_id,
        requires_manual_review=result.requires_manual_review,
    )


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, session: Session = Depends(get_session)) -> ProductRead:
    product = product_repository.create_product(session, payload.model_dump(exclude={"source_id"}))
    if payload.source_id is not None:
        product_repository.attach_source(session, product, payload.source_id)
    return ProductRead.model_validate(product)


@router.get("", response_model=list[ProductRead])
def get_products(
    q: str | None = Query(default=None),
    include_archived: bool = Query(default=False),
    session: Session = Depends(get_session),
) -> list[ProductRead]:
    return [
        ProductRead.model_validate(product)
        for product in product_repository.list_products(session, q, include_archived)
    ]


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, session: Session = Depends(get_session)) -> ProductRead:
    product = product_repository.get_product(session, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductRead.model_validate(product)


@router.put("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    session: Session = Depends(get_session),
) -> ProductRead:
    product = product_repository.get_product(session, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    updated = product_repository.update_product(session, product, payload.model_dump())
    return ProductRead.model_validate(updated)


@router.delete("/{product_id}", response_model=DeleteResponse)
def delete_product(product_id: int, session: Session = Depends(get_session)) -> DeleteResponse:
    product = product_repository.get_product(session, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    product_repository.archive_product(session, product)
    return DeleteResponse(message="Product archived")


@source_router.get("", response_model=list[ProductSourceRead])
def get_sources(
    q: str | None = Query(default=None),
    product_id: int | None = Query(default=None),
    source_id: int | None = Query(default=None),
    session: Session = Depends(get_session),
) -> list[ProductSourceRead]:
    return [
        ProductSourceRead.model_validate(source)
        for source in product_source_repository.list_sources(
            session, q=q, product_id=product_id, source_id=source_id
        )
    ]


@source_router.get("/{source_id}", response_model=ProductSourceRead)
def get_source(source_id: int, session: Session = Depends(get_session)) -> ProductSourceRead:
    source = product_source_repository.get_source(session, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Product source not found")
    return ProductSourceRead.model_validate(source)


@source_router.put("/{source_id}", response_model=ProductSourceRead)
def update_source(
    source_id: int,
    payload: ProductSourceUpdate,
    session: Session = Depends(get_session),
) -> ProductSourceRead:
    source = product_source_repository.get_source(session, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Product source not found")
    updated = product_source_repository.update_source(session, source, payload.model_dump())
    return ProductSourceRead.model_validate(updated)


@source_router.delete("/{source_id}", response_model=DeleteResponse)
def delete_source(source_id: int, session: Session = Depends(get_session)) -> DeleteResponse:
    source = product_source_repository.get_source(session, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Product source not found")
    product_source_repository.delete_source(session, source)
    return DeleteResponse(message="Product source deleted")
