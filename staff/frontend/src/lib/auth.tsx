import { createContext, useContext, useEffect, useMemo, useState } from "react";

import { login as apiLogin, logout as apiLogout, me, type User } from "./api";

type AuthContextState = {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
};

const AuthContext = createContext<AuthContextState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    me()
      .then((current) => setUser(current))
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  const value = useMemo<AuthContextState>(
    () => ({
      user,
      loading,
      login: async (email: string, password: string) => {
        await apiLogin(email, password);
        const current = await me();
        setUser(current);
      },
      logout: async () => {
        await apiLogout();
        setUser(null);
      },
      refreshUser: async () => {
        const current = await me();
        setUser(current);
      },
    }),
    [user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
