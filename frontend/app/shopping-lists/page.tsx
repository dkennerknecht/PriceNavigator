"use client";

import Link from "next/link";
import { startTransition, useEffect, useState } from "react";

import { DataTable } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import { apiClient } from "@/lib/api";
import { formatDate } from "@/lib/format";
import type { ShoppingList } from "@/lib/types";

const emptyList = {
  name: "",
  description: "",
  status: "draft",
  shop_penalty: 10,
};

export default function ShoppingListsPage() {
  const [shoppingLists, setShoppingLists] = useState<ShoppingList[]>([]);
  const [selectedList, setSelectedList] = useState<ShoppingList | null>(null);
  const [draft, setDraft] = useState(emptyList);
  const [error, setError] = useState<string | null>(null);

  async function loadLists() {
    try {
      setShoppingLists(await apiClient.listShoppingLists());
      setError(null);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Einkaufslisten konnten nicht geladen werden.",
      );
    }
  }

  useEffect(() => {
    let active = true;

    apiClient
      .listShoppingLists()
      .then((result) => {
        if (!active) {
          return;
        }
        startTransition(() => {
          setShoppingLists(result);
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
              : "Einkaufslisten konnten nicht geladen werden.",
          );
        });
      });

    return () => {
      active = false;
    };
  }, []);

  async function saveList(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = {
      ...draft,
      description: draft.description || null,
    };
    if (selectedList) {
      await apiClient.updateShoppingList(selectedList.id, payload);
    } else {
      await apiClient.createShoppingList(payload);
    }
    setSelectedList(null);
    setDraft(emptyList);
    startTransition(() => void loadLists());
  }

  async function deleteList(id: number) {
    if (!window.confirm("Einkaufsliste löschen?")) {
      return;
    }
    await apiClient.deleteShoppingList(id);
    startTransition(() => void loadLists());
  }

  return (
    <div className="page">
      <PageHeader
        title="Einkaufslisten"
        description="Mengen je Produkt pflegen und danach mit der Shop-Penalty-Strategie optimieren."
      />
      {error ? <p className="error-text">{error}</p> : null}
      <div className="split-grid">
        <DataTable
          title="Listenübersicht"
          rows={shoppingLists}
          getRowKey={(shoppingList) => shoppingList.id}
          searchableText={(shoppingList) =>
            [shoppingList.name, shoppingList.description, shoppingList.status]
              .filter(Boolean)
              .join(" ")
          }
          columns={[
            {
              key: "name",
              label: "Liste",
              render: (shoppingList) => (
                <div>
                  <strong>{shoppingList.name}</strong>
                  <p className="muted">{shoppingList.description ?? "Keine Beschreibung"}</p>
                </div>
              ),
            },
            { key: "status", label: "Status", render: (shoppingList) => shoppingList.status },
            {
              key: "updated",
              label: "Aktualisiert",
              render: (shoppingList) => formatDate(shoppingList.updated_at),
            },
            {
              key: "actions",
              label: "Aktionen",
              render: (shoppingList) => (
                <div className="inline-actions">
                  <Link className="button button-ghost" href={`/shopping-lists/${shoppingList.id}`}>
                    Öffnen
                  </Link>
                  <button
                    className="button button-ghost"
                    type="button"
                    onClick={() => {
                      setSelectedList(shoppingList);
                      setDraft({
                        name: shoppingList.name,
                        description: shoppingList.description ?? "",
                        status: shoppingList.status,
                        shop_penalty: shoppingList.shop_penalty,
                      });
                    }}
                  >
                    Bearbeiten
                  </button>
                  <button
                    className="button button-danger"
                    type="button"
                    onClick={() => void deleteList(shoppingList.id)}
                  >
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
              <h2>{selectedList ? "Liste bearbeiten" : "Liste anlegen"}</h2>
            </div>
          </div>
          <form className="stack-md" onSubmit={(event) => void saveList(event)}>
            <label>
              Name
              <input value={draft.name} onChange={(event) => setDraft({ ...draft, name: event.target.value })} required />
            </label>
            <label>
              Beschreibung
              <textarea value={draft.description} onChange={(event) => setDraft({ ...draft, description: event.target.value })} />
            </label>
            <div className="form-grid">
              <label>
                Status
                <select value={draft.status} onChange={(event) => setDraft({ ...draft, status: event.target.value })}>
                  <option value="draft">draft</option>
                  <option value="active">active</option>
                  <option value="completed">completed</option>
                </select>
              </label>
              <label>
                Shop Penalty
                <input
                  type="number"
                  step="0.01"
                  value={draft.shop_penalty}
                  onChange={(event) => setDraft({ ...draft, shop_penalty: Number(event.target.value) })}
                />
              </label>
            </div>
            <div className="page-actions">
              <button className="button" type="submit">
                {selectedList ? "Liste speichern" : "Liste anlegen"}
              </button>
              {selectedList ? (
                <button
                  className="button button-ghost"
                  type="button"
                  onClick={() => {
                    setSelectedList(null);
                    setDraft(emptyList);
                  }}
                >
                  Abbrechen
                </button>
              ) : null}
            </div>
          </form>
        </section>
      </div>
    </div>
  );
}
