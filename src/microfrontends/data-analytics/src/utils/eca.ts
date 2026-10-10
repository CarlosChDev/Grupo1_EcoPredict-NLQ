import type { NivelEstado, ParametroCalidadAire } from "../types/analytics.types";

/**
 * Límites del ECA-Aire nacional (D.S. N° 003-2017-MINAM) usados como referencia
 * de comparación. Todos en µg/m³ (igual que el campo `unidad` que trae FLUJO C).
 */
export const ECA_LIMITE: Record<ParametroCalidadAire, number> = {
  pm25: 50, // 24 h
  pm10: 100, // 24 h
  so2: 250, // 24 h
  no2: 200, // 1 h
  o3: 100, // 8 h
  co: 10000, // 8 h
};

/** % del ECA que representa una lectura. */
export function porcentajeEca(parametro: ParametroCalidadAire, valor: number): number {
  return Math.round((valor / ECA_LIMITE[parametro]) * 100);
}

export function nivelPorEca(parametro: ParametroCalidadAire, valor: number): NivelEstado {
  const pct = porcentajeEca(parametro, valor);
  if (pct <= 50) return "bueno";
  if (pct <= 100) return "moderado";
  return "malo";
}
