import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ProductCaptureForm } from "@/components/product-capture-form";

describe("ProductCaptureForm", () => {
  it("resolves a product and saves the populated payload", async () => {
    const resolveProduct = vi.fn().mockResolvedValue({
      candidate: {
        canonical_title: "Milwaukee M18 FUEL Drill Driver",
        manufacturer: "Milwaukee",
        brand: "Milwaukee",
        mpn: "M18FDD3-0",
        ean_gtin: "4058546375941",
        category: "Power Tools",
        description_short: "Resolved description",
        attributes_json: { voltage: "18V" },
        datasheet_url: null,
        image_url: "data:image/svg+xml;charset=UTF-8,%3Csvg%20xmlns%3D%22http://www.w3.org/2000/svg%22%20viewBox%3D%220%200%20100%2075%22%3E%3Crect%20width%3D%22100%22%20height%3D%2275%22%20fill%3D%22%23183d35%22/%3E%3C/svg%3E",
        search_tokens: null,
        fingerprint: null,
      },
      source_id: 12,
      resolver_type: "url",
      match_strategy: "manual_review",
      confidence: 0.95,
      matched_product_id: null,
      requires_manual_review: false,
    });
    const createProduct = vi.fn().mockResolvedValue({
      id: 99,
      canonical_title: "Milwaukee M18 FUEL Drill Driver",
      manufacturer: "Milwaukee",
      brand: "Milwaukee",
      mpn: "M18FDD3-0",
      ean_gtin: "4058546375941",
      category: "Power Tools",
      description_short: "Resolved description",
      attributes_json: { voltage: "18V" },
      datasheet_url: null,
      image_url: "data:image/svg+xml;charset=UTF-8,%3Csvg%20xmlns%3D%22http://www.w3.org/2000/svg%22%20viewBox%3D%220%200%20100%2075%22%3E%3Crect%20width%3D%22100%22%20height%3D%2275%22%20fill%3D%22%23183d35%22/%3E%3C/svg%3E",
      search_tokens: null,
      fingerprint: "ean:4058546375941",
      notes: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      is_archived: false,
    });
    const onSaved = vi.fn();

    const client = {
      resolveProduct,
      createProduct,
      updateProduct: vi.fn(),
    };

    render(
      <ProductCaptureForm
        mode="create"
        onSaved={onSaved}
        client={client as never}
      />,
    );

    await userEvent.type(
      screen.getByPlaceholderText("https://catalog.mock/..."),
      "https://catalog.mock/toolhub/milwaukee-m18fdd3-0",
    );
    await userEvent.click(screen.getByRole("button", { name: "Produktdaten auflösen" }));

    expect(await screen.findByDisplayValue("Milwaukee M18 FUEL Drill Driver")).toBeInTheDocument();
    expect(
      screen.getAllByRole("img", { name: "Produktbild: Milwaukee M18 FUEL Drill Driver" }),
    ).toHaveLength(2);

    await userEvent.click(screen.getByRole("button", { name: "Produkt speichern" }));

    await waitFor(() => {
      expect(createProduct).toHaveBeenCalledWith(
        expect.objectContaining({
          canonical_title: "Milwaukee M18 FUEL Drill Driver",
          manufacturer: "Milwaukee",
          source_id: 12,
        }),
      );
    });
    expect(onSaved).toHaveBeenCalled();
  });
});
