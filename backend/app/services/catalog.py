from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import quote


@dataclass(frozen=True)
class CatalogProduct:
    canonical_title: str
    manufacturer: str
    brand: str
    mpn: str
    ean_gtin: str
    category: str
    description_short: str
    attributes_json: dict[str, Any]
    datasheet_url: str
    image_url: str
    source_url: str


def _mock_image_url(title: str, manufacturer: str, mpn: str, accent: str) -> str:
    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900" role="img" aria-label="{title}">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#112a24" />
      <stop offset="100%" stop-color="{accent}" />
    </linearGradient>
  </defs>
  <rect width="1200" height="900" rx="56" fill="url(#bg)" />
  <circle cx="978" cy="184" r="128" fill="rgba(255,255,255,0.10)" />
  <circle cx="1040" cy="734" r="188" fill="rgba(255,255,255,0.08)" />
  <text x="86" y="126" fill="#f5ede0" font-family="Arial, sans-serif" font-size="34">
    PriceNavigator Mock Catalog
  </text>
  <text x="86" y="318" fill="#ffffff" font-family="Arial, sans-serif" font-size="74" font-weight="700">
    {manufacturer}
  </text>
  <text x="86" y="418" fill="#f5ede0" font-family="Arial, sans-serif" font-size="54" font-weight="700">
    {mpn}
  </text>
  <foreignObject x="86" y="474" width="760" height="220">
    <div xmlns="http://www.w3.org/1999/xhtml"
      style="color:#f5ede0;font-family:Arial,sans-serif;font-size:42px;line-height:1.25;">
      {title}
    </div>
  </foreignObject>
