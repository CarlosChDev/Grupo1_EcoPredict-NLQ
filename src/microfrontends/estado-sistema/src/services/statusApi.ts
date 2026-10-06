import type { Entorno, TipoPing, WebhookCheckResult } from "../types/status.types";

const API_KEY = import.meta.env.VITE_N8N_API_KEY;

/** URL por entorno. "produccion" viene de la nube (OCI) — ver .env.example. Solo alimenta este diagnóstico, no el chat NLQ real. */
const WEBHOOK_URL_POR_ENTORNO: Record<Entorno, string | undefined> = {
  local: import.meta.env.VITE_N8N_WEBHOOK_URL,
  produccion: import.meta.env.VITE_N8N_WEBHOOK_URL_PROD,
};

export function urlDeEntorno(entorno: Entorno): string | undefined {
  return WEBHOOK_URL_POR_ENTORNO[entorno];
}

/**
 * Pregunta fija que dispara Flujo B de verdad (nodo IA de Gemini incluido).
 * Cuesta cuota real del modelo, así que SOLO se usa para el botón manual
 * "Probar conexión ahora" — nunca para el auto-check. Ver src/n8n-workflows/FLUJO B.json.
 */
const PREGUNTA_PING = "ping de estado del sistema";

/**
 * Payload sin "pregunta": el nodo "Validar entrada" de Flujo B lo rechaza
 * con 400 en ~50ms, antes de llegar al nodo de IA. Sirve para confirmar que
 * n8n + el workflow están vivos sin gastar cuota de Gemini — por eso es lo
 * que usa el chequeo automático cada 5 min (ver useWebhookStatus).
 */
const PAYLOAD_REACHABILITY = {};

async function ejecutarPing(
  entorno: Entorno,
  payload: unknown,
  tipo: TipoPing,
  esExitoso: (status: number) => boolean,
): Promise<WebhookCheckResult> {
  const apiKeyEnviada = Boolean(API_KEY);
  const url = urlDeEntorno(entorno);

  if (!url) {
    return {
      estado: "desconocido",
      tipo,
      entorno,
      latenciaMs: null,
      codigoHttp: null,
      apiKeyEnviada,
      rateLimitRestante: null,
      timestamp: new Date(),
      mensajeError:
        entorno === "local"
          ? "VITE_N8N_WEBHOOK_URL no está configurada. Revisa el archivo .env."
          : "VITE_N8N_WEBHOOK_URL_PROD no está configurada. Revisa el archivo .env.",
    };
  }

  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (API_KEY) headers["X-API-Key"] = API_KEY;

  const inicio = performance.now();
  try {
    const res = await fetch(url, {
      method: "POST",
      headers,
      body: JSON.stringify(payload),
    });
    const latenciaMs = Math.round(performance.now() - inicio);

    let cuerpoValido = true;
    try {
      await res.clone().json();
    } catch {
      cuerpoValido = false;
    }

    return {
      estado: cuerpoValido && esExitoso(res.status) ? "operativo" : "degradado",
      tipo,
      entorno,
      latenciaMs,
      codigoHttp: res.status,
      apiKeyEnviada,
      rateLimitRestante: leerRateLimit(res.headers),
      timestamp: new Date(),
      mensajeError: cuerpoValido ? undefined : "El webhook respondió con un cuerpo que no es JSON válido.",
    };
  } catch {
    // El navegador oculta el motivo real de un fetch fallido (server caído, timeout, CORS bloqueado
    // en preflight, etc. dan el mismo TypeError) — no hay forma de distinguirlos desde el código.
    return {
      estado: "caido",
      tipo,
      entorno,
      latenciaMs: Math.round(performance.now() - inicio),
      codigoHttp: null,
      apiKeyEnviada,
      rateLimitRestante: null,
      timestamp: new Date(),
      mensajeError:
        entorno === "local"
          ? "No se pudo contactar al webhook de n8n. ¿Está levantado docker compose?"
          : "No se pudo contactar al webhook de producción. Puede estar caído, o bloqueando el origen por CORS (revisa la consola del navegador para confirmar).",
    };
  }
}

/** Ping real a Flujo B (incluye el nodo de IA) — usar solo desde una acción explícita del usuario. */
export function verificarWebhookReal(entorno: Entorno): Promise<WebhookCheckResult> {
  return ejecutarPing(entorno, { pregunta: PREGUNTA_PING }, "real", (status) => status >= 200 && status < 300);
}

/** Chequeo liviano: confirma que n8n + Flujo B responden, sin invocar al modelo de IA. */
export function verificarReachability(entorno: Entorno): Promise<WebhookCheckResult> {
  return ejecutarPing(
    entorno,
    PAYLOAD_REACHABILITY,
    "reachability",
    (status) => status === 400 || (status >= 200 && status < 300),
  );
}

/** n8n no expone rate limiting propio; esto solo aplica si hay un proxy/gateway delante que sí lo haga. */
function leerRateLimit(headers: Headers): string | null {
  const restante = headers.get("x-ratelimit-remaining");
  const limite = headers.get("x-ratelimit-limit");
  if (!restante || !limite) return null;
  return `${restante} / ${limite} rpm`;
}
