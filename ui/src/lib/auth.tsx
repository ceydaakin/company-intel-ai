import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { Auth } from "./api";

interface Ctx {
  user: string | null;
  loading: boolean;
  login: (u: string, p: string) => Promise<void>;
  logout: () => Promise<void>;
}
const AuthContext = createContext<Ctx | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Auth.me()
      .then((d) => setUser(d.username))
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login: async (u, p) => {
          await Auth.login(u, p);
          const me = await Auth.me();
          setUser(me.username);
        },
        logout: async () => {
          await Auth.logout();
          setUser(null);
        },
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth outside provider");
  return ctx;
};
