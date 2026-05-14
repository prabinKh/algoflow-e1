import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { productService } from '@/api/productService';


export const useProducts = () => {
  const { data: dbProducts = [], isLoading: loading } = useQuery({
    queryKey: ['products'],
    queryFn: () => productService.getAll(),
    refetchInterval: 30000, // Optional: poll every 30 seconds
  });

  const allProducts = useMemo(() => {
    if (!Array.isArray(dbProducts)) return [];
    return dbProducts.map(p => {
      const categoryName = typeof p.category === 'string' ? p.category : (p.category_name || String(p.category || ''));
      const categorySlug = p.categorySlug || p.category_slug || (typeof p.category === 'string' ? p.category.toLowerCase().replace(/\s+/g, '-') : '');
      
      return {
        ...p,
        category: categoryName,
        categorySlug: categorySlug,
        brand: p.brand || ''
      };
    });
  }, [dbProducts]);

  return { products: allProducts, loading };
};
