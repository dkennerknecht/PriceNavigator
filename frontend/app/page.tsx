"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { PageHeader } from "@/components/page-header";
import { apiClient, exportUrl } from "@/lib/api";

export default function DashboardPage() {
  const [counts, setCounts] = useState({
    products: 0,
    sources: 0,
    offers: 0,
    shops: 0,
    shoppingLists: 0,
    optimizationRuns: 0,
  });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    Promise.all([
      apiClient.listProducts({ include_archived: true }),
      apiClient.listProductSources(),
      apiClient.listOffers({ include_inactive: true }),
      apiClient.listShops(),
      apiClient.listShoppingLists(),
      apiClient.listOptimizationRuns(),
    ])
      .then(([products, sources, offers, shops, shoppingLists, optimizationRuns]) => {
        if (!active) {
          return;
        }
        setCounts({
          products: products.length,
          sources: sources.length,
          offers: offers.length,
          shops: shops.length,
          shoppingLists: shoppingLists.length,
          optimizationRuns: optimizationRuns.length,
        });
      })
      .catch((caughtError) => {
        if (!active) {
          return;
        }
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "Dashboard konnte nicht geladen werden.",
        );
      });

    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="page">
      <PageHeader
        title="Deterministische Beschaffung"
        description="PriceNavigator verbindet Produkt-Erfassung, Angebotsdaten und eine testbare Shop-Penalty-Optimierung in einem lokal lauffähigen MVP."
        actions={[
          { href: "/products/new", label: "Produkt erfassen" },
          { href: "/shopping-lists", label: "Einkaufsliste öffnen", variant: "ghost" },
        ]}
      />

      <section className="hero-grid">
        <article className="panel panel-alt">
          <p className="eyebrow">MVP Fokus</p>
          <h2>Phase 1 und 2 in einer konsistenten Datenbasis</h2>
          <p className="muted">
            Produkte lassen sich per URL, Hersteller+MPN oder EAN anlegen. Angebote und
            Einkaufslisten bleiben editierbar, Export und Optimierung laufen nachvollziehbar im
            Backend.
          </p>
        </article>
        <article className="panel">
          <p className="eyebrow">Schnellzugriff</p>
          <h2>Exports & Seeds</h2>
          <div className="link-cluster">
            <a className="button button-ghost" href={exportUrl("/export/products.csv")} target="_blank" rel="noreferrer">
              Products CSV
            </a>
            <a className="button button-ghost" href={exportUrl("/export/offers.csv")} target="_blank" rel="noreferrer">
              Offers CSV
            </a>
            <Link className="button button-ghost" href="/products">
              Katalog öffnen
            </Link>
          </div>
        </article>
      </section>

      {error ? <p className="error-text">{error}</p> : null}

      <section className="metric-grid">
        <article className="metric-card">
          <span>Produkte</span>
          <strong>{counts.products}</strong>
        </article>
        <article className="metric-card">
          <span>Produktquellen</span>
          <strong>{counts.sources}</strong>
        </article>
        <article className="metric-card">
          <span>Angebote</span>
          <strong>{counts.offers}</strong>
        </article>
        <article className="metric-card">
          <span>Shops</span>
          <strong>{counts.shops}</strong>
        </article>
        <article className="metric-card">
          <span>Einkaufslisten</span>
          <strong>{counts.shoppingLists}</strong>
        </article>
        <article className="metric-card">
          <span>Optimierungsläufe</span>
          <strong>{counts.optimizationRuns}</strong>
        </article>
      </section>
    </div>
  );
}

