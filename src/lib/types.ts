/**
 * Shared TypeScript types for products, categories, and brands.
 * All data is fetched from the Django REST API — no static arrays here.
 */

export type Product = {
  id: string;
  name: string;
  slug: string;
  category: string;
  categorySlug: string;
  brand: string;
  price: number;
  originalPrice?: number;
  discount?: number;
  image: string;
  specs: string[];
  description: string;
  inStock: boolean;
  stockCount?: number;
  isNew?: boolean;
  isOffer?: boolean;
  isBestSeller?: boolean;
  isPopular?: boolean;
  freeShipping?: boolean;
  isLimitedStock?: boolean;
  rating: number;
  reviews: number;
  detailedSpecs?: Record<string, string>;
  images?: string[];
  // Laptop specific
  laptopSeries?: string;
  displaySize?: string;
  processor?: string;
  ram?: string;
  storage?: string;
  graphicCard?: string;
  generation?: string;
  // Monitor specific
  screenSize?: string;
  refreshRate?: string;
  panelType?: string;
  // Mobile specific
  mobileProcessor?: string;
  mobileRam?: string;
  mobileStorage?: string;
  color?: string;
  colorHex?: string;
  colors?: { name: string; hex: string }[];
  model3D?: string;
  type?: string;
  features?: string[];
  created_at?: string;
};

export type CategorySection = {
  title: string;
  items: { name: string; slug: string }[];
};

export type Category = {
  name: string;
  slug: string;
  icon: string;
  subcategories?: { name: string; slug: string }[];
  brands?: string[];
  sections?: CategorySection[];
};

export type Brand = {
  name: string;
  slug?: string;
  logo?: string;
  description?: string;
  is_active?: boolean;
}

export interface MegaMenuItem {
  title: string;
  href: string;
  columns: {
    type: 'brands' | 'categories' | 'products';
    title?: string;
    items: {
      name: string;
      href: string;
      image?: string;
      price?: number;
      badge?: string;
      type?: string;
      features?: string[];
    }[];
  }[];
  banner?: {
    text: string;
    buttonText: string;
    buttonHref: string;
    backgroundColor?: string;
    discount?: number;
  };
}
