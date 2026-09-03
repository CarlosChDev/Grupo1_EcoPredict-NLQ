export type EstadoWebhook = "operativo" | "degradado" | "caido" | "verificando" | "desconocido";

/** "real" dispara el nodo de IA (gasta cuota); "reachability" corta en la validación de n8n, sin IA. */
export type TipoPing = "real" | "reachability";

/** Qué webhook de n8n se está diagnosticando. Ver services/statusApi.ts. */
export type Entorno = "local" | "produccion";

export interface WebhookCheckResult {
  estado: EstadoWebhook;
  tipo: TipoPing;
  entorno: Entorno;
  latenciaMs: number | null;
  codigoHttp: number | null;
  apiKeyEnviada: boolean;
  rateLimitRestante: string | null;
  timestamp: Date | null;
  mensajeError?: string;
}

export interface HistorialEntry extends WebhookCheckResult {
  id: string;
}
