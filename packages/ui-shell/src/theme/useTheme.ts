import { useContext } from "react";
import { ThemeContext } from "./ThemeContext";

/** Modo actual del tema + setter, y el siguiente modo en el ciclo claro → oscuro → sistema. */
export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme debe usarse dentro de <ThemeProvider>");

  const siguiente = ctx.mode === "light" ? "dark" : ctx.mode === "dark" ? "system" : "light";
  const ciclar = () => ctx.setMode(siguiente);

  return { ...ctx, ciclar };
}
