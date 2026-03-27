from __future__ import annotations

from urllib.parse import urlparse

from app.models.entities import Product
from app.services.catalog import CATALOG_PRODUCTS, CatalogProduct

IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".bmp", ".avif")


def _looks_like_image_url(url: str | None) -> bool:
    if not url:
        return False

    normalized = url.strip().lower()
    if normalized.startswith("data:image/"):
        return True

    parsed = urlparse(normalized)
    return parsed.path.endswith(IMAGE_SUFFIXES)


def _match_catalog_product(product: Product) -> CatalogProduct | None:
    if product.ean_gtin:
        for catalog_product in CATALOG_PRODUCTS:
            if catalog_product.ean_gtin == product.ean_gtin:
                return catalog_product

    manufacturer = (product.manufacturer or "").strip().lower()
    mpn = (product.mpn or "").strip().upper()
    if manufacturer and mpn:
        for catalog_product in CATALOG_PRODUCTS:
            if (
                catalog_product.manufacturer.strip().lower() == manufacturer
                and catalog_product.mpn.strip().upper() == mpn
            ):
                return catalog_product

    return None


def apply_catalog_asset_fallbacks(product: Product) -> bool:
    if _looks_like_image_url(product.image_url):
        return False

    catalog_product = _match_catalog_product(product)
    if catalog_product is None or catalog_product.image_url == product.image_url:
        return False

    product.image_url = catalog_product.image_url
    return True
