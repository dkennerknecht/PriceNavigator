from __future__ import annotations

from app.models.entities import Product
from app.services.product_matching import find_existing_product, prepare_product_payload


def _create_product(session, **payload):
    product = Product(**prepare_product_payload(payload))
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def test_matching_prefers_ean(session):
    existing = _create_product(
        session,
        canonical_title="Milwaukee Drill Driver",
        manufacturer="Milwaukee",
        brand="Milwaukee",
        mpn="M18FDD3-0",
        ean_gtin="4058546375941",
        category="Power Tools",
        description_short="Existing product",
        attributes_json={"voltage": "18V"},
    )

    matched, strategy = find_existing_product(
        session,
        {
            "canonical_title": "Different title",
            "manufacturer": "Other",
            "mpn": "OTHER-123",
            "ean_gtin": "4058546375941",
            "attributes_json": {},
        },
    )

    assert matched is not None
    assert matched.id == existing.id
    assert strategy == "ean"


def test_matching_uses_manufacturer_and_mpn(session):
    existing = _create_product(
        session,
        canonical_title="Bosch FlexiClick",
        manufacturer="Bosch",
        brand="Bosch Professional",
        mpn="06019H3000",
        ean_gtin=None,
        category="Power Tools",
        description_short="Existing product",
        attributes_json={"voltage": "12V"},
    )

    matched, strategy = find_existing_product(
        session,
        {
            "canonical_title": "Bosch GSR 12V-35 FC",
            "manufacturer": "bosch",
            "mpn": "06019H3000",
            "ean_gtin": None,
            "attributes_json": {"voltage": "12V"},
        },
    )

    assert matched is not None
    assert matched.id == existing.id
    assert strategy == "manufacturer_mpn"


def test_matching_falls_back_to_title_and_attributes(session):
    existing = _create_product(
        session,
        canonical_title="WAGO 221-413 Compact Splicing Connector",
        manufacturer="WAGO",
        brand="WAGO",
        mpn=None,
        ean_gtin=None,
        category="Electrical Connector",
        description_short="Existing product",
        attributes_json={"pole_count": "3", "series": "221"},
    )

    matched, strategy = find_existing_product(
        session,
        {
            "canonical_title": "WAGO 221-413 Compact Splicing Connector",
            "manufacturer": "WAGO",
            "mpn": None,
            "ean_gtin": None,
            "attributes_json": {"series": "221", "pole_count": "3"},
        },
    )

    assert matched is not None
    assert matched.id == existing.id
    assert strategy == "manufacturer_title_attributes"
