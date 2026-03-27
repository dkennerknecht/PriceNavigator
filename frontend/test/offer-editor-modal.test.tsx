import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { OfferEditorModal } from "@/components/offer-editor-modal";
import type { Offer, Product, Shop } from "@/lib/types";

const offer: Offer = {
  id: 14,
  product_id: 3,
  shop_id: 2,
  source_url: "https://electromax.example/test-offer",
  offer_title: "Milwaukee M18 FUEL Drill Driver",
  manufacturer: "Milwaukee",
  brand: "Milwaukee",
  mpn: "M18FDD3-0",
  ean_gtin: "4058546375941",
  pack_qty: 1,
  pack_unit: "unit",
  price: 123.5,
  currency: "EUR",
  availability: "in_stock",
  shipping_cost: 4.9,
  minimum_order_value: null,
  lead_time_days: 1,
  attributes_json: { provider: "mock_offer" },
  matched_confidence: 0.92,
  last_checked_at: new Date().toISOString(),
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  is_active: true,
};

const products: Product[] = [
  {
    id: 3,
    canonical_title: "Milwaukee M18 FUEL Drill Driver",
    manufacturer: "Milwaukee",
    brand: "Milwaukee",
    mpn: "M18FDD3-0",
    ean_gtin: "4058546375941",
    category: "Power Tools",
    description_short: null,
    attributes_json: {},
    datasheet_url: null,
    image_url: null,
    search_tokens: null,
    fingerprint: null,
    notes: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    is_archived: false,
  },
];

const shops: Shop[] = [
  {
    id: 2,
    name: "ElectroMax",
    domain: "electromax.example",
    shipping_free_threshold: 120,
    default_shipping_cost: 4.9,
    trusted: true,
    penalty_score: 0.7,
    notes: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

describe("OfferEditorModal", () => {
  it("renders as dialog and can be closed", async () => {
    const onClose = vi.fn();
    const onSave = vi.fn();

    render(
      <OfferEditorModal
        offer={offer}
        products={products}
        shops={shops}
        onClose={onClose}
        onSave={onSave}
      />,
    );

    expect(screen.getByRole("dialog", { name: "Offer pflegen" })).toBeInTheDocument();
    expect(screen.getByLabelText("Titel")).toHaveValue("Milwaukee M18 FUEL Drill Driver");

    await userEvent.click(screen.getByRole("button", { name: "Abbrechen" }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });
});
