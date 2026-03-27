export type Product = {
  id: number;
  canonical_title: string;
  manufacturer: string | null;
  brand: string | null;
  mpn: string | null;
  ean_gtin: string | null;
  category: string | null;
  description_short: string | null;
  attributes_json: Record<string, unknown>;
  datasheet_url: string | null;
  image_url: string | null;
  search_tokens: string | null;
  fingerprint: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  is_archived: boolean;
};

export type ProductSource = {
  id: number;
  product_id: number | null;
  source_type: string;
  source_value: string;
  raw_title: string | null;
  raw_payload_json: Record<string, unknown>;
  resolved_url: string | null;
  confidence: number;
  created_at: string;
};

export type Shop = {
  id: number;
  name: string;
  domain: string;
  shipping_free_threshold: number | null;
  default_shipping_cost: number;
  trusted: boolean;
  penalty_score: number;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type Offer = {
  id: number;
  product_id: number;
  shop_id: number;
  source_url: string;
  offer_title: string;
  manufacturer: string | null;
  brand: string | null;
  mpn: string | null;
  ean_gtin: string | null;
  pack_qty: number;
  pack_unit: string;
  price: number;
  currency: string;
  availability: string;
  shipping_cost: number | null;
  minimum_order_value: number | null;
  lead_time_days: number | null;
  attributes_json: Record<string, unknown>;
  matched_confidence: number;
  last_checked_at: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
};

export type ProductSummary = {
  id: number;
  canonical_title: string;
  manufacturer: string | null;
  mpn: string | null;
};

export type ShoppingListItem = {
  id: number;
  product_id: number;
  required_qty: number;
  unit: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
  product: ProductSummary;
};

export type ShoppingList = {
  id: number;
  name: string;
  description: string | null;
  status: string;
  shop_penalty: number;
  created_at: string;
  updated_at: string;
};

export type ShoppingListDetail = ShoppingList & {
  items: ShoppingListItem[];
};

export type OptimizationRunItem = {
  id: number;
  optimization_run_id: number;
  shopping_list_item_id: number;
  product_id: number;
  offer_id: number;
  shop_id: number;
  quantity: number;
  unit_price: number;
  line_total: number;
  notes: string | null;
};

export type OptimizationRun = {
  id: number;
  shopping_list_id: number;
  status: string;
  shop_penalty: number;
  total_items_price: number;
  total_shipping: number;
  total_score: number;
  shop_count: number;
  summary_json: {
    shopping_list_name?: string;
    grouped_shops: Array<{
      shop_id: number;
      shop_name: string;
      shop_domain: string;
      subtotal: number;
      shipping_cost: number;
      items: Array<{
        shopping_list_item_id: number;
        product_id: number;
        product_title: string;
        offer_id: number;
        offer_title: string;
        offer_url: string;
        quantity: number;
        unit_price: number;
        line_total: number;
      }>;
    }>;
    item_sum: number;
    shipping_sum: number;
    shop_count: number;
    total_score: number;
  };
  created_at: string;
  items: OptimizationRunItem[];
};

export type ResolveCandidate = {
  canonical_title: string;
  manufacturer: string | null;
  brand: string | null;
  mpn: string | null;
  ean_gtin: string | null;
  category: string | null;
  description_short: string | null;
  attributes_json: Record<string, unknown>;
  datasheet_url: string | null;
  image_url: string | null;
  search_tokens: string | null;
  fingerprint: string | null;
};

export type ResolveResponse = {
  candidate: ResolveCandidate;
  source_id: number;
  resolver_type: string;
  match_strategy: string;
  confidence: number;
  matched_product_id: number | null;
  requires_manual_review: boolean;
};

export type ProductPayload = {
  canonical_title: string;
  manufacturer?: string | null;
  brand?: string | null;
  mpn?: string | null;
  ean_gtin?: string | null;
  category?: string | null;
  description_short?: string | null;
  attributes_json: Record<string, unknown>;
  datasheet_url?: string | null;
  image_url?: string | null;
  notes?: string | null;
  source_id?: number | null;
  is_archived?: boolean;
};
