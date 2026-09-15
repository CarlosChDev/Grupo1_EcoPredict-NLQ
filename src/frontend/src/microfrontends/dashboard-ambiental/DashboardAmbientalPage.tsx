import { useEffect, useState } from "react";
import { usePageHeader } from "../../shell/layout/usePageHeader";
import { IncaIndexCard } from "./components/IncaIndexCard";
import { PmTrendChart } from "./components/PmTrendChart";
import { PollutantsGrid } from "./components/PollutantsGrid";
import { StationRanking } from "./components/StationRanking";
import { SystemAlerts } from "./components/SystemAlerts";
import { EstacionesApiError, obtenerAlertas, obtenerEstaciones, obtenerSerieHoraria } from "./services/estacionesApi";
import type { AlertaSistema, EstacionResumen, PuntoSerieHoraria } from "./types/dashboard.types";
import "./DashboardAmbientalPage.css";

type Estado =
  | { tipo: "cargando" }
  | { tipo: "error"; mensaje: string }
  | { tipo: "listo"; estaciones: EstacionResumen[]; totalEstaciones: number; generadoEn: string };

type EstadoSerieHoraria =
  | { tipo: "cargando" }
  | { tipo: "error"; mensaje: string }
  | { tipo: "listo"; serie: PuntoSerieHoraria[] };

type EstadoAlertas =
  | { tipo: "cargando" }
  | { tipo: "error"; mensaje: string }
  | { tipo: "listo"; alertas: AlertaSistema[] };

/**
 * Microfrontend: Dashboard Ambiental (ver informe §4.2.2).
 *
 * Consume los webhooks de n8n (FLUJO C, ver src/n8n-workflows/Flujo C.json):
 * GET /estaciones para la última medición por estación/parámetro, y GET
 * /estaciones/serie-horaria para la tendencia de PM2.5/PM10 de las últimas 24h.
 */
export function DashboardAmbientalPage() {
  usePageHeader({
    titulo: "Panel de calidad del aire",
    subtitulo: "Lima Metropolitana · datos horarios",
  });

  const [estado, setEstado] = useState<Estado>({ tipo: "cargando" });
  const [estadoSerie, setEstadoSerie] = useState<EstadoSerieHoraria>({ tipo: "cargando" });
  const [estadoAlertas, setEstadoAlertas] = useState<EstadoAlertas>({ tipo: "cargando" });
  const [estacionReferenciaId, setEstacionReferenciaId] = useState<number | null>(null);

  useEffect(() => {
    let cancelado = false;

    obtenerEstaciones()
      .then((respuesta) => {
        if (!cancelado)
          setEstado({
            tipo: "listo",
            estaciones: respuesta.estaciones,
            totalEstaciones: respuesta.total_estaciones,
            generadoEn: respuesta.generado_en,
          });
      })
      .catch((err) => {
        if (cancelado) return;
        const mensaje = err instanceof EstacionesApiError ? err.message : "Error inesperado al cargar estaciones.";
        setEstado({ tipo: "error", mensaje });
      });

    obtenerSerieHoraria()
      .then((respuesta) => {
        if (!cancelado) setEstadoSerie({ tipo: "listo", serie: respuesta.serie });
      })
      .catch((err) => {
        if (cancelado) return;
        const mensaje =
          err instanceof EstacionesApiError ? err.message : "Error inesperado al cargar la serie horaria.";
        setEstadoSerie({ tipo: "error", mensaje });
      });

    obtenerAlertas()
      .then((respuesta) => {
        if (!cancelado) setEstadoAlertas({ tipo: "listo", alertas: respuesta.alertas });
      })
      .catch((err) => {
        if (cancelado) return;
        const mensaje = err instanceof EstacionesApiError ? err.message : "Error inesperado al cargar alertas.";
        setEstadoAlertas({ tipo: "error", mensaje });
      });

    return () => {
      cancelado = true;
    };
  }, []);

  if (estado.tipo === "cargando") {
    return (
      <div className="dashboard-page">
        <div className="dashboard-mock-banner">Cargando estaciones…</div>
      </div>
    );
  }

  if (estado.tipo === "error") {
    return (
      <div className="dashboard-page">
        <div className="dashboard-mock-banner">No se pudo cargar el dashboard: {estado.mensaje}</div>
      </div>
    );
  }

  if (estado.estaciones.length === 0) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-mock-banner">No hay estaciones con mediciones registradas todavía.</div>
      </div>
    );
  }

  const estacionReferencia =
    estado.estaciones.find((estacion) => estacion.id === estacionReferenciaId) ?? estado.estaciones[0];

  return (
    <div className="dashboard-page">
      <div className="dashboard-selector-row">
        <label htmlFor="estacion-referencia" className="eyebrow">
          Estación de referencia
        </label>
        <select
          id="estacion-referencia"
          value={estacionReferencia.id}
          onChange={(e) => setEstacionReferenciaId(Number(e.target.value))}
        >
          {estado.estaciones.map((estacion) => (
            <option key={estacion.id} value={estacion.id}>
              {estacion.nombre}
            </option>
          ))}
        </select>
      </div>

      <div className="dashboard-top-grid">
        <IncaIndexCard estacion={estacionReferencia} />
        <PollutantsGrid estacion={estacionReferencia} />
      </div>

      <div className="dashboard-bottom-grid">
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
        <StationRanking estaciones={estado.estaciones} />
      </div>

      <div className="dashboard-alerts-grid">
        {estadoAlertas.tipo === "listo" ? (
          <SystemAlerts alertas={estadoAlertas.alertas} />
        ) : (
          <div className="card pm-trend-pendiente-card">
            <div className="card-label">
              <span className="small-icon">⚠️</span>
              Alertas del Sistema
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
