import { useEffect, useState } from "react";
import { AlertsPanel } from "./components/AlertsPanel";
import { DistrictSummaryTable } from "./components/DistrictSummaryTable";
import { PmTrendChart } from "./components/PmTrendChart";
import { DataAnalyticsApiError, obtenerAlertas, obtenerEstaciones, obtenerSerieHoraria } from "./services/dataAnalyticsApi";
import type { AlertaSistema, EstacionResumen, PuntoSerieHoraria } from "./types/analytics.types";
import "./DataAnalyticsPage.css";

type Estado =
  | { tipo: "cargando" }
  | { tipo: "error"; mensaje: string }
  | { tipo: "listo"; estaciones: EstacionResumen[] };

type EstadoSerieHoraria =
  | { tipo: "cargando" }
  | { tipo: "error"; mensaje: string }
  | { tipo: "listo"; serie: PuntoSerieHoraria[] };

type EstadoAlertas =
  | { tipo: "cargando" }
  | { tipo: "error"; mensaje: string }
  | { tipo: "listo"; alertas: AlertaSistema[] };

/**
 * Microfrontend: Data Analytics (HU-03 — Panel de Analítica Ambiental, Fase 1).
 *
 * Reutiliza los webhooks de n8n que ya expone FLUJO C (los mismos que
 * consume Dashboard Ambiental) — no hay flujos nuevos que crear, solo una
 * vista distinta: resumen por distrito con categoría ECA y tendencia,
 * gráfico de PM2.5/PM10 de 24h, y alertas con sus factores (analisis_llm).
 */
export function DataAnalyticsPage() {
  const [estado, setEstado] = useState<Estado>({ tipo: "cargando" });
  const [estadoSerie, setEstadoSerie] = useState<EstadoSerieHoraria>({ tipo: "cargando" });
  const [estadoAlertas, setEstadoAlertas] = useState<EstadoAlertas>({ tipo: "cargando" });

  useEffect(() => {
    let cancelado = false;

    obtenerEstaciones()
      .then((respuesta) => {
        if (!cancelado) setEstado({ tipo: "listo", estaciones: respuesta.estaciones });
      })
      .catch((err) => {
        if (cancelado) return;
        const mensaje = err instanceof DataAnalyticsApiError ? err.message : "Error inesperado al cargar estaciones.";
        setEstado({ tipo: "error", mensaje });
      });

    obtenerSerieHoraria()
      .then((respuesta) => {
        if (!cancelado) setEstadoSerie({ tipo: "listo", serie: respuesta.serie });
      })
      .catch((err) => {
        if (cancelado) return;
        const mensaje =
          err instanceof DataAnalyticsApiError ? err.message : "Error inesperado al cargar la serie horaria.";
        setEstadoSerie({ tipo: "error", mensaje });
      });

    obtenerAlertas()
      .then((respuesta) => {
        if (!cancelado) setEstadoAlertas({ tipo: "listo", alertas: respuesta.alertas });
      })
      .catch((err) => {
        if (cancelado) return;
        const mensaje = err instanceof DataAnalyticsApiError ? err.message : "Error inesperado al cargar alertas.";
        setEstadoAlertas({ tipo: "error", mensaje });
      });

    return () => {
      cancelado = true;
    };
  }, []);

  if (estado.tipo === "cargando") {
    return (
      <div className="data-analytics-page">
        <div className="data-analytics-mock-banner">Cargando estaciones…</div>
      </div>
    );
  }

  if (estado.tipo === "error") {
    return (
      <div className="data-analytics-page">
        <div className="data-analytics-mock-banner">No se pudo cargar la analítica: {estado.mensaje}</div>
      </div>
    );
  }

  if (estado.estaciones.length === 0) {
    return (
      <div className="data-analytics-page">
        <div className="data-analytics-mock-banner">No hay estaciones con mediciones registradas todavía.</div>
      </div>
    );
  }

  return (
    <div className="data-analytics-page">
      <DistrictSummaryTable estaciones={estado.estaciones} />

      <div className="data-analytics-bottom-grid">
        {estadoSerie.tipo === "listo" ? (
          <PmTrendChart serie={estadoSerie.serie} />
        ) : (
          <div className="card pm-trend-pendiente-card">
            <div className="card-label">
              <span className="small-icon">📈</span>
              PM2.5 y PM10 · últimas 24 horas
            </div>
            <p className="pm-trend-pendiente-mensaje">
              {estadoSerie.tipo === "cargando" ? "Cargando serie horaria…" : `No se pudo cargar: ${estadoSerie.mensaje}`}
            </p>
          </div>
        )}

        {estadoAlertas.tipo === "listo" ? (
          <AlertsPanel alertas={estadoAlertas.alertas} />
        ) : (
          <div className="card pm-trend-pendiente-card">
            <div className="card-label">
              <span className="small-icon">⚠️</span>
              Alertas y factores asociados
            </div>
            <p className="pm-trend-pendiente-mensaje">
              {estadoAlertas.tipo === "cargando" ? "Cargando alertas…" : `No se pudo cargar: ${estadoAlertas.mensaje}`}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
