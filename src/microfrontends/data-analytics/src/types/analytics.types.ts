/**
 * Tipos de vista para Data Analytics (HU-23 — Panel de Analítica Ambiental, Fase 2).
 *
 * Calzan 1:1 con las respuestas de los webhooks de n8n del flujo de
 * analítica (`/webhook/analitica/...`):
 * - GET /distritos: distritos con datos y si alcanzan para 7 / 30 días.
 * - GET /comparativo?distritos=a,b&dias=7: promedio del periodo vs. el
 *   anterior y serie diaria por distrito (2 a 4 distritos).
 * - GET /ranking-eca?parametro=pm25&dias=7: días sobre el ECA de 24 h.
 * - GET /patron-horario?distrito=a&parametro=pm25&dias=7: promedio por hora.
 * - GET /resumen-ia?distrito=a: texto semanal redactado por IA.
 *
 * Todas responden `{ ok: false, codigo, mensaje }` con HTTP 4xx/5xx al fallar.
 */

/** Los parámetros que agrega el flujo de analítica. */
export type ParametroAnalitica = "pm25" | "pm10";

export type DiasPeriodo = 7 | 30;

export type Tendencia = "sube" | "baja" | "estable";

export interface DistritoRef {
  /** Slug que aceptan los webhooks, p.ej. "san-juan-de-lurigancho". */
  id: string;
  nombre: string;
}

export interface Periodo {
  /** Fechas `YYYY-MM-DD` (hora de Lima). */
  desde: string;
  hasta: string;
}

export interface ErrorRespuesta {
  ok: false;
  codigo: string;
  mensaje: string;
}

/* ---------- GET /distritos ---------- */

export interface DistritoDisponible extends DistritoRef {
  diasConDato: number;
  primerDato: string;
  ultimoDato: string;
  datosSuficientes7: boolean;
  datosSuficientes30: boolean;
}

export interface DistritosResponse {
  ok: true;
  generadoEn: string;
  distritos: DistritoDisponible[];
}

/* ---------- GET /comparativo ---------- */

export interface ResumenParametro {
  unidad: string;
  promedio: number | null;
  anterior: number | null;
  variacionPct: number | null;
  tendencia: Tendencia | null;
  diasConDato: number;
  diasExcedidos: number;
  limiteEca: number;
}

export interface PuntoSerieDiaria {
  fecha: string;
  pm25: number | null;
  pm10: number | null;
}

export interface DistritoComparado extends DistritoRef {
  datosSuficientes: boolean;
  /** Solo viene cuando `datosSuficientes` es false. */
  ultimoDato?: string | null;
  parametros: Record<ParametroAnalitica, ResumenParametro> | null;
  serie: PuntoSerieDiaria[];
}

export interface ComparativoResponse {
  ok: true;
  generadoEn: string;
  dias: DiasPeriodo;
  periodo: Periodo;
  periodoAnterior: Periodo;
  distritos: DistritoComparado[];
}

/* ---------- GET /ranking-eca ---------- */

export interface FilaRanking {
  posicion: number;
  distrito: DistritoRef;
  diasExcedidos: number;
  diasConDato: number;
  promedio: number;
  /** Lectura más alta del periodo (no el promedio diario más alto). */
  maximo: number;
}

export interface RankingEcaResponse {
  ok: true;
  generadoEn: string;
  dias: DiasPeriodo;
  parametro: ParametroAnalitica;
  unidad: string;
  limiteEca: number;
  criterio: string;
  ranking: FilaRanking[];
  /** Ids de distritos que no entran al ranking por falta de datos. */
  sinDatosSuficientes: string[];
}

/* ---------- GET /patron-horario ---------- */

export interface PuntoHorario {
  /** 0–23, hora de Lima. */
  hora: number;
  promedio: number | null;
  /** Mediciones que entran en el promedio de esa hora. */
  n: number;
}

export interface PatronHorarioResponse {
  ok: true;
  generadoEn: string;
  distrito: DistritoRef;
  dias: DiasPeriodo;
  parametro: ParametroAnalitica;
  unidad: string;
  zonaHoraria: string;
  datosSuficientes: boolean;
  horas: PuntoHorario[];
  /** null mientras no haya datos suficientes. */
  horaCritica: number | { hora: number; promedio?: number | null } | null;
}

/* ---------- GET /resumen-ia ---------- */

export interface ResumenIaResponse {
  ok: true;
  generadoEn: string;
  distrito: DistritoRef;
  disponible: boolean;
  semana: { inicio: string; fin: string } | null;
  resumen: string | null;
  /** p.ej. "groq:openai/gpt-oss-120b". */
  modelo: string | null;
  resumenGeneradoEn: string | null;
}
