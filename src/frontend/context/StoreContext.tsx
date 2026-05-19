<<<<<<< HEAD
import React, { createContext, useContext } from 'react';
import { type Company } from '@/lib/types';
=======
import React, { createContext, useContext, useEffect, useState } from 'react';
import { type Company } from '@/lib/types';
import { companyService } from '@/api/companyService';
>>>>>>> dev

interface StoreContextType {
  companySlug?: string;
  company?: Company | null;
<<<<<<< HEAD
}

const StoreContext = createContext<StoreContextType>({ companySlug: undefined, company: null });

export const useStore = () => useContext(StoreContext);

export const StoreProvider: React.FC<{ companySlug?: string, company?: Company | null, children: React.ReactNode }> = ({ companySlug, company, children }) => {
  return (
    <StoreContext.Provider value={{ companySlug, company }}>
=======
  loading: boolean;
}

const StoreContext = createContext<StoreContextType>({ 
  companySlug: undefined, 
  company: null, 
  loading: true 
});

export const useStore = () => useContext(StoreContext);

// Helper to convert hex to HSL for CSS variable injection
function hexToHsl(hex: string): { h: number; s: number; l: number } {
  hex = hex.replace(/^#/, '');
  if (hex.length === 3) {
    hex = hex.split('').map(c => c + c).join('');
  }
  let r = parseInt(hex.substring(0, 2), 16) / 255;
  let g = parseInt(hex.substring(2, 4), 16) / 255;
  let b = parseInt(hex.substring(4, 6), 16) / 255;
  
  let max = Math.max(r, g, b), min = Math.min(r, g, b);
  let h = 0, s = 0, l = (max + min) / 2;
  
  if (max !== min) {
    let d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    switch (max) {
      case r: h = (g - b) / d + (g < b ? 6 : 0); break;
      case g: h = (b - r) / d + 2; break;
      case b: h = (r - g) / d + 4; break;
    }
    h /= 6;
  }
  
  return {
    h: Math.round(h * 360),
    s: Math.round(s * 100),
    l: Math.round(l * 100)
  };
}

export const StoreProvider: React.FC<{ companySlug?: string, company?: Company | null, children: React.ReactNode }> = ({ 
  companySlug: initialSlug, 
  company: initialCompany, 
  children 
}) => {
  const [company, setCompany] = useState<Company | null>(initialCompany || null);
  const [companySlug, setCompanySlug] = useState<string | undefined>(initialSlug);
  const [loading, setLoading] = useState(!initialCompany);

  useEffect(() => {
    if (initialCompany) {
      setCompany(initialCompany);
      setCompanySlug(initialSlug);
      setLoading(false);
      return;
    }

    async function loadCurrentCompany() {
      try {
        const activeCompany = await companyService.getCurrentCompany();
        if (activeCompany) {
          setCompany(activeCompany);
          setCompanySlug(activeCompany.slug);
        }
      } catch (error) {
        console.error("Failed to load active tenant company:", error);
      } finally {
        setLoading(false);
      }
    }

    loadCurrentCompany();
  }, [initialCompany, initialSlug]);

  useEffect(() => {
    if (company && company.theme_color) {
      try {
        const hsl = hexToHsl(company.theme_color);
        // Set CSS variables dynamically
        document.documentElement.style.setProperty('--primary', `${hsl.h} ${hsl.s}% ${hsl.l}%`);
        document.documentElement.style.setProperty('--ring', `${hsl.h} ${hsl.s}% ${hsl.l}%`);
      } catch (err) {
        console.error("Failed to parse theme color:", err);
      }
    }
  }, [company]);

  return (
    <StoreContext.Provider value={{ companySlug, company, loading }}>
>>>>>>> dev
      {children}
    </StoreContext.Provider>
  );
};
