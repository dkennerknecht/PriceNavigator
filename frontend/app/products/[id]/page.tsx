"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { startTransition, useEffect, useState } from "react";

import { DataTable } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import { ProductImagePreview } from "@/components/product-image-preview";
import { apiClient } from "@/lib/api";
import { formatCurrency, toJsonText } from "@/lib/format";
import type { Offer, Product, ProductSource } from "@/lib/types";

export default function ProductDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const productId = Number(params.id);
  const [product, setProduct] = useState<Product | null>(null);
  const [sources, setSources] = useState<ProductSource[]>([]);
  const [offers, setOffers] = useState<Offer[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function loadPage() {
    try {
      const [productResult, sourceResult, offerResult] = await Promise.all([
        apiClient.getProduct(productId),
        apiClient.listProductSources({ product_id: productId }),
        apiClient.listOffers({ product_id: productId, include_inactive: true }),
      ]);
      setProduct(productResult);
      setSources(sourceResult);
      setOffers(offerResult);
      setError(null);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Produktdetail konnte nicht geladen werden.",
      );
    }
  }

  useEffect(() => {
    let active = true;

    Promise.all([
      apiClient.getProduct(productId),
      apiClient.listProductSources({ product_id: productId }),
      apiClient.listOffers({ product_id: productId, include_inactive: true }),
    ])
      .then(([productResult, sourceResult, offerResult]) => {
        if (!active) {
          return;
        }
        startTransition(() => {
          setProduct(productResult);
          setSources(sourceResult);
          setOffers(offerResult);
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
              : "Produktdetail konnte nicht geladen werden.",
          );
        });
      });

    return () => {
      active = false;
    };
  }, [productId]);

  async function searchOffers() {
    await apiClient.searchOffers([productId]);
    void loadPage();
  }

  async function archiveProduct() {
    if (!window.confirm("Produkt archivieren?")) {
      return;
    }
    await apiClient.deleteProduct(productId);
    router.push("/products");
  }

  if (!product) {
    return (
      <div className="page">
        <PageHeader title="Produktdetail" description="Produkt wird geladen." />
        {error ? <p className="error-text">{error}</p> : <p className="muted">Lade Daten ...</p>}
      </div>
    );
  }

  return (
    <div className="page">
      <PageHeader
        title={product.canonical_title}
        description="Detailansicht mit Quellen, Angeboten und manueller Nachbearbeitung."
        actions={[
          { href: `/products/${product.id}/edit`, label: "Bearbeiten" },
          { href: "/offers", label: "Angebote öffnen", variant: "ghost" },
        ]}
      />
      {error ? <p className="error-text">{error}</p> : null}

      <section className="split-grid">
        <article className="panel">
          <p className="eyebrow">Stammdaten</p>
          <h2>{product.canonical_title}</h2>
          <div className="form-grid">
            <div>
              <strong>Hersteller</strong>
              <p>{product.manufacturer ?? "—"}</p>
            </div>
            <div>
              <strong>Brand</strong>
              <p>{product.brand ?? "—"}</p>
            </div>
            <div>
              <strong>MPN</strong>
              <p>{product.mpn ?? "—"}</p>
            </div>
            <div>
              <strong>EAN / GTIN</strong>
              <p>{product.ean_gtin ?? "—"}</p>
            </div>
            <div>
              <strong>Kategorie</strong>
              <p>{product.category ?? "—"}</p>
            </div>
            <div>
              <strong>Fingerprint</strong>
              <p>{product.fingerprint ?? "—"}</p>
            </div>
          </div>
          <p className="muted">{product.description_short ?? "Keine Kurzbeschreibung vorhanden."}</p>
          {product.image_url ? (
            <ProductImagePreview
              imageUrl={product.image_url}
              title={product.canonical_title}
              caption="Gespeichertes Produktbild."
            />
          ) : null}
          <label>
            Attribute JSON
            <textarea value={toJsonText(product.attributes_json)} readOnly rows={10} />
          </label>
          <div className="link-cluster">
            {product.datasheet_url ? (
              <a className="button button-ghost" href={product.datasheet_url} target="_blank" rel="noreferrer">
                Datenblatt
              </a>
            ) : null}
            {product.image_url ? (
              <a className="button button-ghost" href={product.image_url} target="_blank" rel="noreferrer">
                Bild
              </a>
            ) : null}
            <button className="button" type="button" onClick={() => void searchOffers()}>
              Mock-Angebote suchen
            </button>
            {!product.is_archived ? (
              <button className="button button-danger" type="button" onClick={() => void archiveProduct()}>
                Archivieren
              </button>
            ) : null}
          </div>
        </article>
        <article className="panel">
          <p className="eyebrow">Angebotslage</p>
          <h2>{offers.length} gespeicherte Offers</h2>
          <ul className="shop-items">
            {offers.map((offer) => (
              <li key={offer.id}>
                <div>
                  <strong>{offer.offer_title}</strong>
                  <p className="muted">
                    {formatCurrency(offer.price)} · Shop #{offer.shop_id} · {offer.availability}
                  </p>
                </div>
                <a href={offer.source_url} target="_blank" rel="noreferrer">
                  Öffnen
                </a>
              </li>
            ))}
          </ul>
        </article>
      </section>

      <DataTable
        title="Produktquellen"
        rows={sources}
        getRowKey={(source) => source.id}
        searchableText={(source) =>
          [source.source_type, source.source_value, source.raw_title].filter(Boolean).join(" ")
        }
        columns={[
          { key: "type", label: "Typ", render: (source) => source.source_type },
          { key: "value", label: "Quelle", render: (source) => source.source_value },
          { key: "confidence", label: "Confidence", render: (source) => source.confidence.toFixed(2) },
          {
            key: "actions",
            label: "Aktionen",
            render: (source) => (
              <Link className="button button-ghost" href={`/product-sources?source_id=${source.id}`}>
                Quelle #{source.id} öffnen
              </Link>
            ),
          },
        ]}
      />
    </div>
  );
}
