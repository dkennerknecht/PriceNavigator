"use client";

import Link from "next/link";
import { startTransition, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import { DataTable } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import { apiClient, exportUrl } from "@/lib/api";
import { formatCurrency } from "@/lib/format";
import type { OptimizationRun, Product, ShoppingListDetail } from "@/lib/types";

const emptyItem = {
  product_id: "",
  required_qty: 1,
  unit: "pcs",
  notes: "",
};

export default function ShoppingListDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const shoppingListId = Number(params.id);
  const [shoppingList, setShoppingList] = useState<ShoppingListDetail | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [runs, setRuns] = useState<OptimizationRun[]>([]);
  const [selectedItemId, setSelectedItemId] = useState<number | null>(null);
  const [itemDraft, setItemDraft] = useState(emptyItem);
  const [error, setError] = useState<string | null>(null);

  async function loadPage() {
    try {
      const [shoppingListResult, productResult, runResult] = await Promise.all([
        apiClient.getShoppingList(shoppingListId),
        apiClient.listProducts({ include_archived: false }),
        apiClient.listOptimizationRuns(shoppingListId),
      ]);
      setShoppingList(shoppingListResult);
      setProducts(productResult);
      setRuns(runResult);
      setError(null);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Einkaufsliste konnte nicht geladen werden.",
      );
    }
  }

  useEffect(() => {
    let active = true;

    Promise.all([
      apiClient.getShoppingList(shoppingListId),
      apiClient.listProducts({ include_archived: false }),
      apiClient.listOptimizationRuns(shoppingListId),
    ])
      .then(([shoppingListResult, productResult, runResult]) => {
        if (!active) {
          return;
        }
        startTransition(() => {
          setShoppingList(shoppingListResult);
          setProducts(productResult);
          setRuns(runResult);
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
              : "Einkaufsliste konnte nicht geladen werden.",
          );
        });
      });

    return () => {
      active = false;
    };
  }, [shoppingListId]);

  async function saveItem(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = {
      product_id: Number(itemDraft.product_id),
      required_qty: Number(itemDraft.required_qty),
      unit: itemDraft.unit,
      notes: itemDraft.notes || null,
    };
    if (selectedItemId) {
      await apiClient.updateShoppingListItem(selectedItemId, payload);
    } else {
      await apiClient.addShoppingListItem(shoppingListId, payload);
    }
    setSelectedItemId(null);
    setItemDraft(emptyItem);
    startTransition(() => void loadPage());
  }

  async function deleteItem(itemId: number) {
    if (!window.confirm("Position löschen?")) {
      return;
    }
    await apiClient.deleteShoppingListItem(itemId);
    startTransition(() => void loadPage());
  }

  async function runOptimization() {
    const run = await apiClient.optimizeShoppingList(shoppingListId);
    router.push(`/optimization-runs/${run.id}`);
  }

  if (!shoppingList) {
    return (
      <div className="page">
        <PageHeader title="Einkaufsliste" description="Lade Daten ..." />
        {error ? <p className="error-text">{error}</p> : <p className="muted">Wird geladen ...</p>}
      </div>
    );
  }

  return (
    <div className="page">
      <PageHeader
        title={shoppingList.name}
        description={shoppingList.description ?? "Einkaufsliste ohne Beschreibung."}
        actions={[
          { href: exportUrl(`/export/shopping-list/${shoppingList.id}.csv`), label: "CSV Export", variant: "ghost" },
        ]}
      />
      {error ? <p className="error-text">{error}</p> : null}
      <section className="metric-grid">
        <article className="metric-card">
          <span>Status</span>
          <strong>{shoppingList.status}</strong>
        </article>
        <article className="metric-card">
          <span>Shop Penalty</span>
          <strong>{formatCurrency(shoppingList.shop_penalty)}</strong>
        </article>
        <article className="metric-card">
          <span>Items</span>
          <strong>{shoppingList.items.length}</strong>
        </article>
        <article className="metric-card">
          <span>Läufe</span>
          <strong>{runs.length}</strong>
        </article>
      </section>

      <div className="split-grid">
        <DataTable
          title="Listenpositionen"
          rows={shoppingList.items}
          getRowKey={(item) => item.id}
          searchableText={(item) =>
            [item.product.canonical_title, item.product.manufacturer, item.notes].filter(Boolean).join(" ")
          }
          columns={[
            {
              key: "product",
              label: "Produkt",
              render: (item) => (
                <div>
                  <strong>{item.product.canonical_title}</strong>
                  <p className="muted">{item.product.manufacturer ?? "—"}</p>
                </div>
              ),
            },
            {
              key: "qty",
              label: "Menge",
              render: (item) => `${item.required_qty} ${item.unit}`,
            },
            { key: "notes", label: "Notizen", render: (item) => item.notes ?? "—" },
            {
              key: "actions",
              label: "Aktionen",
              render: (item) => (
                <div className="inline-actions">
                  <button
                    className="button button-ghost"
                    type="button"
                    onClick={() => {
                      setSelectedItemId(item.id);
                      setItemDraft({
                        product_id: String(item.product_id),
                        required_qty: item.required_qty,
                        unit: item.unit,
                        notes: item.notes ?? "",
                      });
                    }}
                  >
                    Bearbeiten
                  </button>
                  <button className="button button-danger" type="button" onClick={() => void deleteItem(item.id)}>
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
              <p className="eyebrow">Position</p>
              <h2>{selectedItemId ? "Item bearbeiten" : "Item hinzufügen"}</h2>
            </div>
          </div>
          <form className="stack-md" onSubmit={(event) => void saveItem(event)}>
            <label>
              Produkt
              <select
                value={itemDraft.product_id}
                onChange={(event) => setItemDraft({ ...itemDraft, product_id: event.target.value })}
                required
              >
                <option value="">Produkt wählen</option>
                {products.map((product) => (
                  <option key={product.id} value={product.id}>
                    {product.canonical_title}
                  </option>
                ))}
              </select>
            </label>
            <div className="form-grid">
              <label>
                Menge
                <input
                  type="number"
                  step="0.01"
                  value={itemDraft.required_qty}
                  onChange={(event) =>
                    setItemDraft({ ...itemDraft, required_qty: Number(event.target.value) })
                  }
                  required
                />
              </label>
              <label>
                Einheit
                <input
                  value={itemDraft.unit}
                  onChange={(event) => setItemDraft({ ...itemDraft, unit: event.target.value })}
                  required
                />
              </label>
            </div>
            <label>
              Notizen
              <textarea
                value={itemDraft.notes}
                onChange={(event) => setItemDraft({ ...itemDraft, notes: event.target.value })}
              />
            </label>
            <div className="page-actions">
              <button className="button" type="submit">
                {selectedItemId ? "Item speichern" : "Item hinzufügen"}
              </button>
              <button className="button button-ghost" type="button" onClick={() => void runOptimization()}>
                Optimierung starten
              </button>
            </div>
          </form>
        </section>
      </div>

      <section className="panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">Runs</p>
            <h2>Vergangene Optimierungen</h2>
          </div>
        </div>
        <div className="link-cluster">
          {runs.map((run) => (
            <Link className="button button-ghost" href={`/optimization-runs/${run.id}`} key={run.id}>
              Run #{run.id} · Score {formatCurrency(run.total_score)}
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
