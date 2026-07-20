/** Auth state management with Zustand. */

import { create } from "zustand";
import type { User } from "@/types";
import apiClient from "@/api/client";

interface AuthState {
  user: any;
  token: string | null;
  loading: boolean;
  error: string | null;

  login: (username: string, password: string) => Promise<boolean>;
  register: (username: string, email: string, password: string, display_name?: string) => Promise<boolean>;
  logout: () => void;
  loadFromStorage: () => void;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  loading: false,
  error: null,

  login: async (username: string, password: string) => {
    set({ loading: true, error: null });
    try {
      const res = await apiClient.post<any>("/auth/login", { username, password });
      const { access_token, user } = res.data;
      localStorage.setItem("token", access_token);
      localStorage.setItem("user", JSON.stringify(user));
      set({ user, token: access_token, loading: false });
      return true;
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.response?.data?.error || "登录失败";
      set({ error: msg, loading: false });
      return false;
    }
  },

  register: async (username: string, email: string, password: string, display_name?: string) => {
    set({ loading: true, error: null });
    try {
      const res = await apiClient.post<any>("/auth/register", {
        username,
        email,
        password,
        display_name: display_name || username,
      });
      const { access_token, user } = res.data;
      localStorage.setItem("token", access_token);
      localStorage.setItem("user", JSON.stringify(user));
      set({ user, token: access_token, loading: false });
      return true;
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      let msg = "注册失败";
      if (Array.isArray(detail)) {
        msg = detail.map((d: { msg: string }) => d.msg).join("; ");
      } else if (typeof detail === "string") {
        msg = detail;
      } else {
        msg = err?.response?.data?.error || "注册失败";
      }
      set({ error: msg, loading: false });
      return false;
    }
  },

  logout: () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    set({ user: null, token: null });
  },

  loadFromStorage: () => {
    const token = localStorage.getItem("token");
    const userStr = localStorage.getItem("user");
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr) as User;
        set({ user, token });
      } catch {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
      }
    }
  },

  clearError: () => {
    set({ error: null });
  },
}));