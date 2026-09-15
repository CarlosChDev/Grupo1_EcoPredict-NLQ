/**
 * Tipos de vista para Dashboard Ambiental.
 *
 * IMPORTANTE: todavía no existe un webhook n8n que exponga estos datos
 * (FLUJO A solo INSERTA en `estaciones`/`mediciones_aire`, no expone
 * lectura por HTTP — ver src/n8n-workflows/FLUJO A.json). Estas formas
 * están pensadas para calzar 1:1 con esas tablas cuando ese webhook
 * exista; mientras tanto la página consume `data/mockDashboardData.ts`.
 */

export type ParametroCalidadAire = "pm25" | "pm10" | "no2" | "so2" | "o3" | "co";

export type NivelEstado = "bueno" | "moderado" | "malo";

export interface MedicionParametro {
  parametro: ParametroCalidadAire;
  valor: number;
  /** Valor de la lectura anterior (misma estación/parámetro), para la flecha de tendencia. */
  valorAnterior?: number;
  unidad: string;
  medidoEn: string;
}

export interface EstacionResumen {
  id: number;
  nombre: string;
  zona: string | null;
  mediciones: MedicionParametro[];
}

/** Un punto horario de la serie PM2.5/PM10 de las últimas 24 horas (agregado de todas las estaciones). */
export interface PuntoSerieHoraria {
  horaIso: string;
  pm25: number | null;
  pm10: number | null;
}
