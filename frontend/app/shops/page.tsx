"use client";

import { startTransition, useEffect, useState } from "react";

import { DataTable } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import { apiClient } from "@/lib/api";
import type { Shop } from "@/lib/types";

const emptyShop = {
  name: "",
  domain: "",
  shipping_free_threshold: 0,
  default_shipping_cost: 0,
  trusted: true,
  penalty_score: 0,
  notes: "",
};

export default function ShopsPage() {
  const [shops, setShops] = useState<Shop[]>([]);
  const [selectedShop, setSelectedShop] = useState<Shop | null>(null);
  const [draft, setDraft] = useState(emptyShop);
  const [error, setError] = useState<string | null>(null);

  async function loadShops() {
    try {
      const result = await apiClient.listShops();
      setShops(result);
      setError(null);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Shops konnten nicht geladen werden.");
    }
  }

  useEffect(() => {
    let active = true;

    apiClient
      .listShops()
      .then((result) => {
        if (!active) {
          return;
        }
        startTransition(() => {
          setShops(result);
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
              : "Shops konnten nicht geladen werden.",
          );
        });
      });

    return () => {
      active = false;
    };
  }, []);

  async function submitShop(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = {
      ...draft,
      notes: draft.notes || null,
      shipping_free_threshold: draft.shipping_free_threshold || null,
    };
    if (selectedShop) {
      await apiClient.updateShop(selectedShop.id, payload);
    } else {
      await apiClient.createShop(payload);
    }
    setSelectedShop(null);
    setDraft(emptyShop);
    startTransition(() => void loadShops());
  }

  async function deleteShop(id: number) {
    if (!window.confirm("Shop löschen?")) {
      return;
    }
    await apiClient.deleteShop(id);
    startTransition(() => void loadShops());
  }

  return (
    <div className="page">
      <PageHeader title="Shops" description="Versandlogik, Vertrauensstatus und Penalty-Basis pro Shop." />
      {error ? <p className="error-text">{error}</p> : null}
      <div className="split-grid">
        <DataTable
          title="Shop Tabelle"
          rows={shops}
          getRowKey={(shop) => shop.id}
          searchableText={(shop) => [shop.name, shop.domain, shop.notes].filter(Boolean).join(" ")}
          columns={[
            {
              key: "shop",
              label: "Shop",
              render: (shop) => (
                <div>
                  <strong>{shop.name}</strong>
                  <p className="muted">{shop.domain}</p>
                </div>
              ),
            },
            { key: "shipping", label: "Versand", render: (shop) => `${shop.default_shipping_cost.toFixed(2)} EUR` },
            { key: "penalty", label: "Penalty", render: (shop) => shop.penalty_score.toFixed(2) },
            {
              key: "actions",
              label: "Aktionen",
              render: (shop) => (
                <div className="inline-actions">
                  <button
                    className="button button-ghost"
                    type="button"
                    onClick={() => {
                      setSelectedShop(shop);
                      setDraft({
                        name: shop.name,
                        domain: shop.domain,
                        shipping_free_threshold: shop.shipping_free_threshold ?? 0,
                        default_shipping_cost: shop.default_shipping_cost,
                        trusted: shop.trusted,
                        penalty_score: shop.penalty_score,
                        notes: shop.notes ?? "",
                      });
                    }}
                  >
                    Bearbeiten
                  </button>
                  <button className="button button-danger" type="button" onClick={() => void deleteShop(shop.id)}>
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
              <h2>{selectedShop ? "Shop bearbeiten" : "Shop anlegen"}</h2>
            </div>
          </div>
          <form className="stack-md" onSubmit={(event) => void submitShop(event)}>
            <label>
              Name
              <input value={draft.name} onChange={(event) => setDraft({ ...draft, name: event.target.value })} required />
            </label>
            <label>
              Domain
              <input value={draft.domain} onChange={(event) => setDraft({ ...draft, domain: event.target.value })} required />
            </label>
            <div className="form-grid">
              <label>
                Versandkosten
                <input
                  type="number"
                  step="0.01"
                  value={draft.default_shipping_cost}
                  onChange={(event) =>
                    setDraft({ ...draft, default_shipping_cost: Number(event.target.value) })
                  }
                />
              </label>
              <label>
                Versandfrei ab
                <input
                  type="number"
                  step="0.01"
                  value={draft.shipping_free_threshold}
                  onChange={(event) =>
                    setDraft({ ...draft, shipping_free_threshold: Number(event.target.value) })
                  }
                />
              </label>
              <label>
                Penalty
                <input
                  type="number"
                  step="0.01"
                  value={draft.penalty_score}
                  onChange={(event) => setDraft({ ...draft, penalty_score: Number(event.target.value) })}
                />
              </label>
            </div>
            <label className="inline-actions">
              <input
                type="checkbox"
                checked={draft.trusted}
                onChange={(event) => setDraft({ ...draft, trusted: event.target.checked })}
              />
              Trusted
            </label>
            <label>
              Notizen
              <textarea value={draft.notes} onChange={(event) => setDraft({ ...draft, notes: event.target.value })} />
            </label>
            <div className="page-actions">
              <button className="button" type="submit">
                {selectedShop ? "Shop speichern" : "Shop anlegen"}
              </button>
              {selectedShop ? (
                <button
                  className="button button-ghost"
                  type="button"
                  onClick={() => {
                    setSelectedShop(null);
                    setDraft(emptyShop);
                  }}
                >
                  Zurücksetzen
                </button>
              ) : null}
            </div>
          </form>
        </section>
      </div>
    </div>
  );
}
