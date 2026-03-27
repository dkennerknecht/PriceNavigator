"use client";

import Link from "next/link";
import { startTransition, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { DataTable } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import { ProductThumbnail } from "@/components/product-thumbnail";
import { apiClient, exportUrl } from "@/lib/api";
import { formatDate } from "@/lib/format";
import type { Product } from "@/lib/types";

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  async function loadProducts() {
    try {
      setProducts(await apiClient.listProducts({ include_archived: true }));
      setError(null);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Produkte konnten nicht geladen werden.");
    }
  }

  useEffect(() => {
    let active = true;

    apiClient
      .listProducts({ include_archived: true })
      .then((result) => {
        if (!active) {
          return;
        }
        startTransition(() => {
          setProducts(result);
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
              : "Produkte konnten nicht geladen werden.",
          );
        });
      });

    return () => {
      active = false;
    };
  }, []);

  async function archiveProduct(id: number) {
    if (!window.confirm("Produkt archivieren?")) {
      return;
    }
    await apiClient.deleteProduct(id);
    void loadProducts();
  }

  return (
    <div className="page">
      <PageHeader
        title="Produkte"
        description="Produkterfassung, Nachbearbeitung und Soft-Delete in einer zentralen Liste."
        actions={[
          { href: "/products/new", label: "Neues Produkt" },
          { href: exportUrl("/export/products.csv"), label: "CSV Export", variant: "ghost" },
        ]}
      />
      {error ? <p className="error-text">{error}</p> : null}
      <DataTable
        title="Produktkatalog"
        description="Suche läuft clientseitig auf Titel, Hersteller, MPN und Kategorie."
        rows={products}
        getRowKey={(product) => product.id}
        searchableText={(product) =>
          [
            product.canonical_title,
            product.manufacturer,
            product.mpn,
            product.ean_gtin,
            product.category,
          ]
            .filter(Boolean)
            .join(" ")
        }
        columns={[
          {
            key: "title",
            label: "Produkt",
            render: (product) => (
              <div className="product-row-summary">
                <ProductThumbnail imageUrl={product.image_url} title={product.canonical_title} />
                <div>
                  <strong>{product.canonical_title}</strong>
                  <p className="muted">
                    {product.manufacturer ?? "Kein Hersteller"} · {product.mpn ?? "Keine MPN"}
                  </p>
                </div>
              </div>
            ),
          },
          {
            key: "category",
            label: "Kategorie",
            render: (product) => product.category ?? "—",
          },
          {
            key: "updated",
            label: "Aktualisiert",
            render: (product) => formatDate(product.updated_at),
          },
          {
            key: "status",
            label: "Status",
            render: (product) => (
              <span className="pill">{product.is_archived ? "Archiviert" : "Aktiv"}</span>
            ),
          },
          {
            key: "actions",
            label: "Aktionen",
            render: (product) => (
              <div className="inline-actions">
                <Link className="button button-ghost" href={`/products/${product.id}`}>
                  Details
                </Link>
                <button
                  className="button button-ghost"
                  type="button"
                  onClick={() => router.push(`/products/${product.id}/edit`)}
                >
                  Bearbeiten
                </button>
                {!product.is_archived ? (
                  <button
                    className="button button-danger"
                    type="button"
                    onClick={() => void archiveProduct(product.id)}
                  >
                    Archivieren
                  </button>
                ) : null}
              </div>
            ),
          },
        ]}
      />
    </div>
  );
}
