import { useState, useMemo } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useOutletContext } from "react-router-dom";

import { Package, Search, Plus, Edit2, Trash2, ExternalLink, Filter } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { Link } from "react-router-dom";
import { type Product } from "@/lib/types";
import { formatPrice } from "@/lib/utils";
import { toast } from "sonner";
import { useProducts } from "@/hooks/useProducts";
import { SafeImage } from "@/frontend/components/SafeImage";

import { productService } from "@/api/productService";

const AdminProducts = () => {
  const { setIsSidebarOpen } = useOutletContext<{ setIsSidebarOpen: (open: boolean) => void }>();
  const { products, loading } = useProducts();
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("All");

  const queryClient = useQueryClient();

  const handleDelete = async (id: string) => {
    if (window.confirm("Are you sure you want to delete this product?")) {
      try {
        await productService.delete(id);
        await queryClient.invalidateQueries({ queryKey: ['products'] });
        toast.success("Product deleted successfully");
      } catch (error) {
        toast.error("Failed to delete product");
      }
    }
  };

  const categories = useMemo(() => ["All", ...new Set(products.map(p => p.category))], [products]);

  const filteredProducts = useMemo(() => products.filter(product => {
    const matchesSearch = (product.name?.toLowerCase() || "").includes(searchTerm.toLowerCase()) ||
                         (product.description?.toLowerCase() || "").includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === "All" || product.category === selectedCategory;
    return matchesSearch && matchesCategory;
  }), [products, searchTerm, selectedCategory]);

  return (
    <div className="flex-1 flex flex-col min-w-0 min-h-full pb-20 lg:pb-0">
      <main className="flex-1 p-4 md:p-8">
        <div className="max-w-7xl mx-auto space-y-8">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div>
              <h1 className="text-3xl font-bold text-foreground">Product Management</h1>
              <p className="text-muted-foreground">Manage your store's product catalog</p>
            </div>
            
            <Link
              to="/admin/products/add"
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors shadow-sm"
            >
              <Plus size={18} />
              <span>Add Product</span>
            </Link>
          </div>

          <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
            <div className="relative w-full md:w-80">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={18} />
              <input 
                type="text"
                placeholder="Search products..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-card border border-border rounded-xl focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
              />
            </div>

            <div className="flex items-center gap-2 w-full md:w-auto overflow-x-auto pb-2 md:pb-0 no-scrollbar">
              <Filter size={18} className="text-muted-foreground flex-shrink-0" />
              {categories.map(category => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`px-4 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-all ${
                    selectedCategory === category
                      ? "bg-blue-600 text-white shadow-sm"
                      : "bg-card text-muted-foreground border border-border hover:border-blue-500"
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>
          </div>

          <div className="bg-card rounded-2xl border border-border overflow-hidden shadow-sm">
            {/* Desktop Table View */}
            <div className="hidden md:block overflow-x-auto">
              <table className="w-full text-left">
                <thead className="bg-muted border-b border-border">
                  <tr>
                    <th className="px-6 py-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Product</th>
                    <th className="px-6 py-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Category</th>
                    <th className="px-6 py-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Price</th>
                    <th className="px-6 py-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Status</th>
                    <th className="px-6 py-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {loading ? (
                    Array(5).fill(0).map((_, i) => (
                      <tr key={i} className="animate-pulse">
                        <td className="px-6 py-4"><div className="h-10 w-40 bg-accent rounded" /></td>
                        <td className="px-6 py-4"><div className="h-6 w-20 bg-accent rounded" /></td>
                        <td className="px-6 py-4"><div className="h-6 w-16 bg-accent rounded" /></td>
                        <td className="px-6 py-4"><div className="h-6 w-16 bg-accent rounded" /></td>
                        <td className="px-6 py-4"><div className="h-6 w-24 bg-accent ml-auto rounded" /></td>
                      </tr>
                    ))
                  ) : filteredProducts.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="px-6 py-12 text-center text-muted-foreground">
                        No products found matching your criteria.
                      </td>
                    </tr>
                  ) : (
                    filteredProducts.map((product) => (
                      <tr key={product.id} className="hover:bg-muted transition-colors">
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <div className="w-12 h-12 rounded-lg overflow-hidden bg-accent flex-shrink-0">
                              <SafeImage src={product.image} alt={product.name} className="w-full h-full object-cover" />
                            </div>
                            <div className="min-w-0">
                              <div className="text-sm font-bold text-foreground truncate">{product.name}</div>
                              <div className="text-xs text-muted-foreground truncate max-w-[200px]">{product.description}</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-accent text-muted-foreground border border-border">
                            {product.category}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm font-bold text-foreground">
                          {formatPrice(product.price)}
                        </td>
                        <td className="px-6 py-4">
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-100">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                            Active
                          </span>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <Link
                              to={product.slug || product.id ? `/product/${product.slug || product.id}` : "#"}
                              target="_blank"
                              className={`p-2 text-muted-foreground hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all ${!(product.slug || product.id) ? "pointer-events-none" : ""}`}
                              title="View on store"
                            >
                              <ExternalLink size={18} />
                            </Link>
                            <Link
                              to={`/admin/products/edit/${product.id}`}
                              className="p-2 text-muted-foreground hover:text-amber-600 hover:bg-amber-50 rounded-lg transition-all"
                              title="Edit product"
                            >
                              <Edit2 size={18} />
                            </Link>
                            <button
                              onClick={() => handleDelete(product.id)}
                              className="p-2 text-muted-foreground hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-all"
                              title="Delete product"
                            >
                              <Trash2 size={18} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {/* Mobile Card View */}
            <div className="md:hidden divide-y divide-gray-200">
              {loading ? (
                Array(3).fill(0).map((_, i) => (
                  <div key={i} className="p-4 animate-pulse space-y-3">
                    <div className="flex gap-3">
                      <div className="w-16 h-16 bg-accent rounded-lg" />
                      <div className="flex-1 space-y-2">
                        <div className="h-4 bg-accent rounded w-3/4" />
                        <div className="h-3 bg-accent rounded w-1/2" />
                      </div>
                    </div>
                    <div className="flex justify-between items-center">
                      <div className="h-4 bg-accent rounded w-20" />
                      <div className="h-8 bg-accent rounded w-24" />
                    </div>
                  </div>
                ))
              ) : filteredProducts.length === 0 ? (
                <div className="p-8 text-center text-muted-foreground">
                  No products found matching your criteria.
                </div>
              ) : (
                filteredProducts.map((product) => (
                  <div key={product.id} className="p-4 space-y-4">
                    <div className="flex gap-4">
                      <div className="w-20 h-20 rounded-xl overflow-hidden bg-accent flex-shrink-0">
                        <SafeImage src={product.image} alt={product.name} className="w-full h-full object-cover" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-start justify-between gap-2">
                          <h3 className="text-sm font-bold text-foreground line-clamp-2">{product.name}</h3>
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-accent text-muted-foreground border border-border whitespace-nowrap">
                            {product.category}
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground mt-1 line-clamp-1">{product.description}</p>
                        <p className="text-sm font-black text-blue-600 mt-2">{formatPrice(product.price)}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between pt-2">
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-emerald-50 text-emerald-700 border border-emerald-100">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                        Active
                      </span>
                      
                      <div className="flex items-center gap-1">
                        <Link
                          to={product.slug || product.id ? `/product/${product.slug || product.id}` : "#"}
                          target="_blank"
                          className={`p-2 text-muted-foreground hover:bg-accent rounded-lg transition-all ${!(product.slug || product.id) ? "pointer-events-none" : ""}`}
                        >
                          <ExternalLink size={18} />
                        </Link>
                        <Link
                          to={`/admin/products/edit/${product.id}`}
                          className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-all"
                        >
                          <Edit2 size={18} />
                        </Link>
                        <button
                          onClick={() => handleDelete(product.id)}
                          className="p-2 text-rose-600 hover:bg-rose-50 rounded-lg transition-all"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default AdminProducts;