</svg>
""".strip()
    return f"data:image/svg+xml;charset=UTF-8,{quote(svg)}"


CATALOG_PRODUCTS: list[CatalogProduct] = [
    CatalogProduct(
        canonical_title="Milwaukee M18 FUEL Drill Driver",
        manufacturer="Milwaukee",
        brand="Milwaukee",
        mpn="M18FDD3-0",
        ean_gtin="4058546375941",
        category="Power Tools",
        description_short="Brushless 18V drill driver as bare tool.",
        attributes_json={"voltage": "18V", "variant": "bare tool", "tool_type": "drill driver"},
        datasheet_url="https://docs.mock/milwaukee-m18fdd3-0.pdf",
        image_url=_mock_image_url(
            "M18 FUEL Drill Driver",
            "Milwaukee",
            "M18FDD3-0",
            "#b71c1c",
        ),
        source_url="https://catalog.mock/toolhub/milwaukee-m18fdd3-0",
    ),
    CatalogProduct(
        canonical_title="Bosch GSR 12V-35 FC FlexiClick",
        manufacturer="Bosch",
        brand="Bosch Professional",
        mpn="06019H3000",
        ean_gtin="3165140958669",
        category="Power Tools",
        description_short="12V FlexiClick drill driver system without battery.",
        attributes_json={"voltage": "12V", "variant": "bare tool", "tool_type": "drill driver"},
        datasheet_url="https://docs.mock/bosch-06019h3000.pdf",
        image_url=_mock_image_url(
            "GSR 12V-35 FC FlexiClick",
            "Bosch Professional",
            "06019H3000",
            "#0f6eb6",
        ),
        source_url="https://catalog.mock/toolhub/bosch-gsr-12v-35-fc",
    ),
    CatalogProduct(
        canonical_title="WAGO 221-413 Compact Splicing Connector",
        manufacturer="WAGO",
        brand="WAGO",
        mpn="221-413",
        ean_gtin="4050821808441",
        category="Electrical Connector",
        description_short="3-port compact splicing connector.",
        attributes_json={"pole_count": "3", "series": "221", "pack_reference": "50 pcs"},
        datasheet_url="https://docs.mock/wago-221-413.pdf",
        image_url=_mock_image_url(
            "221-413 Compact Splicing Connector",
            "WAGO",
            "221-413",
            "#f59f00",
        ),
        source_url="https://catalog.mock/electro/wago-221-413",
    ),
    CatalogProduct(
        canonical_title="Phoenix Contact QUINT4 Power Supply 24V 5A",
        manufacturer="Phoenix Contact",
        brand="Phoenix Contact",
        mpn="2904601",
        ean_gtin="4046356906060",
        category="Power Supply",
        description_short="DIN rail power supply with 24V/5A output.",
        attributes_json={"output_voltage": "24V", "output_current": "5A", "series": "QUINT4"},
        datasheet_url="https://docs.mock/phoenix-2904601.pdf",
        image_url=_mock_image_url(
            "QUINT4 Power Supply 24V 5A",
            "Phoenix Contact",
            "2904601",
            "#008c95",
        ),
        source_url="https://catalog.mock/electro/phoenix-quint4-2904601",
    ),
    CatalogProduct(
        canonical_title="Harting Han 3A Hood Top Entry",
        manufacturer="Harting",
        brand="Harting",
        mpn="19300060447",
        ean_gtin="5713140106100",
        category="Industrial Connector",
        description_short="Han 3A hood with top entry and metal housing.",
        attributes_json={"size": "3A", "entry": "top", "housing": "metal"},
        datasheet_url="https://docs.mock/harting-19300060447.pdf",
        image_url=_mock_image_url(
            "Han 3A Hood Top Entry",
            "Harting",
            "19300060447",
            "#f28c28",
        ),
        source_url="https://catalog.mock/industrial/harting-19300060447",
    ),
    CatalogProduct(
        canonical_title="Hager univers Enclosure IP44 1400x550x205 mm",
        manufacturer="Hager",
        brand="Hager",
        mpn="FP92TN2",
        ean_gtin="3250612668090",
        category="Electrical Enclosure",
        description_short="Empty univers enclosure, IP44, class I, 1400x550x205 mm.",
        attributes_json={
            "height_mm": 1400,
            "width_mm": 550,
            "depth_mm": 205,
            "ip_rating": "IP44",
            "protection_class": "Class I",
            "series": "univers",
            "is_empty": True,
        },
        datasheet_url="https://hager.com/ie/catalogue/products/fp92tn2-encl-univers-ip44-cl-1-1400x550x205mm",
        image_url="https://assets.hager.com/step-content/P/HA_16209054/11/std.lang.all/FP92TN2.webp",
        source_url="https://hager.com/ie/catalogue/products/fp92tn2-encl-univers-ip44-cl-1-1400x550x205mm",
    ),
]


MOCK_SHOPS: list[dict[str, Any]] = [
    {
        "name": "ToolSource",
        "domain": "toolsource.example",
        "shipping_free_threshold": 150.0,
        "default_shipping_cost": 5.9,
        "trusted": True,
        "penalty_score": 1.0,
        "notes": "Strong power tools assortment.",
    },
    {
        "name": "ElectroMax",
        "domain": "electromax.example",
        "shipping_free_threshold": 120.0,
        "default_shipping_cost": 4.9,
        "trusted": True,
        "penalty_score": 0.7,
        "notes": "Broad electrical inventory.",
    },
    {
        "name": "IndustrialHub",
        "domain": "industrialhub.example",
        "shipping_free_threshold": 200.0,
        "default_shipping_cost": 6.5,
        "trusted": True,
        "penalty_score": 1.5,
        "notes": "Industrial connectors and enclosure parts.",
    },
]


MOCK_OFFERS: list[dict[str, Any]] = [
    {
        "mpn": "M18FDD3-0",
        "shop_domain": "toolsource.example",
        "source_url": "https://toolsource.example/milwaukee-m18fdd3-0",
        "offer_title": "Milwaukee M18 FUEL Drill Driver bare tool",
        "price": 119.0,
        "shipping_cost": 5.9,
        "availability": "in_stock",
        "lead_time_days": 2,
    },
    {
        "mpn": "M18FDD3-0",
        "shop_domain": "electromax.example",
        "source_url": "https://electromax.example/milwaukee-m18fdd3-0",
        "offer_title": "Milwaukee M18 FUEL Drill Driver",
        "price": 123.5,
        "shipping_cost": 4.9,
        "availability": "in_stock",
        "lead_time_days": 1,
    },
    {
        "mpn": "06019H3000",
        "shop_domain": "toolsource.example",
        "source_url": "https://toolsource.example/bosch-06019h3000",
        "offer_title": "Bosch GSR 12V-35 FC FlexiClick",
        "price": 149.0,
        "shipping_cost": 5.9,
        "availability": "in_stock",
        "lead_time_days": 2,
    },
    {
        "mpn": "06019H3000",
        "shop_domain": "industrialhub.example",
        "source_url": "https://industrialhub.example/bosch-06019h3000",
        "offer_title": "Bosch GSR 12V-35 FC",
        "price": 158.0,
        "shipping_cost": 6.5,
        "availability": "in_stock",
        "lead_time_days": 4,
    },
    {
        "mpn": "221-413",
        "shop_domain": "electromax.example",
        "source_url": "https://electromax.example/wago-221-413",
        "offer_title": "WAGO 221-413 Compact Splicing Connector",
        "price": 7.9,
        "shipping_cost": 4.9,
        "availability": "in_stock",
        "lead_time_days": 1,
    },
    {
        "mpn": "221-413",
        "shop_domain": "industrialhub.example",
        "source_url": "https://industrialhub.example/wago-221-413",
        "offer_title": "WAGO 221-413 Compact Splicing Connector",
        "price": 8.5,
        "shipping_cost": 6.5,
        "availability": "in_stock",
        "lead_time_days": 2,
    },
    {
        "mpn": "221-413",
        "shop_domain": "toolsource.example",
        "source_url": "https://toolsource.example/wago-221-413",
        "offer_title": "WAGO 221-413 Compact Splicing Connector",
        "price": 8.9,
        "shipping_cost": 5.9,
        "availability": "in_stock",
        "lead_time_days": 3,
    },
    {
        "mpn": "2904601",
        "shop_domain": "electromax.example",
        "source_url": "https://electromax.example/phoenix-2904601",
        "offer_title": "Phoenix Contact QUINT4 24V 5A",
        "price": 189.0,
        "shipping_cost": 0.0,
        "availability": "in_stock",
        "lead_time_days": 2,
    },
    {
        "mpn": "2904601",
        "shop_domain": "industrialhub.example",
        "source_url": "https://industrialhub.example/phoenix-2904601",
        "offer_title": "Phoenix Contact QUINT4 Power Supply",
        "price": 194.0,
        "shipping_cost": 6.5,
        "availability": "in_stock",
        "lead_time_days": 4,
    },
    {
        "mpn": "19300060447",
        "shop_domain": "industrialhub.example",
        "source_url": "https://industrialhub.example/harting-19300060447",
        "offer_title": "Harting Han 3A Hood Top Entry",
        "price": 13.5,
        "shipping_cost": 6.5,
        "availability": "in_stock",
        "lead_time_days": 2,
    },
    {
        "mpn": "19300060447",
        "shop_domain": "electromax.example",
        "source_url": "https://electromax.example/harting-19300060447",
        "offer_title": "Harting Han 3A Hood",
        "price": 14.2,
        "shipping_cost": 4.9,
        "availability": "in_stock",
        "lead_time_days": 3,
    },
    {
        "mpn": "19300060447",
        "shop_domain": "toolsource.example",
        "source_url": "https://toolsource.example/harting-19300060447",
        "offer_title": "Harting Han 3A Hood Top Entry",
        "price": 15.1,
        "shipping_cost": 5.9,
        "availability": "in_stock",
        "lead_time_days": 5,
    },
    {
        "mpn": "FP92TN2",
        "shop_domain": "electromax.example",
        "source_url": "https://electromax.example/hager-fp92tn2",
        "offer_title": "Hager univers Enclosure IP44 1400x550x205 mm",
        "price": 394.0,
        "shipping_cost": 4.9,
        "availability": "in_stock",
        "lead_time_days": 2,
    },
    {
        "mpn": "FP92TN2",
        "shop_domain": "industrialhub.example",
        "source_url": "https://industrialhub.example/hager-fp92tn2",
        "offer_title": "Hager univers Enclosure FP92TN2",
        "price": 389.0,
        "shipping_cost": 0.0,
        "availability": "in_stock",
        "lead_time_days": 4,
    },
    {
        "mpn": "FP92TN2",
        "shop_domain": "toolsource.example",
        "source_url": "https://toolsource.example/hager-fp92tn2",
        "offer_title": "Hager univers enclosure FP92TN2",
        "price": 401.0,
        "shipping_cost": 5.9,
        "availability": "limited",
        "lead_time_days": 5,
    },
]


def product_catalog_index() -> dict[str, CatalogProduct]:
    return {product.mpn: product for product in CATALOG_PRODUCTS}
