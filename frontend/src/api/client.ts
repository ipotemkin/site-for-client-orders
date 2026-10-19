import type {
  AdminSettings,
  BehaviorPayload,
  Lead,
  LeadPayload,
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

export async function fetchAdminSettings(): Promise<AdminSettings> {
  try {
    return await request<AdminSettings>("/admin/latest");
  } catch {
    return {
      services: [
        "Стратегия роста",
        "Операционная эффективность",
        "Цифровая трансформация",
        "Выход на новые рынки",
      ],
      budget_min: "300000",
      budget_max: "5000000",
    };
  }
}

export function createLead(payload: LeadPayload): Promise<Lead> {
  return request<Lead>("/leads/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function createBehavior(
  payload: BehaviorPayload,
): Promise<unknown> {
  return request("/behaviors/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
