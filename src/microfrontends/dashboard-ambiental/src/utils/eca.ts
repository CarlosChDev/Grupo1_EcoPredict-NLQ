import type { NivelEstado, ParametroCalidadAire } from "../types/dashboard.types";

/**
 * Límites del ECA-Aire nacional (D.S. N° 003-2017-MINAM) usados como referencia
 * de comparación. Todos en µg/m³, igual que el campo `unidad` que trae FLUJO A/C
 * para los 6 parámetros (el CO del ECA es 10 mg/m³ = 10 000 µg/m³ — antes este
 * límite estaba en mg/m³ mientras el dato llega en µg/m³, lo que disparaba el
 * % del ECA x1000 y el Índice INCA a valores absurdos como 16089).
 */
export const ECA_LIMITE: Record<ParametroCalidadAire, number> = {
  pm25: 50, // 24 h
  pm10: 100, // 24 h
  so2: 250, // 24 h
  no2: 200, // 1 h
  o3: 100, // 8 h
  co: 10000, // 8 h
};

/**
 * % del ECA que representa una lectura. Es también la base del Índice INCA:
 * el contaminante que más se acerca o supera su límite es el que domina el
 * índice general, igual que en los índices de calidad del aire estándar.
 */
export function porcentajeEca(parametro: ParametroCalidadAire, valor: number): number {
  return Math.round((valor / ECA_LIMITE[parametro]) * 100);
}

export function nivelPorEca(parametro: ParametroCalidadAire, valor: number): NivelEstado {
  const pct = porcentajeEca(parametro, valor);
  if (pct <= 50) return "bueno";
  if (pct <= 100) return "moderado";
  return "malo";
}

export function nivelPorIndice(indice: number): NivelEstado {
  if (indice <= 50) return "bueno";
  if (indice <= 100) return "moderado";
  return "malo";
}
