"use client";

import { Suspense, startTransition, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

import { DataTable } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import { apiClient } from "@/lib/api";
import { formatDate, toJsonText } from "@/lib/format";
import type { Product, ProductSource } from "@/lib/types";

function ProductSourcesContent() {
  const searchParams = useSearchParams();
  const sourceIdFilter = Number(searchParams.get("source_id") ?? "") || undefined;
  const productIdFilter = Number(searchParams.get("product_id") ?? "") || undefined;
  const [sources, setSources] = useState<ProductSource[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedSource, setSelectedSource] = useState<ProductSource | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadPage() {
    try {
      const [sourceResult, productResult] = await Promise.all([
        apiClient.listProductSources({
          source_id: sourceIdFilter,
          product_id: productIdFilter,
        }),
        apiClient.listProducts({ include_archived: true }),
      ]);
      setSources(sourceResult);
      setProducts(productResult);
      setSelectedSource((current) =>
        current
          ? sourceResult.find((source) => source.id === current.id) ?? sourceResult[0] ?? null
          : sourceResult[0] ?? null,
      );
      setError(null);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Quellen konnten nicht geladen werden.");
    }
  }

  useEffect(() => {
    let active = true;

    Promise.all([
      apiClient.listProductSources({
        source_id: sourceIdFilter,
        product_id: productIdFilter,
      }),
      apiClient.listProducts({ include_archived: true }),
    ])
      .then(([sourceResult, productResult]) => {
        if (!active) {
          return;
        }
        startTransition(() => {
          setSources(sourceResult);
          setProducts(productResult);
          setSelectedSource(sourceResult[0] ?? null);
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
              : "Quellen konnten nicht geladen werden.",
          );
        });
      });

    return () => {
      active = false;
    };
  }, [productIdFilter, sourceIdFilter]);

  async function saveSource(formData: FormData) {
    if (!selectedSource) {
      return;
    }
    const payload = {
      product_id: Number(formData.get("product_id")) || null,
      source_type: String(formData.get("source_type") ?? ""),
      source_value: String(formData.get("source_value") ?? ""),
      raw_title: String(formData.get("raw_title") ?? "") || null,
      raw_payload_json: JSON.parse(String(formData.get("raw_payload_json") ?? "{}")),
      resolved_url: String(formData.get("resolved_url") ?? "") || null,
      confidence: Number(formData.get("confidence") ?? 0),
    };
    await apiClient.updateProductSource(selectedSource.id, payload);
    startTransition(() => void loadPage());
  }

  async function deleteSource(id: number) {
    if (!window.confirm("Quelle löschen?")) {
      return;
    }
    await apiClient.deleteProductSource(id);
    startTransition(() => void loadPage());
  }

  return (
    <div className="page">
      <PageHeader
        title="Produktquellen"
        description={
          sourceIdFilter
            ? `Gefiltert auf Quelle #${sourceIdFilter}.`
            : productIdFilter
              ? `Gefiltert auf Produkt #${productIdFilter}.`
              : "Hier bleiben Resolve-Ergebnisse, Rohdaten und manuelle Zuordnung sichtbar."
        }
        actions={
          sourceIdFilter || productIdFilter
            ? [{ href: "/product-sources", label: "Alle Quellen", variant: "ghost" }]
            : []
        }
      />
      {error ? <p className="error-text">{error}</p> : null}
      <div className="split-grid">
        <DataTable
          title="Quellenliste"
          rows={sources}
          getRowKey={(source) => source.id}
          searchableText={(source) =>
            [source.source_type, source.source_value, source.raw_title].filter(Boolean).join(" ")
          }
          columns={[
            { key: "type", label: "Typ", render: (source) => source.source_type },
            { key: "value", label: "Quelle", render: (source) => source.source_value },
            { key: "created", label: "Erfasst", render: (source) => formatDate(source.created_at) },
            {
              key: "actions",
              label: "Aktionen",
              render: (source) => (
                <div className="inline-actions">
                  <button className="button button-ghost" type="button" onClick={() => setSelectedSource(source)}>
                    Bearbeiten
                  </button>
                  <button className="button button-danger" type="button" onClick={() => void deleteSource(source.id)}>
                    Löschen
                  </button>
                </div>
              ),
            },
          ]}
        />

        <section className="panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Editor</p>
              <h2>Quelle bearbeiten</h2>
            </div>
          </div>
          {selectedSource ? (
            <form
              className="stack-md"
              onSubmit={(event) => {
                event.preventDefault();
                void saveSource(new FormData(event.currentTarget));
              }}
            >
              <label>
                Produkt
                <select name="product_id" defaultValue={selectedSource.product_id ?? ""}>
                  <option value="">Nicht zugeordnet</option>
                  {products.map((product) => (
                    <option key={product.id} value={product.id}>
                      {product.canonical_title}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Source Type
                <input name="source_type" defaultValue={selectedSource.source_type} required />
              </label>
              <label>
                Source Value
                <input name="source_value" defaultValue={selectedSource.source_value} required />
              </label>
              <label>
                Raw Title
                <input name="raw_title" defaultValue={selectedSource.raw_title ?? ""} />
              </label>
              <label>
                Resolved URL
                <input name="resolved_url" defaultValue={selectedSource.resolved_url ?? ""} />
              </label>
              <label>
                Confidence
                <input name="confidence" type="number" step="0.01" defaultValue={selectedSource.confidence} />
              </label>
              <label>
                Payload JSON
                <textarea
                  name="raw_payload_json"
                  rows={8}
                  defaultValue={toJsonText(selectedSource.raw_payload_json)}
                />
              </label>
              <button className="button" type="submit">
                Speichern
              </button>
            </form>
          ) : (
            <p className="muted">Quelle in der Tabelle auswählen.</p>
          )}
        </section>
      </div>
    </div>
  );
}

export default function ProductSourcesPage() {
  return (
    <Suspense
      fallback={
        <div className="page">
          <PageHeader
            title="Produktquellen"
            description="Hier bleiben Resolve-Ergebnisse, Rohdaten und manuelle Zuordnung sichtbar."
          />
          <p className="muted">Quellen werden geladen ...</p>
        </div>
      }
    >
      <ProductSourcesContent />
    </Suspense>
  );
}
