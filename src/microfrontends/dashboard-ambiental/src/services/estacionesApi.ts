import type { AlertasResponse, EstacionesResponse, SerieHorariaResponse } from "../types/dashboard.types";

const WEBHOOK_URL = import.meta.env.VITE_N8N_ESTACIONES_WEBHOOK_URL;
const SERIE_HORARIA_WEBHOOK_URL = import.meta.env.VITE_N8N_SERIE_HORARIA_WEBHOOK_URL;
const ALERTAS_WEBHOOK_URL = import.meta.env.VITE_N8N_ALERTAS_WEBHOOK_URL;
const API_KEY = import.meta.env.VITE_N8N_API_KEY;

export class EstacionesApiError extends Error {}

async function pedirJson<T>(url: string | undefined, envVarFaltante: string, mensajeErrorGenerico: string): Promise<T> {
  if (!url) {
    throw new EstacionesApiError(`${envVarFaltante} no está configurada. Revisa el archivo .env.`);
  }

  const headers: Record<string, string> = {};
  if (API_KEY) headers["X-API-Key"] = API_KEY;

  let res: Response;
  try {
    res = await fetch(url, { headers });
  } catch {
    throw new EstacionesApiError("No se pudo contactar al webhook de n8n. ¿Está levantado docker compose?");
  }

  let json: unknown;
  try {
    json = await res.json();
  } catch {
    throw new EstacionesApiError("El webhook respondió con un cuerpo que no es JSON válido.");
  }

  if (!res.ok) {
    const mensaje = (json as { mensaje?: string } | null)?.mensaje ?? mensajeErrorGenerico;
    throw new EstacionesApiError(mensaje);
  }

  return json as T;
}

/**
 * Pide al webhook GET /estaciones de n8n (FLUJO C) la última medición (y la
 * anterior) por estación y parámetro. Ver src/n8n-workflows/Flujo C.json.
 */
export async function obtenerEstaciones(): Promise<EstacionesResponse> {
  return pedirJson<EstacionesResponse>(
    WEBHOOK_URL,
    "VITE_N8N_ESTACIONES_WEBHOOK_URL",
    "Error al consultar las estaciones.",
  );
}

/**
 * Pide al webhook GET /estaciones/serie-horaria de n8n (FLUJO C) el promedio
 * horario de PM2.5/PM10 de las últimas 24 horas. Ver src/n8n-workflows/Flujo C.json.
 */
export async function obtenerSerieHoraria(): Promise<SerieHorariaResponse> {
  return pedirJson<SerieHorariaResponse>(
    SERIE_HORARIA_WEBHOOK_URL,
    "VITE_N8N_SERIE_HORARIA_WEBHOOK_URL",
    "Error al consultar la serie horaria de PM2.5/PM10.",
  );
}

/** Pide al webhook GET /alertas de n8n las alertas de la tabla `alertas_anomalias`. */
export async function obtenerAlertas(): Promise<AlertasResponse> {
  return pedirJson<AlertasResponse>(
    ALERTAS_WEBHOOK_URL,
    "VITE_N8N_ALERTAS_WEBHOOK_URL",
    "Error al consultar las alertas del sistema.",
  );
}
