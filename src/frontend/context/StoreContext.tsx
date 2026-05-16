import React, { createContext, useContext } from 'react';
import { type Company } from '@/lib/types';

interface StoreContextType {
  companySlug?: string;
  company?: Company | null;
}

const StoreContext = createContext<StoreContextType>({ companySlug: undefined, company: null });

export const useStore = () => useContext(StoreContext);

export const StoreProvider: React.FC<{ companySlug?: string, company?: Company | null, children: React.ReactNode }> = ({ companySlug, company, children }) => {
  return (
    <StoreContext.Provider value={{ companySlug, company }}>
      {children}
    </StoreContext.Provider>
  );
};
