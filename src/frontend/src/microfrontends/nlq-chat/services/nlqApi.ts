import type { NlqRequest, NlqResponse } from "../types/nlq.types";

const WEBHOOK_URL = import.meta.env.VITE_N8N_WEBHOOK_URL;
const API_KEY = import.meta.env.VITE_N8N_API_KEY;

export class NlqApiError extends Error {}

/**
 * Envía la pregunta en lenguaje natural al webhook de n8n (FLUJO B) y
 * devuelve el JSON tal cual lo arma el workflow, sea éxito o error de
 * negocio (400/422) — todos son respuestas válidas del contrato NLQ.
 */
export async function preguntarNlq(payload: NlqRequest): Promise<NlqResponse> {
  if (!WEBHOOK_URL) {
    throw new NlqApiError("VITE_N8N_WEBHOOK_URL no está configurada. Revisa el archivo .env.");
  }

  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (API_KEY) headers["X-API-Key"] = API_KEY;

  let res: Response;
  try {
    res = await fetch(WEBHOOK_URL, {
      method: "POST",
      headers,
      body: JSON.stringify(payload),
    });
  } catch {
    throw new NlqApiError("No se pudo contactar al webhook de n8n. ¿Está levantado docker compose?");
  }

  let json: unknown;
  try {
    json = await res.json();
  } catch {
    throw new NlqApiError("El webhook respondió con un cuerpo que no es JSON válido.");
  }

  return json as NlqResponse;
}
