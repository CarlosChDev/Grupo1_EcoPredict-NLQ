/**
 * Tipos de vista para Dashboard Ambiental.
 *
 * Calzan 1:1 con el contrato que arma el webhook de n8n (FLUJO C, ver
 * src/n8n-workflows/Flujo C.json):
 * - GET /estaciones ("Formatear contrato de respuesta"): última medición
 *   (y la anterior, para la flecha de tendencia) por estación y parámetro.
 * - GET /estaciones/serie-horaria ("Formatear serie horaria"): promedio
 *   horario de PM2.5/PM10 de todas las estaciones en las últimas 24h.
 * - GET /alertas: alertas de la tabla `alertas_anomalias` (detección de
 *   anomalías por umbral) más una alerta informativa de sincronización.
 */

export type ParametroCalidadAire = "pm25" | "pm10" | "no2" | "so2" | "o3" | "co";

export type NivelEstado = "bueno" | "moderado" | "malo";

export interface MedicionParametro {
  parametro: ParametroCalidadAire;
  valor: number;
  /** Valor de la lectura anterior (misma estación/parámetro), para la flecha de tendencia. */
  valorAnterior?: number | null;
  unidad: string;
  medidoEn: string;
}

export interface Coordenadas {
  lat: number;
  lon: number;
}

export interface EstacionResumen {
  id: number;
  nombre: string;
  zona: string | null;
  coordenadas: Coordenadas;
  mediciones: MedicionParametro[];
}

/** Cuerpo tal cual lo responde el webhook GET /estaciones. */
export interface EstacionesResponse {
  estaciones: EstacionResumen[];
  total_estaciones: number;
  generado_en: string;
}

/** Un punto horario de la serie PM2.5/PM10 de las últimas 24 horas (agregado de todas las estaciones). */
export interface PuntoSerieHoraria {
  hora: string;
  pm25: number | null;
  pm10: number | null;
}

/** Cuerpo tal cual lo responde el webhook GET /estaciones/serie-horaria. */
export interface SerieHorariaResponse {
  serie: PuntoSerieHoraria[];
}

export type TipoAlerta = "anomalia" | "sincronizacion";
export type SeveridadAlerta = "info" | "baja" | "moderada" | "alta" | "critica";

export interface AlertaSistema {
  tipo: TipoAlerta;
  severidad: SeveridadAlerta;
  titulo: string;
  mensaje: string;
  estacion: string | null;
  parametro: ParametroCalidadAire | null;
  valor: number | null;
  umbral: number | null;
  evento_en: string;
}

/** Cuerpo tal cual lo responde el webhook GET /alertas. */
export interface AlertasResponse {
  alertas: AlertaSistema[];
  total_alertas: number;
  generado_en: string;
}
