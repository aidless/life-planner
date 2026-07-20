/**
 * API Client Configuration
 *
 * Axios-based API client with:
 * - Base URL configuration (/api proxy to backend)
 * - Request/response interceptors
 * - JWT token authentication
 * - 401 auto-redirect to login
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import type { ApiResponse } from '@/types/api';

const apiClient: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle 401 + unified error toast
apiClient.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      // 用 history.pushState + popstate 触发 React Router 重定向（避免页面 reload）
      // 避免在 login 页重复跳转
      if (!window.location.pathname.startsWith('/login')) {
        window.history.pushState({}, '', '/login');
        window.dispatchEvent(new PopStateEvent('popstate'));
      }
      return Promise.reject(error);
    }
    // 提取后端 ApiResponse.error 信息（统一响应格式）
    const apiError = error.response?.data?.error || error.response?.data?.detail;
    if (apiError) {
      // 将后端错误信息附加到 error 对象，前端可统一 toast
      (error as any).userMessage = typeof apiError === 'string'
        ? apiError
        : JSON.stringify(apiError);
    }
    return Promise.reject(error);
  }
);

export default apiClient;

// Convenience functions
export async function get<T = unknown>(url: string, params?: Record<string, unknown>): Promise<ApiResponse<T>> {
  const response = await apiClient.get<ApiResponse<T>>(url, { params });
  return response.data;
}

export async function post<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
  const response = await apiClient.post<ApiResponse<T>>(url, data, config);
  return response.data;
}

export async function put<T = unknown>(url: string, data?: unknown): Promise<ApiResponse<T>> {
  const response = await apiClient.put<ApiResponse<T>>(url, data);
  return response.data;
}

export async function del<T = unknown>(url: string): Promise<ApiResponse<T>> {
  const response = await apiClient.delete<ApiResponse<T>>(url);
  return response.data;
}
