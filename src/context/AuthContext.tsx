import React, { createContext, useContext, useEffect, useState } from "react";
import { authService } from "@/api/authService";
import { setCartUserId } from "@/stores/cart";

interface User {
  id: string;
  email: string;
  name: string;
  is_staff: boolean;
  is_superuser: boolean;
  email_verified: boolean;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (data: { user: User; access: string; refresh: string }) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      try {
        const data = await authService.checkAuth();
        if (data.authenticated) {
          setUser(data.user);
          setCartUserId(data.user.id);
        }
      } catch (error) {
        // Not authenticated
      } finally {
        setLoading(false);
      }
    };
    initAuth();
  }, []);

  const login = (data: { user: User; access: string; refresh: string }) => {
    setUser(data.user);
    setCartUserId(data.user.id);
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch (e) {
      console.error(e);
    }
    setUser(null);
    setCartUserId(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
