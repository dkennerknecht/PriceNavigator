import { render, screen } from "@testing-library/react";

import { OptimizationResultView } from "@/components/optimization-result-view";
import type { OptimizationRun } from "@/lib/types";

const run: OptimizationRun = {
  id: 7,
  shopping_list_id: 2,
  status: "completed",
  shop_penalty: 12,
  total_items_price: 196.1,
  total_shipping: 0,
  total_score: 196.1,
  shop_count: 1,
  created_at: "2026-03-27T10:00:00Z",
  items: [],
  summary_json: {
    shopping_list_name: "Workshop Restock",
    grouped_shops: [
      {
        shop_id: 2,
        shop_name: "ElectroMax",
        shop_domain: "electromax.example",
        subtotal: 196.1,
        shipping_cost: 0,
        items: [
          {
            shopping_list_item_id: 3,
            product_id: 4,
            product_title: "Milwaukee M18 FUEL Drill Driver",
            offer_id: 44,
            offer_title: "Milwaukee Offer",
            offer_url: "https://electromax.example/milwaukee-m18fdd3-0",
            quantity: 1,
            unit_price: 123.5,
            line_total: 123.5,
          },
        ],
      },
    ],
    item_sum: 196.1,
    shipping_sum: 0,
    shop_count: 1,
    total_score: 196.1,
  },
};

describe("OptimizationResultView", () => {
  it("renders grouped shop results and totals", () => {
    render(<OptimizationResultView run={run} />);

    expect(screen.getByText("Gesamtscore")).toBeInTheDocument();
    expect(screen.getByText("Workshop Restock")).toBeInTheDocument();
    expect(screen.getByText("ElectroMax")).toBeInTheDocument();
    expect(screen.getByText("Milwaukee M18 FUEL Drill Driver")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Angebotslink" })).toHaveAttribute(
      "href",
      "https://electromax.example/milwaukee-m18fdd3-0",
    );
  });
});

