import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ComponentProps } from "react";

const mocks = vi.hoisted(() => ({
  apiClient: {
    listOffers: vi.fn(),
    listProducts: vi.fn(),
    listShops: vi.fn(),
    searchOffers: vi.fn(),
  },
}));

vi.mock("next/link", () => ({
  default: ({ href, children, ...props }: ComponentProps<"a">) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

vi.mock("@/lib/api", () => ({
  apiClient: mocks.apiClient,
  exportUrl: (path: string) => `http://localhost:8000/api${path}`,
}));

import OffersPage from "@/app/offers/page";

describe("OffersPage", () => {
  it("selects the first active product and starts the offer search", async () => {
    mocks.apiClient.listOffers.mockResolvedValue([]);
    mocks.apiClient.listProducts.mockResolvedValue([
      {
        id: 1,
        canonical_title: "Archiviertes Produkt",
        manufacturer: "Alt",
        brand: null,
        mpn: null,
        ean_gtin: null,
        category: null,
        description_short: null,
        attributes_json: {},
        datasheet_url: null,
        image_url: null,
        search_tokens: null,
        fingerprint: null,
        notes: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        is_archived: true,
      },
      {
        id: 6,
        canonical_title: "Hager univers Enclosure IP44 1400x550x205 mm",
        manufacturer: "Hager",
        brand: "Hager",
        mpn: "FP92TN2",
        ean_gtin: "3250612668090",
        category: "Enclosures",
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
    ]);
    mocks.apiClient.listShops.mockResolvedValue([]);
    mocks.apiClient.searchOffers.mockResolvedValue({ offers: [], created_count: 2, warnings: [] });

    render(<OffersPage />);

    await waitFor(() => {
      expect(mocks.apiClient.listProducts).toHaveBeenCalledTimes(1);
    });

    const select = await screen.findByRole("combobox");
    expect(select).toHaveValue("6");

    await userEvent.click(screen.getByRole("button", { name: "Angebots-Suche starten" }));

    await waitFor(() => {
      expect(mocks.apiClient.searchOffers).toHaveBeenCalledWith([6]);
    });
    expect(await screen.findByText("2 Angebote neu geladen.")).toBeInTheDocument();
  });
});
