import type { AlertasResponse, EstacionesResponse, SerieHorariaResponse } from "../types/analytics.types";

const WEBHOOK_URL = import.meta.env.VITE_N8N_ESTACIONES_WEBHOOK_URL;
const SERIE_HORARIA_WEBHOOK_URL = import.meta.env.VITE_N8N_SERIE_HORARIA_WEBHOOK_URL;
const ALERTAS_WEBHOOK_URL = import.meta.env.VITE_N8N_ALERTAS_WEBHOOK_URL;
const API_KEY = import.meta.env.VITE_N8N_API_KEY;

export class DataAnalyticsApiError extends Error {}

async function pedirJson<T>(url: string | undefined, envVarFaltante: string, mensajeErrorGenerico: string): Promise<T> {
  if (!url) {
    throw new DataAnalyticsApiError(`${envVarFaltante} no está configurada. Revisa el archivo .env.`);
  }

  const headers: Record<string, string> = {};
  if (API_KEY) headers["X-API-Key"] = API_KEY;

  let res: Response;
  try {
    res = await fetch(url, { headers });
  } catch {
    throw new DataAnalyticsApiError("No se pudo contactar al webhook de n8n. ¿Está levantado docker compose?");
  }

  let json: unknown;
  try {
    json = await res.json();
  } catch {
    throw new DataAnalyticsApiError("El webhook respondió con un cuerpo que no es JSON válido.");
  }

  if (!res.ok) {
    const mensaje = (json as { mensaje?: string } | null)?.mensaje ?? mensajeErrorGenerico;
    throw new DataAnalyticsApiError(mensaje);
  }

  return json as T;
}

/**
 * Mismos webhooks que ya consume Dashboard Ambiental (FLUJO C) — la HU-03
 * no pide flujos nuevos, solo una vista distinta sobre los mismos datos.
 * Ver src/n8n-workflows/Flujo C.json.
 */
export async function obtenerEstaciones(): Promise<EstacionesResponse> {
  return pedirJson<EstacionesResponse>(
    WEBHOOK_URL,
    "VITE_N8N_ESTACIONES_WEBHOOK_URL",
    "Error al consultar las estaciones.",
  );
}

export async function obtenerSerieHoraria(): Promise<SerieHorariaResponse> {
  return pedirJson<SerieHorariaResponse>(
    SERIE_HORARIA_WEBHOOK_URL,
    "VITE_N8N_SERIE_HORARIA_WEBHOOK_URL",
    "Error al consultar la serie horaria de PM2.5/PM10.",
  );
}

/** Alertas de la tabla `alertas_anomalias` — `mensaje` es la columna `analisis_llm`. */
export async function obtenerAlertas(): Promise<AlertasResponse> {
  return pedirJson<AlertasResponse>(
    ALERTAS_WEBHOOK_URL,
    "VITE_N8N_ALERTAS_WEBHOOK_URL",
    "Error al consultar las alertas del sistema.",
  );
}
