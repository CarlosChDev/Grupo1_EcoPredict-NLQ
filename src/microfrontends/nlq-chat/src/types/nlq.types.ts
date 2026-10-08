/**
 * Tipos alineados 1:1 con el contrato del webhook `POST /webhook/nlq`
 * (ver src/n8n-workflows/FLUJO B.json). Cualquier cambio en el workflow
 * de n8n debe reflejarse aquí primero.
 */

export type ParametroCalidadAire = "pm25" | "pm10" | "no2" | "so2" | "o3" | "co";

export interface NlqRequest {
  pregunta: string;
}

export interface NlqPuntoSerie {
  x: string;
  y: number;
  estacion: string;
}

/** 200 con datos — nodo "Armar payload (texto + grafico)" */
export interface NlqRespuestaConDatos {
  ok: true;
  codigo_http: 200;
  texto: string;
  modelo_usado: string;
  parametro: ParametroCalidadAire;
  rango: { desde: string; hasta: string };
  serie: NlqPuntoSerie[];
}

/** 200 sin datos disponibles — nodo "Respond 200 sin datos1" */
export interface NlqRespuestaSinDatos {
  ok: true;
  codigo_http: 200;
  mensaje: string;
  sugerencia: { desde: string; hasta: string } | null;
}

/** 400 — la pregunta no pasó "Validar entrada" */
export interface NlqErrorValidacion {
  ok: false;
  codigo_http: 400;
  errores: string[];
}

/** 422 — el LLM no devolvió un esquema de intención válido */
export interface NlqErrorEsquema {
  ok: false;
  codigo_http: 422;
  motivo: string;
}

export type NlqResponse =
  | NlqRespuestaConDatos
  | NlqRespuestaSinDatos
  | NlqErrorValidacion
  | NlqErrorEsquema;

export function tieneSerie(r: NlqResponse): r is NlqRespuestaConDatos {
  return r.ok && "serie" in r;
}

export function esError(r: NlqResponse): r is NlqErrorValidacion | NlqErrorEsquema {
  return !r.ok;
}

export type ChatRole = "usuario" | "asistente";

export interface ChatMessage {
  id: string;
  role: ChatRole;
  texto: string;
  timestamp: Date;
  respuesta?: NlqResponse;
}
