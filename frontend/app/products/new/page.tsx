"use client";

import { useRouter } from "next/navigation";

import { PageHeader } from "@/components/page-header";
import { ProductCaptureForm } from "@/components/product-capture-form";

export default function NewProductPage() {
  const router = useRouter();

  return (
    <div className="page">
      <PageHeader
        title="Produkt erfassen"
        description="URL, Hersteller+MPN oder EAN auflösen und anschließend als Produkt speichern."
      />
      <ProductCaptureForm
        mode="create"
        onSaved={(product) => router.push(`/products/${product.id}`)}
      />
    </div>
  );
}

