import type { EstadoWebhook, TipoPing } from "../types/status.types";

export const ESTADO_LABEL: Record<EstadoWebhook, string> = {
  operativo: "OPERATIVO",
  degradado: "DEGRADADO",
  caido: "CAÍDO",
  verificando: "VERIFICANDO…",
  desconocido: "SIN DATOS",
};

export const ESTADO_COLOR_VAR: Record<EstadoWebhook, string> = {
  operativo: "var(--good)",
  degradado: "var(--mod)",
  caido: "var(--bad)",
  verificando: "var(--aqua)",
  desconocido: "var(--ink-3)",
};

export const ESTADO_PILL_CLASS: Record<EstadoWebhook, string> = {
  operativo: "p-good",
  degradado: "p-mod",
  caido: "p-bad",
  verificando: "p-neutral",
  desconocido: "p-neutral",
};

export const TIPO_LABEL: Record<TipoPing, string> = {
  real: "🤖 Real (IA)",
  reachability: "🩺 Liviano",
};

export function formatearRelativo(fecha: Date): string {
  const minutos = Math.floor((Date.now() - fecha.getTime()) / 60000);
  if (minutos < 1) return "hace instantes";
  if (minutos === 1) return "hace 1 minuto";
  return `hace ${minutos} minutos`;
}
