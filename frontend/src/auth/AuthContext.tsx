import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import {
  loginAdmin,
  registerAdmin,
} from "../api/client";
import {
  AUTH_CLEARED_EVENT,
  clearToken,
  getToken,
  setToken,
} from "./token";

type AuthContextValue = {
  token: string | null;
  isAuthenticated: boolean;
  login: (login: string, password: string) => Promise<void>;
  register: (
    login: string,
    password: string,
  ) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(
  null,
);

export function AuthProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [token, setTokenState] = useState<string | null>(
    () => getToken(),
  );

  useEffect(() => {
    const onCleared = () => setTokenState(null);
    window.addEventListener(AUTH_CLEARED_EVENT, onCleared);
    return () => {
      window.removeEventListener(
        AUTH_CLEARED_EVENT,
        onCleared,
      );
    };
  }, []);

  const persist = useCallback((value: string) => {
    setToken(value);
    setTokenState(value);
  }, []);

  const login = useCallback(
    async (loginValue: string, password: string) => {
      const res = await loginAdmin(loginValue, password);
      persist(res.access_token);
    },
    [persist],
  );

  const register = useCallback(
    async (loginValue: string, password: string) => {
      const res = await registerAdmin(loginValue, password);
      persist(res.access_token);
    },
    [persist],
  );

  const logout = useCallback(() => {
    clearToken();
    setTokenState(null);
  }, []);

  const value = useMemo(
    () => ({
      token,
      isAuthenticated: Boolean(token),
      login,
      register,
      logout,
    }),
    [token, login, register, logout],
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
