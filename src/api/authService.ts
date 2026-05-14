import { handleApiError } from "./utils";

export const authService = {
  login: async (email: string, password: string) => {
    try {
      const response = await fetch("/api/account/login/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.message || "Failed to login");
      return data;
    } catch (error) {
      handleApiError(error);
      throw error;
    }
  },

  logout: async () => {
    try {
      const response = await fetch("/api/account/logout/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });
      const data = await response.json();
      if (!response.ok) throw new Error("Failed to logout");
      return data;
    } catch (error) {
      handleApiError(error);
      throw error;
    }
  },

  checkAuth: async () => {
    try {
      const response = await fetch("/api/account/check/", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });
      const data = await response.json();
      if (!response.ok) throw new Error("Not authenticated");
      return data;
    } catch (error) {
      // Don't call handleApiError here since it's normal to be unauthenticated
      throw error;
    }
  },
};
