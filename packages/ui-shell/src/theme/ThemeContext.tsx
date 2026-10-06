import { createContext, ReactNode, useEffect, useMemo, useState } from "react";

export type ThemeMode = "light" | "dark" | "system";

export interface ThemeContextValue {
  mode: ThemeMode;
  setMode: (mode: ThemeMode) => void;
}

const STORAGE_KEY = "ecopredict-theme";

export const ThemeContext = createContext<ThemeContextValue | null>(null);

function leerModoGuardado(): ThemeMode {
  if (typeof window === "undefined") return "system";
  const guardado = window.localStorage.getItem(STORAGE_KEY);
  return guardado === "light" || guardado === "dark" || guardado === "system" ? guardado : "system";
}

/**
 * Aplica el tema elegido al documento (`data-theme` en <html>) y lo persiste.
 * "system" no fija el atributo: styles/global.css sigue prefers-color-scheme.
 */
export function ThemeProvider({ children }: { children: ReactNode }) {
  const [mode, setModeState] = useState<ThemeMode>(leerModoGuardado);

  useEffect(() => {
    const root = document.documentElement;
    if (mode === "system") {
      root.removeAttribute("data-theme");
    } else {
      root.setAttribute("data-theme", mode);
    }
    window.localStorage.setItem(STORAGE_KEY, mode);
  }, [mode]);

  const value = useMemo<ThemeContextValue>(
    () => ({ mode, setMode: setModeState }),
    [mode],
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}
