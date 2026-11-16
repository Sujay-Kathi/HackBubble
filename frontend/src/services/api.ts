const API_BASE = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1';

export async function apiFetch(path: string, options: RequestInit = {}) {
  const token = localStorage.getItem('hb_token');
  const headers: Record<string, string> = { 'Content-Type': 'application/json', ...(options.headers as any) };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const text = await res.text();
  let data: any = {};
  try { data = text ? JSON.parse(text) : {}; } catch { data = { raw: text }; }
  if (!res.ok) throw new Error(data?.detail || data?.error?.message || res.statusText);
  return data;
}

export const api = {
  login: (email: string, password: string) => apiFetch('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  register: (email: string, password: string, display_name: string) => apiFetch('/auth/register', { method: 'POST', body: JSON.stringify({ email, password, display_name }) }),
  hackathons: (params?: Record<string, string>) => {
    const q = params ? '?' + new URLSearchParams(params).toString() : '';
    return apiFetch(`/hackathons${q}`);
  },
  teamsDiscover: (params?: Record<string, string>) => {
    const q = params ? '?' + new URLSearchParams(params).toString() : '';
    return apiFetch(`/teams/discover${q}`);
  },
  notifications: () => apiFetch('/notifications'),
};
