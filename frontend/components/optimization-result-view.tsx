import { formatCurrency, formatDate } from "@/lib/format";
import type { OptimizationRun } from "@/lib/types";

export function OptimizationResultView({ run }: { run: OptimizationRun }) {
  return (
    <div className="stack-lg">
      <section className="metric-grid">
        <article className="metric-card">
          <span>Gesamtscore</span>
          <strong>{formatCurrency(run.total_score)}</strong>
        </article>
        <article className="metric-card">
          <span>Positionssumme</span>
          <strong>{formatCurrency(run.total_items_price)}</strong>
        </article>
        <article className="metric-card">
          <span>Versand</span>
          <strong>{formatCurrency(run.total_shipping)}</strong>
        </article>
        <article className="metric-card">
          <span>Shops</span>
          <strong>{run.shop_count}</strong>
        </article>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">Optimierung</p>
            <h2>{run.summary_json.shopping_list_name ?? "Einkaufsliste"}</h2>
            <p className="muted">Erstellt am {formatDate(run.created_at)}</p>
          </div>
        </div>
        <div className="shop-groups">
          {run.summary_json.grouped_shops.map((shop) => (
            <article className="shop-card" key={shop.shop_id}>
              <header>
                <div>
                  <h3>{shop.shop_name}</h3>
                  <p className="muted">{shop.shop_domain}</p>
                </div>
                <div className="shop-meta">
                  <span>{formatCurrency(shop.subtotal)}</span>
                  <small>Versand {formatCurrency(shop.shipping_cost)}</small>
                </div>
              </header>
              <ul className="shop-items">
                {shop.items.map((item) => (
                  <li key={item.offer_id}>
                    <div>
                      <strong>{item.product_title}</strong>
                      <p className="muted">
                        {item.quantity} × {formatCurrency(item.unit_price)}
                      </p>
                    </div>
                    <a href={item.offer_url} target="_blank" rel="noreferrer">
                      Angebotslink
                    </a>
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}

