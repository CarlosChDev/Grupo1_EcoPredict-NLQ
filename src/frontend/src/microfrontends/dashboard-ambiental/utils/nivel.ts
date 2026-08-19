import type { NivelEstado } from "../types/dashboard.types";

const ORDEN: Record<NivelEstado, number> = { bueno: 0, moderado: 1, malo: 2 };

export const NIVEL_LABEL: Record<NivelEstado, string> = {
  bueno: "Bueno",
  moderado: "Moderado",
  malo: "Malo",
};

export const NIVEL_COLOR_VAR: Record<NivelEstado, string> = {
  bueno: "var(--status-good)",
  moderado: "var(--status-moderate)",
  malo: "var(--status-bad)",
};

export function peorNivel(niveles: NivelEstado[]): NivelEstado {
  return niveles.reduce<NivelEstado>(
    (peor, actual) => (ORDEN[actual] > ORDEN[peor] ? actual : peor),
    "bueno",
  );
}
