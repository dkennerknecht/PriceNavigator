"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { startTransition, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { apiClient } from "@/lib/api";
import { ProductImagePreview } from "@/components/product-image-preview";
import { toJsonText } from "@/lib/format";
import type { Product, ProductPayload, ResolveResponse } from "@/lib/types";

const productSchema = z.object({
  canonical_title: z.string().min(3, "Titel ist erforderlich."),
  manufacturer: z.string().optional(),
  brand: z.string().optional(),
  mpn: z.string().optional(),
  ean_gtin: z.string().optional(),
  category: z.string().optional(),
  description_short: z.string().optional(),
  attributes_json_text: z.string(),
  datasheet_url: z.string().optional(),
  image_url: z.string().optional(),
  notes: z.string().optional(),
});

type FormValues = z.infer<typeof productSchema>;

type ProductCaptureFormProps = {
  product?: Product;
  mode: "create" | "edit";
  onSaved?: (product: Product) => void;
  client?: typeof apiClient;
};

function productToFormValues(product?: Product): FormValues {
  return {
    canonical_title: product?.canonical_title ?? "",
    manufacturer: product?.manufacturer ?? "",
    brand: product?.brand ?? "",
    mpn: product?.mpn ?? "",
    ean_gtin: product?.ean_gtin ?? "",
    category: product?.category ?? "",
    description_short: product?.description_short ?? "",
    attributes_json_text: toJsonText(product?.attributes_json ?? {}),
    datasheet_url: product?.datasheet_url ?? "",
    image_url: product?.image_url ?? "",
    notes: product?.notes ?? "",
  };
}

