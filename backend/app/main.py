from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import exports, health, offers, optimization, products, shopping_lists, shops
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(products.router, prefix=settings.api_prefix)
app.include_router(products.source_router, prefix=settings.api_prefix)
app.include_router(shops.router, prefix=settings.api_prefix)
app.include_router(offers.router, prefix=settings.api_prefix)
app.include_router(shopping_lists.router, prefix=settings.api_prefix)
app.include_router(shopping_lists.item_router, prefix=settings.api_prefix)
app.include_router(optimization.router, prefix=settings.api_prefix)
app.include_router(exports.router, prefix=settings.api_prefix)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "PriceNavigator API"}
