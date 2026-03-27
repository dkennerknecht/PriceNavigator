"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { PageHeader } from "@/components/page-header";
import { ProductCaptureForm } from "@/components/product-capture-form";
import { apiClient } from "@/lib/api";
import type { Product } from "@/lib/types";

export default function EditProductPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [product, setProduct] = useState<Product | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiClient
      .getProduct(Number(params.id))
      .then(setProduct)
      .catch((caughtError) =>
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "Produkt konnte nicht geladen werden.",
        ),
      );
  }, [params.id]);

  return (
    <div className="page">
      <PageHeader title="Produkt bearbeiten" description="Manuelle Korrekturen bleiben jederzeit möglich." />
      {error ? <p className="error-text">{error}</p> : null}
      {product ? (
        <ProductCaptureForm
          mode="edit"
          product={product}
          onSaved={(savedProduct) => router.push(`/products/${savedProduct.id}`)}
        />
      ) : (
        <p className="muted">Lade Daten ...</p>
      )}
    </div>
  );
}

