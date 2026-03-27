import { render, screen } from "@testing-library/react";

import { ProductThumbnail } from "@/components/product-thumbnail";

describe("ProductThumbnail", () => {
  it("renders the product image when available", () => {
    render(
      <ProductThumbnail
        imageUrl="data:image/svg+xml;charset=UTF-8,%3Csvg%20xmlns%3D%22http://www.w3.org/2000/svg%22%20viewBox%3D%220%200%20100%2075%22%3E%3Crect%20width%3D%22100%22%20height%3D%2275%22%20fill%3D%22%23183d35%22/%3E%3C/svg%3E"
        title="Test Product"
      />,
    );

    expect(screen.getByRole("img", { name: "Produktbild: Test Product" })).toBeInTheDocument();
  });

  it("renders a fallback when no image is available", () => {
    const { container } = render(<ProductThumbnail imageUrl={null} title="Fallback Product" />);

    expect(screen.queryByRole("img", { name: "Produktbild: Fallback Product" })).not.toBeInTheDocument();
    expect(container.querySelector(".product-thumbnail-fallback")).not.toBeNull();
  });
});
