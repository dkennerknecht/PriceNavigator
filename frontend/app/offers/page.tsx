"use client";

import { startTransition, useEffect, useState } from "react";

import { DataTable } from "@/components/data-table";
import { OfferEditorModal } from "@/components/offer-editor-modal";
import { PageHeader } from "@/components/page-header";
import { apiClient, exportUrl } from "@/lib/api";
import { formatCurrency, formatDate } from "@/lib/format";
import type { Offer, Product, Shop } from "@/lib/types";

function pickDefaultSearchProductId(products: Product[], current: string): string {
  const currentMatch = products.find((product) => String(product.id) === current);
  if (currentMatch && !currentMatch.is_archived) {
    return current;
  }

  const firstActiveProduct = products.find((product) => !product.is_archived);
  if (firstActiveProduct) {
    return String(firstActiveProduct.id);
  }

  return currentMatch ? current : "";
}

export default function OffersPage() {
  const [offers, setOffers] = useState<Offer[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [shops, setShops] = useState<Shop[]>([]);
  const [selectedOffer, setSelectedOffer] = useState<Offer | null>(null);
  const [searchProductId, setSearchProductId] = useState<string>("");
  const [searchState, setSearchState] = useState<"idle" | "loading" | "success">("idle");
  const [searchFeedback, setSearchFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const searchableProducts = products.some((product) => !product.is_archived)
    ? products.filter((product) => !product.is_archived)
    : products;

  async function loadPage() {
    try {
      const [offerResult, productResult, shopResult] = await Promise.all([
        apiClient.listOffers({ include_inactive: true }),
        apiClient.listProducts({ include_archived: true }),
        apiClient.listShops(),
      ]);
      setOffers(offerResult);
      setProducts(productResult);
      setShops(shopResult);
      setSearchProductId((current) => pickDefaultSearchProductId(productResult, current));
      setSelectedOffer((current) =>
        current ? offerResult.find((offer) => offer.id === current.id) ?? null : null,
      );
      setError(null);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Offers konnten nicht geladen werden.");
    }
  }

  useEffect(() => {
    let active = true;

    Promise.all([
      apiClient.listOffers({ include_inactive: true }),
      apiClient.listProducts({ include_archived: true }),
      apiClient.listShops(),
    ])
      .then(([offerResult, productResult, shopResult]) => {
        if (!active) {
          return;
        }
        startTransition(() => {
          setOffers(offerResult);
          setProducts(productResult);
          setShops(shopResult);
          setSearchProductId((current) => pickDefaultSearchProductId(productResult, current));
          setSelectedOffer(null);
          setError(null);
        });
      })
      .catch((caughtError) => {
        if (!active) {
          return;
        }
        startTransition(() => {
          setError(
            caughtError instanceof Error
              ? caughtError.message
              : "Offers konnten nicht geladen werden.",
          );
        });
      });

    return () => {
      active = false;
    };
  }, []);

  async function saveOffer(formData: FormData) {
    if (!selectedOffer) {
      return;
    }
    const payload = {
      product_id: Number(formData.get("product_id")),
      shop_id: Number(formData.get("shop_id")),
      source_url: String(formData.get("source_url")),
      offer_title: String(formData.get("offer_title")),
      manufacturer: String(formData.get("manufacturer") ?? "") || null,
      brand: String(formData.get("brand") ?? "") || null,
      mpn: String(formData.get("mpn") ?? "") || null,
      ean_gtin: String(formData.get("ean_gtin") ?? "") || null,
      pack_qty: Number(formData.get("pack_qty") ?? 1),
      pack_unit: String(formData.get("pack_unit") ?? "unit"),
      price: Number(formData.get("price") ?? 0),
      currency: String(formData.get("currency") ?? "EUR"),
      availability: String(formData.get("availability") ?? "unknown"),
      shipping_cost: Number(formData.get("shipping_cost") ?? 0),
      minimum_order_value: null,
      lead_time_days: Number(formData.get("lead_time_days") ?? 0),
      attributes_json: JSON.parse(String(formData.get("attributes_json") ?? "{}")),
      matched_confidence: Number(formData.get("matched_confidence") ?? 0),
      is_active: formData.get("is_active") === "on",
    };
    await apiClient.updateOffer(selectedOffer.id, payload);
    setSelectedOffer(null);
    startTransition(() => void loadPage());
  }

  async function deactivateOffer(id: number) {
    if (!window.confirm("Offer deaktivieren?")) {
      return;
    }
    await apiClient.deleteOffer(id);
    startTransition(() => void loadPage());
  }

  async function clearOfferTable() {
    if (!offers.length) {
      setSearchState("idle");
      setSearchFeedback("Keine Offers zum Löschen vorhanden.");
      return;
    }
    if (!window.confirm("Wirklich die komplette Offer-Tabelle leeren?")) {
      return;
    }
    try {
      setError(null);
      const result = await apiClient.deleteAllOffers();
      setSelectedOffer(null);
      setSearchState("success");
      setSearchFeedback(
        result.deleted_count
          ? `${result.deleted_count} Offers gelöscht.`
          : "Offer-Tabelle geleert.",
      );
      startTransition(() => void loadPage());
    } catch (caughtError) {
      setSearchState("idle");
      setSearchFeedback(null);
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Offer-Tabelle konnte nicht geleert werden.",
      );
    }
  }

  async function triggerSearch() {
    if (!searchProductId) {
      setSearchState("idle");
      setSearchFeedback("Bitte zuerst ein Produkt wählen.");
      return;
    }
    try {
      setSearchState("loading");
      setSearchFeedback(null);
      setError(null);
      const result = await apiClient.searchOffers([Number(searchProductId)]);
      setSearchState("success");
      const warningText = result.warnings.length ? ` ${result.warnings.join(" ")}` : "";
      setSearchFeedback(
        result.created_count > 0
          ? `${result.created_count} Angebote neu geladen.${warningText}`
          : result.warnings[0] ?? "Für dieses Produkt wurden keine Angebote gefunden.",
      );
      startTransition(() => void loadPage());
    } catch (caughtError) {
      setSearchState("idle");
      setSearchFeedback(null);
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Angebots-Suche konnte nicht gestartet werden.",
      );
    }
  }

  return (
    <div className="page">
      <PageHeader
        title="Angebote"
        description="Angebotssuche bleibt gekapselt, schreibt aber echte Offer-Datensätze in die Datenbank."
        actions={[{ href: exportUrl("/export/offers.csv"), label: "CSV Export", variant: "ghost" }]}
      />
      {error ? <p className="error-text">{error}</p> : null}
      <section className="panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">Offer Provider</p>
            <h2>Angebote nachladen</h2>
          </div>
        </div>
        <div className="page-actions">
          <select
            value={searchProductId}
            onChange={(event) => {
              setSearchProductId(event.target.value);
              setSearchState("idle");
              setSearchFeedback(null);
            }}
          >
            {products.length === 0 ? <option value="">Keine Produkte vorhanden</option> : null}
            {searchableProducts.map((product) => (
              <option key={product.id} value={product.id}>
                {product.canonical_title}
              </option>
            ))}
          </select>
          <button
            className="button"
            type="button"
            onClick={() => void triggerSearch()}
            disabled={!searchProductId || searchState === "loading"}
          >
            {searchState === "loading" ? "Suche läuft ..." : "Angebots-Suche starten"}
          </button>
          <button
            className="button button-danger"
            type="button"
            onClick={() => void clearOfferTable()}
            disabled={searchState === "loading"}
          >
            Offer-Tabelle leeren
          </button>
        </div>
        {searchFeedback ? (
          <p className={searchState === "success" ? "callout-text" : "error-text"}>{searchFeedback}</p>
        ) : null}
      </section>

      <DataTable
        title="Offer Tabelle"
        description="Bearbeitung oeffnet sich als Dialog, damit die Tabelle die volle Breite nutzen kann."
        rows={offers}
        getRowKey={(offer) => offer.id}
        searchableText={(offer) =>
          [offer.offer_title, offer.mpn, offer.ean_gtin, offer.source_url].filter(Boolean).join(" ")
        }
        columns={[
          {
            key: "offer",
            label: "Offer",
            render: (offer) => (
              <div>
                <strong>{offer.offer_title}</strong>
                <p className="muted">
                  {products.find((product) => product.id === offer.product_id)?.canonical_title ?? "Produkt"}
                </p>
              </div>
            ),
          },
          {
            key: "shop",
            label: "Shop",
            render: (offer) => shops.find((shop) => shop.id === offer.shop_id)?.name ?? `#${offer.shop_id}`,
          },
          { key: "price", label: "Preis", render: (offer) => formatCurrency(offer.price) },
          { key: "checked", label: "Geprueft", render: (offer) => formatDate(offer.updated_at) },
          {
            key: "actions",
            label: "Aktionen",
            render: (offer) => (
              <div className="inline-actions">
                <button className="button button-ghost" type="button" onClick={() => setSelectedOffer(offer)}>
                  Bearbeiten
                </button>
                <button
                  className="button button-danger"
                  type="button"
                  onClick={() => void deactivateOffer(offer.id)}
                >
                  Deaktivieren
                </button>
              </div>
            ),
          },
        ]}
      />

      <OfferEditorModal
        offer={selectedOffer}
        products={products}
        shops={shops}
        onClose={() => setSelectedOffer(null)}
        onSave={saveOffer}
      />
    </div>
  );
}
