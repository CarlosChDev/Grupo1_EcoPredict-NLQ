import type { NivelEstado, ParametroCalidadAire } from "../types/dashboard.types";

/**
 * Límites del ECA-Aire nacional (D.S. N° 003-2017-MINAM) usados como referencia
 * de comparación. Unidades consistentes con las que produce FLUJO A: µg/m³ para
 * todos los parámetros salvo CO, que se ingiere en mg/m³.
 */
export const ECA_LIMITE: Record<ParametroCalidadAire, number> = {
  pm25: 50, // 24 h
  pm10: 100, // 24 h
  so2: 250, // 24 h
  no2: 200, // 1 h
  o3: 100, // 8 h
  co: 10, // 8 h, mg/m³
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
