"use client";

/* eslint-disable @next/next/no-img-element */

import { useState } from "react";

type ProductThumbnailProps = {
  imageUrl: string | null;
  title: string;
};

export function ProductThumbnail({ imageUrl, title }: ProductThumbnailProps) {
  const [hasError, setHasError] = useState(false);

  if (!imageUrl || hasError) {
    return <div aria-hidden="true" className="product-thumbnail product-thumbnail-fallback" />;
  }

  return (
    <img
      alt={`Produktbild: ${title}`}
      className="product-thumbnail"
      loading="lazy"
      src={imageUrl}
      onError={() => setHasError(true)}
    />
  );
}
