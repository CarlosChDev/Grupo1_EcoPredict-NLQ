import { createContext, ReactNode, useEffect, useMemo, useState } from "react";

export type Densidad = "compacta" | "normal" | "amplia";
export type VistaInicio = "inicio" | "dashboard-ambiental" | "nlq-chat" | "estado-sistema";

export interface PreferencesState {
  densidad: Densidad;
  altoContraste: boolean;
  reducirMovimiento: boolean;
  vistaInicio: VistaInicio;
}

export interface PreferencesContextValue extends PreferencesState {
  setDensidad: (densidad: Densidad) => void;
  setAltoContraste: (activo: boolean) => void;
  setReducirMovimiento: (activo: boolean) => void;
  setVistaInicio: (vista: VistaInicio) => void;
}

const STORAGE_KEY = "ecopredict-preferencias";

const ESTADO_POR_DEFECTO: PreferencesState = {
  densidad: "normal",
  altoContraste: false,
  reducirMovimiento: false,
  vistaInicio: "inicio",
};

export const PreferencesContext = createContext<PreferencesContextValue | null>(null);

function leerEstadoGuardado(): PreferencesState {
  if (typeof window === "undefined") return ESTADO_POR_DEFECTO;
  try {
    const guardado = window.localStorage.getItem(STORAGE_KEY);
    if (!guardado) return ESTADO_POR_DEFECTO;
    return { ...ESTADO_POR_DEFECTO, ...JSON.parse(guardado) };
  } catch {
    return ESTADO_POR_DEFECTO;
  }
}

/**
 * Aplica las preferencias de Apariencia/Accesibilidad al documento
 * (`data-density`, `data-contrast`, `data-motion` en <html>, ver
 * styles/global.css) y las persiste. `vistaInicio` la lee el shell al
 * resolver la ruta "/" (ver shell/App.tsx).
 */
export function PreferencesProvider({ children }: { children: ReactNode }) {
  const [estado, setEstado] = useState<PreferencesState>(leerEstadoGuardado);

  useEffect(() => {
    const root = document.documentElement;
    root.setAttribute("data-density", estado.densidad);
    if (estado.altoContraste) {
      root.setAttribute("data-contrast", "alto");
    } else {
      root.removeAttribute("data-contrast");
    }
    if (estado.reducirMovimiento) {
      root.setAttribute("data-motion", "reducida");
    } else {
      root.removeAttribute("data-motion");
    }
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(estado));
  }, [estado]);

  const value = useMemo<PreferencesContextValue>(
    () => ({
      ...estado,
      setDensidad: (densidad) => setEstado((prev) => ({ ...prev, densidad })),
      setAltoContraste: (altoContraste) => setEstado((prev) => ({ ...prev, altoContraste })),
      setReducirMovimiento: (reducirMovimiento) => setEstado((prev) => ({ ...prev, reducirMovimiento })),
      setVistaInicio: (vistaInicio) => setEstado((prev) => ({ ...prev, vistaInicio })),
    }),
    [estado],
  );

  return <PreferencesContext.Provider value={value}>{children}</PreferencesContext.Provider>;
}
