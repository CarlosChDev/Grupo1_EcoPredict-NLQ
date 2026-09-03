import type { EstadoWebhook, TipoPing } from "../types/status.types";

export const ESTADO_LABEL: Record<EstadoWebhook, string> = {
  operativo: "OPERATIVO",
  degradado: "DEGRADADO",
  caido: "CAÍDO",
  verificando: "VERIFICANDO…",
  desconocido: "SIN DATOS",
};

export const ESTADO_COLOR_VAR: Record<EstadoWebhook, string> = {
  operativo: "var(--status-good)",
  degradado: "var(--status-moderate)",
  caido: "var(--status-bad)",
  verificando: "var(--primary-cyan)",
  desconocido: "#6c7d94",
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
