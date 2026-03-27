"use client";

import { useEffect } from "react";

import { toJsonText } from "@/lib/format";
import type { Offer, Product, Shop } from "@/lib/types";

type OfferEditorModalProps = {
  offer: Offer | null;
  products: Product[];
  shops: Shop[];
  onClose: () => void;
  onSave: (formData: FormData) => void | Promise<void>;
};

export function OfferEditorModal({
  offer,
  products,
  shops,
  onClose,
  onSave,
}: OfferEditorModalProps) {
  useEffect(() => {
    if (!offer) {
      return;
    }

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [offer, onClose]);

  if (!offer) {
    return null;
  }

  return (
    <div
      className="modal-backdrop"
      onClick={onClose}
      role="presentation"
    >
      <section
        aria-labelledby="offer-editor-title"
        aria-modal="true"
        className="modal-card panel"
        role="dialog"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="modal-header">
          <div>
            <p className="eyebrow">Editor</p>
            <h2 id="offer-editor-title">Offer pflegen</h2>
            <p className="muted">{offer.offer_title}</p>
          </div>
          <button className="button button-ghost" type="button" onClick={onClose}>
            Schließen
          </button>
        </div>

        <form
          className="stack-md"
          onSubmit={(event) => {
            event.preventDefault();
            void onSave(new FormData(event.currentTarget));
          }}
        >
          <label>
            Produkt
            <select name="product_id" defaultValue={offer.product_id}>
              {products.map((product) => (
                <option key={product.id} value={product.id}>
                  {product.canonical_title}
                </option>
              ))}
            </select>
          </label>
          <label>
            Shop
            <select name="shop_id" defaultValue={offer.shop_id}>
              {shops.map((shop) => (
                <option key={shop.id} value={shop.id}>
                  {shop.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Titel
            <input name="offer_title" defaultValue={offer.offer_title} required />
          </label>
          <label>
            Quelle
            <input name="source_url" defaultValue={offer.source_url} required />
          </label>
          <div className="form-grid">
            <label>
              Preis
              <input name="price" type="number" step="0.01" defaultValue={offer.price} />
            </label>
            <label>
              Versand
              <input
                name="shipping_cost"
                type="number"
                step="0.01"
                defaultValue={offer.shipping_cost ?? 0}
              />
            </label>
            <label>
              Lead Time
              <input
                name="lead_time_days"
                type="number"
                step="1"
                defaultValue={offer.lead_time_days ?? 0}
              />
            </label>
            <label>
              Confidence
              <input
                name="matched_confidence"
                type="number"
                step="0.01"
                defaultValue={offer.matched_confidence}
              />
            </label>
          </div>
          <div className="form-grid">
            <label>
              Hersteller
              <input name="manufacturer" defaultValue={offer.manufacturer ?? ""} />
            </label>
            <label>
              Brand
              <input name="brand" defaultValue={offer.brand ?? ""} />
            </label>
            <label>
              MPN
              <input name="mpn" defaultValue={offer.mpn ?? ""} />
            </label>
            <label>
              EAN
              <input name="ean_gtin" defaultValue={offer.ean_gtin ?? ""} />
            </label>
          </div>
          <div className="form-grid">
            <label>
              Pack Qty
              <input name="pack_qty" type="number" step="0.01" defaultValue={offer.pack_qty} />
            </label>
            <label>
              Pack Unit
              <input name="pack_unit" defaultValue={offer.pack_unit} />
            </label>
            <label>
              Currency
              <input name="currency" defaultValue={offer.currency} />
            </label>
            <label>
              Availability
              <input name="availability" defaultValue={offer.availability} />
            </label>
          </div>
          <label>
            Attribute JSON
            <textarea
              name="attributes_json"
              rows={6}
              defaultValue={toJsonText(offer.attributes_json)}
            />
          </label>
          <label className="inline-actions">
            <input type="checkbox" name="is_active" defaultChecked={offer.is_active} />
            Aktiv
          </label>
          <div className="modal-actions">
            <button className="button button-ghost" type="button" onClick={onClose}>
              Abbrechen
            </button>
            <button className="button" type="submit">
              Offer speichern
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
