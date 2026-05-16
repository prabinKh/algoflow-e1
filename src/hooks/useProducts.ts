import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { productService } from '@/api/productService';


import { useStore } from '@/frontend/context/StoreContext';

export const useProducts = () => {
  const { companySlug } = useStore();
  
  const { data: dbProducts = [], isLoading: loading } = useQuery({
    queryKey: ['products', companySlug],
    queryFn: () => productService.getAll({ company: companySlug }),
    refetchInterval: 30000,
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
