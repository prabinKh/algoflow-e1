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
<<<<<<< HEAD
      const categoryName = typeof p.category === 'string' ? p.category : (p.category_name || String(p.category || ''));
      const categorySlug = p.categorySlug || p.category_slug || (typeof p.category === 'string' ? p.category.toLowerCase().replace(/\s+/g, '-') : '');
=======
      const categoryName = p.category_name || (typeof p.category === 'string' ? p.category : String(p.category || ''));
      const categorySlug = p.categorySlug || p.category_slug || '';
      const brandName = p.brand_name || (typeof p.brand === 'string' ? p.brand : String(p.brand || ''));
>>>>>>> dev
      
      return {
        ...p,
        category: categoryName,
        categorySlug: categorySlug,
<<<<<<< HEAD
        brand: p.brand || ''
=======
        brand: brandName
>>>>>>> dev
      };
    });
  }, [dbProducts]);

  return { products: allProducts, loading };
};
