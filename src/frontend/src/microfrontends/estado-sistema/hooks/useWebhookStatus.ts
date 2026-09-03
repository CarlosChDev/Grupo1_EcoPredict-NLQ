import { useCallback, useEffect, useState } from "react";
import { verificarReachability, verificarWebhookReal } from "../services/statusApi";
import type { Entorno, HistorialEntry, WebhookCheckResult } from "../types/status.types";
import { cargarHistorial, guardarHistorial, MAX_ENTRADAS } from "../utils/historial";

const INTERVALO_AUTO_MS = 5 * 60 * 1000;

export function useWebhookStatus(entorno: Entorno) {
  const [resultado, setResultado] = useState<WebhookCheckResult | null>(null);
  const [verificando, setVerificando] = useState(false);
  const [ultimaExitosa, setUltimaExitosa] = useState<Date | null>(null);
  const [historial, setHistorial] = useState<HistorialEntry[]>(() => cargarHistorial());

  const registrar = useCallback((r: WebhookCheckResult) => {
    setResultado(r);
    if (r.estado === "operativo" && r.timestamp) setUltimaExitosa(r.timestamp);
    setHistorial((prev) => {
      const entrada: HistorialEntry = { ...r, id: crypto.randomUUID() };
      const siguiente = [entrada, ...prev].slice(0, MAX_ENTRADAS);
      guardarHistorial(siguiente);
      return siguiente;
    });
  }, []);

  /** Botón "Probar conexión ahora": ping real a Flujo B, incluye el nodo de IA. */
  const verificar = useCallback(async () => {
    setVerificando(true);
    registrar(await verificarWebhookReal(entorno));
    setVerificando(false);
  }, [entorno, registrar]);

  /**
   * Chequeo automático cada 5 min del entorno seleccionado: reachability
   * liviano, SIN nodo de IA. El ping real (con costo de cuota) queda
   * reservado al botón manual. Cambiar de entorno reinicia el intervalo y
   * dispara un chequeo inmediato del nuevo entorno.
   */
  useEffect(() => {
    let cancelado = false;
    setResultado(null);
    setUltimaExitosa(null);

    async function chequeoAutomatico() {
      const r = await verificarReachability(entorno);
      if (!cancelado) registrar(r);
    }

    chequeoAutomatico();
    const id = setInterval(chequeoAutomatico, INTERVALO_AUTO_MS);
    return () => {
      cancelado = true;
      clearInterval(id);
    };
  }, [entorno, registrar]);

  return { resultado, verificando, ultimaExitosa, historial, verificar };
}
