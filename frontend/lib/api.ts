import type {
  Offer,
  OptimizationRun,
  Product,
  ProductPayload,
  ProductSource,
  ResolveResponse,
  ShoppingList,
  ShoppingListDetail,
  Shop,
} from "@/lib/types";

const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

type RequestOptions = RequestInit & {
  searchParams?: Record<string, string | number | boolean | undefined | null>;
};

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const url = new URL(`${apiBaseUrl}${path}`);

  for (const [key, value] of Object.entries(options.searchParams ?? {})) {
    if (value === undefined || value === null || value === "") {
      continue;
    }
    url.searchParams.set(key, String(value));
  }

  const response = await fetch(url.toString(), {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    const message = payload?.detail ?? response.statusText;
    throw new Error(message);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export const apiClient = {
  listProducts: (params: { q?: string; include_archived?: boolean } = {}) =>
    request<Product[]>("/products", { searchParams: params }),
  getProduct: (id: number) => request<Product>(`/products/${id}`),
  resolveProduct: (payload: {
    url?: string;
    manufacturer?: string;
    mpn?: string;
    ean_gtin?: string;
  }) =>
    request<ResolveResponse>("/products/resolve", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  createProduct: (payload: ProductPayload) =>
    request<Product>("/products", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  updateProduct: (id: number, payload: ProductPayload) =>
    request<Product>(`/products/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  deleteProduct: (id: number) =>
    request<{ message: string }>(`/products/${id}`, { method: "DELETE" }),
  listProductSources: (params: { q?: string; product_id?: number; source_id?: number } = {}) =>
    request<ProductSource[]>("/product-sources", { searchParams: params }),
  getProductSource: (id: number) => request<ProductSource>(`/product-sources/${id}`),
  updateProductSource: (id: number, payload: Partial<ProductSource>) =>
    request<ProductSource>(`/product-sources/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  deleteProductSource: (id: number) =>
    request<{ message: string }>(`/product-sources/${id}`, { method: "DELETE" }),
  listShops: (q?: string) => request<Shop[]>("/shops", { searchParams: { q } }),
  createShop: (payload: Partial<Shop>) =>
    request<Shop>("/shops", { method: "POST", body: JSON.stringify(payload) }),
  updateShop: (id: number, payload: Partial<Shop>) =>
    request<Shop>(`/shops/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  deleteShop: (id: number) =>
    request<{ message: string }>(`/shops/${id}`, { method: "DELETE" }),
  listOffers: (params: {
    q?: string;
    product_id?: number;
    shop_id?: number;
    include_inactive?: boolean;
  } = {}) => request<Offer[]>("/offers", { searchParams: params }),
  searchOffers: (productIds: number[]) =>
    request<{ offers: Offer[]; created_count: number; warnings: string[] }>("/offers/search", {
      method: "POST",
      body: JSON.stringify({ product_ids: productIds }),
    }),
  updateOffer: (id: number, payload: Partial<Offer>) =>
    request<Offer>(`/offers/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  deleteOffer: (id: number) =>
    request<{ message: string }>(`/offers/${id}`, { method: "DELETE" }),
  listShoppingLists: (q?: string) =>
    request<ShoppingList[]>("/shopping-lists", { searchParams: { q } }),
  createShoppingList: (payload: Partial<ShoppingList>) =>
    request<ShoppingList>("/shopping-lists", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getShoppingList: (id: number) =>
    request<ShoppingListDetail>(`/shopping-lists/${id}`),
  updateShoppingList: (id: number, payload: Partial<ShoppingList>) =>
    request<ShoppingList>(`/shopping-lists/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  deleteShoppingList: (id: number) =>
    request<{ message: string }>(`/shopping-lists/${id}`, { method: "DELETE" }),
  addShoppingListItem: (
    shoppingListId: number,
    payload: {
      product_id: number;
      required_qty: number;
      unit: string;
      notes?: string | null;
    },
  ) =>
    request(`/shopping-lists/${shoppingListId}/items`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  updateShoppingListItem: (
    itemId: number,
    payload: {
      product_id: number;
      required_qty: number;
      unit: string;
      notes?: string | null;
    },
  ) =>
    request(`/shopping-list-items/${itemId}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  deleteShoppingListItem: (itemId: number) =>
    request<{ message: string }>(`/shopping-list-items/${itemId}`, {
      method: "DELETE",
    }),
  optimizeShoppingList: (shoppingListId: number) =>
    request<OptimizationRun>(`/shopping-lists/${shoppingListId}/optimize`, {
      method: "POST",
    }),
  listOptimizationRuns: (shoppingListId?: number) =>
    request<OptimizationRun[]>("/optimization-runs", {
      searchParams: { shopping_list_id: shoppingListId },
    }),
  getOptimizationRun: (id: number) =>
    request<OptimizationRun>(`/optimization-runs/${id}`),
  deleteOptimizationRun: (id: number) =>
    request<{ message: string }>(`/optimization-runs/${id}`, {
      method: "DELETE",
    }),
};

export function exportUrl(path: string): string {
  return `${apiBaseUrl}${path}`;
}
