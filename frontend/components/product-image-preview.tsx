"use client";

/* eslint-disable @next/next/no-img-element */

import { useState } from "react";

type ProductImagePreviewProps = {
  imageUrl: string;
  title: string;
  caption?: string;
  compact?: boolean;
};

export function ProductImagePreview({
  imageUrl,
  title,
  caption,
  compact = false,
}: ProductImagePreviewProps) {
  const [hasError, setHasError] = useState(false);

  if (!imageUrl || hasError) {
    return null;
  }

  return (
    <figure className={compact ? "product-image-card product-image-card-compact" : "product-image-card"}>
      <img
        className="product-image"
        src={imageUrl}
        alt={`Produktbild: ${title}`}
        loading="lazy"
        onError={() => setHasError(true)}
      />
      {caption ? <figcaption className="muted">{caption}</figcaption> : null}
    </figure>
  );
}
