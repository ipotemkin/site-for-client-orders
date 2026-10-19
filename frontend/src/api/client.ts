import type {
  AdminSettings,
  BehaviorPayload,
  Lead,
  LeadPayload,
  Service,
  ServiceInput,
} from "../types";

const API = "/api";

async function request<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  if (res.status === 204) {
    return undefined as T;
  }
  return res.json() as Promise<T>;
}

export function fetchServices(
  activeOnly = false,
): Promise<Service[]> {
  const q = activeOnly ? "?active_only=true" : "";
  return request<Service[]>(`/services/${q}`);
}

export function createService(
  payload: ServiceInput,
): Promise<Service> {
  return request<Service>("/services/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateService(
  id: number,
  payload: ServiceInput,
): Promise<Service> {
  return request<Service>(`/services/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function deleteService(id: number): Promise<void> {
  return request<void>(`/services/${id}`, {
    method: "DELETE",
  });
}

export async function fetchAdminSettings(): Promise<AdminSettings> {
  try {
    return await request<AdminSettings>("/admin/latest");
  } catch {
    return {
      services: [],
      budget_min: "200000",
      budget_max: "3000000",
    };
  }
}

export function saveAdminSettings(
  payload: AdminSettings,
): Promise<AdminSettings> {
  if (payload.id) {
    return request<AdminSettings>(`/admin/${payload.id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  }
  return request<AdminSettings>("/admin/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function createLead(payload: LeadPayload): Promise<Lead> {
  return request<Lead>("/leads/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function fetchLeads(limit = 200): Promise<Lead[]> {
  return request<Lead[]>(`/leads/?limit=${limit}`);
}

export function createBehavior(
  payload: BehaviorPayload,
): Promise<unknown> {
  return request("/behaviors/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
