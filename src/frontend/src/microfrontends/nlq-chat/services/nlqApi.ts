import type { NlqRequest, NlqResponse } from "../types/nlq.types";

const WEBHOOK_URL = import.meta.env.VITE_N8N_WEBHOOK_URL;

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

  let res: Response;
  try {
    res = await fetch(WEBHOOK_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new NlqApiError("No se pudo contactar al webhook de n8n. ¿Está levantado docker compose?");
  }

  let rawText = "";
  try {
    rawText = await res.text();
  } catch {
    throw new NlqApiError("No se pudo leer la respuesta del webhook.");
  }

  let json: unknown;
  try {
    const cleanedText = rawText.trim().startsWith("=") ? rawText.trim().slice(1) : rawText.trim();
    json = JSON.parse(cleanedText);
  } catch {
    if (res.ok) {
      json = {
        ok: true,
        codigo_http: 200,
        mensaje: rawText || "No hay mediciones registradas para ese contaminante en el rango seleccionado.",
      };
    } else {
      throw new NlqApiError("El webhook respondió con un cuerpo que no es JSON válido.");
    }
  }

  return json as NlqResponse;
}
