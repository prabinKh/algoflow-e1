import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const axiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add JWT token and Company Slug
axiosInstance.interceptors.request.use(
  (config) => {
    // 1. Add Auth Token
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // 2. Add Company Slug for Public APIs
    // This can be retrieved from a Context or URL path in the UI
    const companySlug = localStorage.getItem('current_company_slug');
    if (companySlug) {
      config.headers['X-Company-Slug'] = companySlug;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token expiration
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized (e.g., redirect to login or refresh token)
      console.error('Unauthorized access - potential token expiration');
      // localStorage.removeItem('access_token');
      // window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;
