import axios from "axios";
import type { CompanyDetail, CompanyListItem } from "./types";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  withCredentials: true,
});

export const Auth = {
  login: (username: string, password: string) =>
    api.post("/api/auth/login", { username, password }),
  logout: () => api.post("/api/auth/logout"),
  me: () => api.get<{ username: string }>("/api/auth/me").then((r) => r.data),
};

export const Companies = {
  list: (params: { q?: string; market_tag?: string; favorite?: boolean; sort?: string } = {}) =>
    api.get<CompanyListItem[]>("/api/companies", { params }).then((r) => r.data),
  get: (id: string) => api.get<CompanyDetail>(`/api/companies/${id}`).then((r) => r.data),
  create: (payload: { name: string; hq?: string; website?: string; context?: string }) =>
    api.post<CompanyDetail>("/api/companies", payload).then((r) => r.data),
  patch: (
    id: string,
    payload: Partial<{ hq: string; website: string; context: string; favorite: boolean }>,
  ) => api.patch<CompanyDetail>(`/api/companies/${id}`, payload).then((r) => r.data),
  remove: (id: string) => api.delete(`/api/companies/${id}`),
  regenerate: (id: string) =>
    api.post<CompanyDetail>(`/api/companies/${id}/regenerate`).then((r) => r.data),
  exportUrl: (id: string) =>
    `${import.meta.env.VITE_API_BASE_URL}/api/companies/${id}/export.pdf`,
};

export const Notes = {
  add: (companyId: string, body: string) =>
    api.post(`/api/companies/${companyId}/notes`, { body }).then((r) => r.data),
  remove: (companyId: string, noteId: string) =>
    api.delete(`/api/companies/${companyId}/notes/${noteId}`),
};

export const Compare = {
  run: (a_id: string, b_id: string) =>
    api
      .post<{ a: CompanyDetail; b: CompanyDetail }>("/api/compare", { a_id, b_id })
      .then((r) => r.data),
};
