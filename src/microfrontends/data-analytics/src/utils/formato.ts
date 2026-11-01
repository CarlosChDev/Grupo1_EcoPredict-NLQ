import type { ParametroAnalitica } from "../types/analytics.types";

export const PARAMETRO_LABEL: Record<ParametroAnalitica, string> = { pm25: "PM2.5", pm10: "PM10" };

/** Mismos colores que el gráfico de tendencia del Dashboard Ambiental. */
export const PARAMETRO_COLOR: Record<ParametroAnalitica, string> = { pm25: "var(--aqua)", pm10: "var(--accent)" };

const ZONA_LIMA = "America/Lima";

/** Número con un decimal en formato peruano ("23,1"). */
export function f1(valor: number): string {
  return valor.toLocaleString("es-PE", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
}

/** `YYYY-MM-DD` como fecha local, sin el corrimiento de zona de `new Date("YYYY-MM-DD")`. */
function fechaLocal(fecha: string): Date {
  const [y, m, d] = fecha.split("-").map(Number);
  return new Date(y, m - 1, d);
}

/** "2026-10-22" → "22 oct." */
export function fechaCorta(fecha: string): string {
  return fechaLocal(fecha).toLocaleDateString("es-PE", { day: "numeric", month: "short" });
}

/** "22 – 28 oct." o "29 sept. – 28 oct." */
export function rangoFechas(desde: string, hasta: string): string {
  const a = fechaLocal(desde);
  const b = fechaLocal(hasta);
  if (a.getMonth() === b.getMonth()) return `${a.getDate()}–${fechaCorta(hasta)}`;
  return `${fechaCorta(desde)} – ${fechaCorta(hasta)}`;
}

/** Fecha-hora ISO → "lun. 26 oct. 19:15" en hora de Lima. */
export function fechaHoraLima(iso: string): string {
  const d = new Date(iso);
  const dia = d.toLocaleDateString("es-PE", { weekday: "short", day: "numeric", month: "short", timeZone: ZONA_LIMA });
  const hora = d.toLocaleTimeString("es-PE", { hour: "2-digit", minute: "2-digit", hour12: false, timeZone: ZONA_LIMA });
  return `${dia} ${hora}`;
}

/** 8 → "08:00" */
export function horaDelDia(hora: number): string {
  return `${String(hora).padStart(2, "0")}:00`;
}

/** "groq:openai/gpt-oss-120b" → "gpt-oss-120b · Groq" */
export function etiquetaModelo(modelo: string): string {
  const [proveedor, ...resto] = modelo.split(":");
  if (resto.length === 0) return modelo;
  const nombre = resto.join(":").split("/").pop() ?? modelo;
  return `${nombre} · ${proveedor.charAt(0).toUpperCase()}${proveedor.slice(1)}`;
}

/** "la-molina" → "La Molina", para ids que no vienen en /distritos. */
export function nombreDesdeId(id: string): string {
  return id
    .split("-")
    .map((p) => (["de", "del", "la", "el"].includes(p) ? p : `${p.charAt(0).toUpperCase()}${p.slice(1)}`))
    .join(" ")
    .replace(/^./, (c) => c.toUpperCase());
}