export function ProductCaptureForm({
  product,
  mode,
  onSaved,
  client = apiClient,
}: ProductCaptureFormProps) {
  const [resolveInput, setResolveInput] = useState({
    url: "",
    manufacturer: product?.manufacturer ?? "",
    mpn: product?.mpn ?? "",
    ean_gtin: product?.ean_gtin ?? "",
  });
  const [resolveResult, setResolveResult] = useState<ResolveResponse | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [isResolving, setIsResolving] = useState(false);

  const form = useForm<FormValues>({
    resolver: zodResolver(productSchema),
    defaultValues: productToFormValues(product),
  });
  const previewImageUrl = form.watch("image_url");
  const previewTitle = form.watch("canonical_title") || "Produkt";

  function preferValue(...values: Array<string | null | undefined>) {
    return values.find((value) => Boolean(value && value.trim().length)) ?? "";
  }

  async function handleResolve() {
    setSubmitError(null);
    setIsResolving(true);
    try {
      const result = await client.resolveProduct(resolveInput);
      setResolveResult(result);
      form.reset({
        canonical_title: preferValue(
          result.candidate.canonical_title,
          form.getValues("canonical_title"),
        ),
        manufacturer: preferValue(
          result.candidate.manufacturer,
          resolveInput.manufacturer,
          form.getValues("manufacturer"),
        ),
        brand: preferValue(
          result.candidate.brand,
          resolveInput.manufacturer,
          form.getValues("brand"),
        ),
        mpn: preferValue(result.candidate.mpn, resolveInput.mpn, form.getValues("mpn")),
        ean_gtin: preferValue(
          result.candidate.ean_gtin,
          resolveInput.ean_gtin,
          form.getValues("ean_gtin"),
        ),
        category: preferValue(result.candidate.category, form.getValues("category")),
        description_short: preferValue(
          result.candidate.description_short,
          form.getValues("description_short"),
        ),
        attributes_json_text: toJsonText(result.candidate.attributes_json),
        datasheet_url: result.candidate.datasheet_url ?? "",
        image_url: result.candidate.image_url ?? "",
        notes: form.getValues("notes"),
      });
    } catch (error) {
      setSubmitError(
        error instanceof Error ? error.message : "Produktdaten konnten nicht aufgelöst werden.",
      );
    } finally {
      setIsResolving(false);
    }
  }

  async function onSubmit(values: FormValues) {
    setSubmitError(null);
    try {
      const attributes_json = values.attributes_json_text
        ? JSON.parse(values.attributes_json_text)
        : {};
      const payload: ProductPayload = {
        canonical_title: values.canonical_title,
        manufacturer: values.manufacturer || null,
        brand: values.brand || null,
        mpn: values.mpn || null,
        ean_gtin: values.ean_gtin || null,
        category: values.category || null,
        description_short: values.description_short || null,
        attributes_json,
        datasheet_url: values.datasheet_url || null,
        image_url: values.image_url || null,
        notes: values.notes || null,
        source_id: resolveResult?.source_id ?? null,
      };

      const saved =
        mode === "create" || !product
          ? await client.createProduct(payload)
          : await client.updateProduct(product.id, {
              ...payload,
              is_archived: product.is_archived,
            });

      startTransition(() => onSaved?.(saved));
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : "Produkt konnte nicht gespeichert werden.");
    }
  }

  return (
    <div className="stack-lg">
      <section className="panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">Resolve</p>
            <h2>Produkt über URL oder Identifier anreichern</h2>
            <p className="muted">
              Für das MVP werden Mock-Resolver verwendet, die später austauschbar bleiben.
            </p>
          </div>
        </div>
        <div className="form-grid">
          <label>
            URL
            <input
              value={resolveInput.url}
              onChange={(event) =>
                setResolveInput((current) => ({ ...current, url: event.target.value }))
              }
              placeholder="https://catalog.mock/..."
            />
          </label>
          <label>
            Hersteller
            <input
              value={resolveInput.manufacturer}
              onChange={(event) =>
                setResolveInput((current) => ({ ...current, manufacturer: event.target.value }))
              }
              placeholder="Milwaukee"
            />
          </label>
          <label>
            MPN
            <input
              value={resolveInput.mpn}
              onChange={(event) =>
                setResolveInput((current) => ({ ...current, mpn: event.target.value }))
              }
              placeholder="M18FDD3-0"
            />
          </label>
          <label>
            EAN / GTIN
            <input
              value={resolveInput.ean_gtin}
              onChange={(event) =>
                setResolveInput((current) => ({ ...current, ean_gtin: event.target.value }))
              }
              placeholder="4058546375941"
            />
          </label>
        </div>
        <button className="button" type="button" onClick={handleResolve} disabled={isResolving}>
          {isResolving ? "Löse auf ..." : "Produktdaten auflösen"}
        </button>
        {resolveResult ? (
          <div className="callout">
            <strong>Resolve-Ergebnis</strong>
            <p>
              Resolver: <code>{resolveResult.resolver_type}</code>, Produkt-Match:{" "}
              <code>{resolveResult.match_strategy}</code>, Confidence:{" "}
              {resolveResult.confidence.toFixed(2)}
            </p>
            {resolveResult.matched_product_id ? (
              <p>Bestehendes Produkt erkannt: #{resolveResult.matched_product_id}</p>
            ) : null}
            {resolveResult.requires_manual_review ? (
              <p>
                Kein Resolver-Treffer. Unten wurden nur die bekannten Eingabewerte
                übernommen, fehlende Stammdaten musst du manuell ergänzen.
              </p>
            ) : null}
            {resolveResult.candidate.image_url ? (
              <ProductImagePreview
                imageUrl={resolveResult.candidate.image_url}
                title={resolveResult.candidate.canonical_title}
                caption="Vom Resolver gelieferte Bildvorschau."
                compact
              />
            ) : null}
          </div>
        ) : null}
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">Produkt</p>
            <h2>{mode === "create" ? "Produkt erfassen" : "Produkt bearbeiten"}</h2>
          </div>
        </div>
        <form className="stack-md" onSubmit={form.handleSubmit(onSubmit)}>
          <div className="form-grid">
            <label>
              Titel
              <input {...form.register("canonical_title")} />
              <small>{form.formState.errors.canonical_title?.message}</small>
            </label>
            <label>
              Hersteller
              <input {...form.register("manufacturer")} />
            </label>
            <label>
              Brand
              <input {...form.register("brand")} />
            </label>
            <label>
              MPN
              <input {...form.register("mpn")} />
            </label>
            <label>
              EAN / GTIN
              <input {...form.register("ean_gtin")} />
            </label>
            <label>
              Kategorie
              <input {...form.register("category")} />
            </label>
          </div>
          <label>
            Kurzbeschreibung
            <textarea rows={3} {...form.register("description_short")} />
          </label>
          <label>
            Attribute JSON
            <textarea rows={8} {...form.register("attributes_json_text")} />
          </label>
          <div className="form-grid">
            <label>
              Datasheet URL
              <input {...form.register("datasheet_url")} />
            </label>
            <label>
              Image URL
              <input {...form.register("image_url")} />
            </label>
          </div>
          {previewImageUrl ? (
            <ProductImagePreview
              imageUrl={previewImageUrl}
              title={previewTitle}
              caption="Aktuelle Produktbild-Vorschau auf Basis der gespeicherten Bild-URL."
            />
          ) : null}
          <label>
            Notizen
            <textarea rows={3} {...form.register("notes")} />
          </label>
          {submitError ? <p className="error-text">{submitError}</p> : null}
          <div className="page-actions">
            <button className="button" type="submit">
              {mode === "create" ? "Produkt speichern" : "Änderungen speichern"}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
