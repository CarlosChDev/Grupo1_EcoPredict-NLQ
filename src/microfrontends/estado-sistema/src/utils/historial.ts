import type { HistorialEntry } from "../types/status.types";

const STORAGE_KEY = "ecopredict:estado-sistema:historial";
export const MAX_ENTRADAS = 50;

type HistorialEntrySerializado = Omit<HistorialEntry, "timestamp" | "tipo" | "entorno"> & {
  timestamp: string | null;
  tipo?: HistorialEntry["tipo"];
  entorno?: HistorialEntry["entorno"];
};

/** El historial vive en localStorage: es diagnóstico del navegador de quien lo mira, no dato compartido del backend. */
export function cargarHistorial(): HistorialEntry[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const datos = JSON.parse(raw) as HistorialEntrySerializado[];
    // Entradas guardadas antes de separar ping real/reachability y local/producción usan los valores previos por defecto.
    return datos.map((d) => ({
      ...d,
      tipo: d.tipo ?? "real",
      entorno: d.entorno ?? "local",
      timestamp: d.timestamp ? new Date(d.timestamp) : null,
    }));
  } catch {
    return [];
  }
}

export function guardarHistorial(historial: HistorialEntry[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(historial.slice(0, MAX_ENTRADAS)));
  } catch {
    // localStorage puede fallar (modo privado, cuota llena); el historial sigue funcionando en memoria.
  }
}
