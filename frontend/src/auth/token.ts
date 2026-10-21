const TOKEN_KEY = "autello_admin_token";
export const AUTH_CLEARED_EVENT = "autello-auth-cleared";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
  window.dispatchEvent(new Event(AUTH_CLEARED_EVENT));
}
