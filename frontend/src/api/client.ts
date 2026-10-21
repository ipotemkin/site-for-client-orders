import type {
  AdminSettings,
  BehaviorMetricPayload,
  BehaviorPayload,
  BehaviorStats,
  Lead,
  LeadPayload,
  LeadQueueResponse,
  Service,
  ServiceInput,
  TokenResponse,
} from "../types";
import { clearToken, getToken } from "../auth/token";

const API = "/api";

async function request<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init?.headers as Record<string, string> | undefined),
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${API}${path}`, {
    ...init,
    headers,
  });

  if (res.status === 401) {
    clearToken();
  }

  if (!res.ok) {
    const text = await res.text();
    let message = text || `HTTP ${res.status}`;
    try {
      const parsed = JSON.parse(text) as {
        detail?: string | { msg?: string }[];
      };
      if (typeof parsed.detail === "string") {
        message = parsed.detail;
      }
    } catch {
      // keep raw text
    }
    throw new Error(message);
  }
  if (res.status === 204) {
    return undefined as T;
  }
  return res.json() as Promise<T>;
}

export function getBootstrapStatus(): Promise<{
  registration_open: boolean;
}> {
  return request("/auth/bootstrap-status");
}

export function registerAdmin(
  login: string,
  password: string,
): Promise<TokenResponse> {
  return request<TokenResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify({ login, password }),
  });
}

export function loginAdmin(
  login: string,
  password: string,
): Promise<TokenResponse> {
  return request<TokenResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ login, password }),
  });
}

export function fetchMe(): Promise<{
  id: number;
  login: string;
}> {
  return request("/auth/me");
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

export function fetchLeadQueue(
  limit = 200,
): Promise<LeadQueueResponse> {
  return request<LeadQueueResponse>(
    `/leads/queue?limit=${limit}`,
  );
}

export function createBehavior(
  payload: BehaviorPayload,
): Promise<unknown> {
  return request("/behaviors/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function postBehaviorMetric(
  payload: BehaviorMetricPayload,
): Promise<unknown> {
  return request("/behavior-metrics/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function fetchBehaviorStats(): Promise<BehaviorStats> {
  return request<BehaviorStats>("/behavior-metrics/stats");
}
