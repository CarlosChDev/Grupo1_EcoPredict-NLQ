import { useEffect, useState } from "react";
import { DistrictComparison } from "./components/DistrictComparison";
import { EcaRanking } from "./components/EcaRanking";
import { HourlyPattern } from "./components/HourlyPattern";
import { Esqueleto, PanelError, Segmentado } from "./components/Panel";
import { WeeklyAiSummary } from "./components/WeeklyAiSummary";
import { useRemoteData } from "./hooks/useRemoteData";
import { obtenerDistritos } from "./services/dataAnalyticsApi";
import type { DiasPeriodo, DistritoDisponible } from "./types/analytics.types";
import { fechaCorta, fechaHoraLima } from "./utils/formato";
import "./DataAnalyticsPage.css";

const OPCIONES_DIAS = [
  { valor: 7 as const, etiqueta: "Últimos 7 días" },
  { valor: 30 as const, etiqueta: "Últimos 30 días" },
];

/** Los primeros 3 distritos con datos de la última semana (o los 2 primeros, si no alcanza). */
function seleccionInicial(distritos: DistritoDisponible[]): string[] {
  const conDatos = distritos.filter((d) => d.datosSuficientes7).map((d) => d.id);
  if (conDatos.length >= 2) return conDatos.slice(0, 3);
  return distritos.slice(0, 2).map((d) => d.id);
}

/**
 * Microfrontend: Data Analytics (HU-23 — Panel de Analítica Ambiental, Fase 2).
 *
 * Histórico y comparación entre distritos sobre los webhooks del flujo de
 * analítica en n8n (`/webhook/analitica/...`). Cada bloque pide sus propios
 * datos, así que si uno falla los demás siguen funcionando.
 */
export function DataAnalyticsPage() {
  const [dias, setDias] = useState<DiasPeriodo>(7);
  const [seleccion, setSeleccion] = useState<string[]>([]);
  const [estado, reintentar] = useRemoteData((signal) => obtenerDistritos(signal), "distritos");

  useEffect(() => {
    if (estado.tipo === "listo") setSeleccion(seleccionInicial(estado.datos.distritos));
  }, [estado]);

  if (estado.tipo === "cargando" || (estado.tipo === "listo" && seleccion.length === 0 && estado.datos.distritos.length >= 2)) {
    return (
      <div className="data-analytics-page">
        <Esqueleto alto={56} />
        <Esqueleto alto={320} />
        <div className="data-analytics-grid">
          <Esqueleto alto={360} />
          <Esqueleto alto={360} />
        </div>
      </div>
    );
  }

  if (estado.tipo === "error") {
    return (
      <div className="data-analytics-page">
        <PanelError titulo="No se pudo cargar la analítica" mensaje={estado.mensaje} onReintentar={reintentar} />
      </div>
    );
  }

  const { distritos, generadoEn } = estado.datos;
  if (distritos.length < 2) {
    return (
      <div className="data-analytics-page">
        <p className="da-aviso">Se necesitan al menos 2 distritos con mediciones para mostrar la analítica.</p>
      </div>
    );
  }

  const ultimoDato = distritos.reduce((max, d) => (d.ultimoDato > max ? d.ultimoDato : max), distritos[0].ultimoDato);
  const seleccionados = seleccion
    .map((id) => distritos.find((d) => d.id === id))
    .filter((d): d is DistritoDisponible => d !== undefined);

  return (
    <div className="data-analytics-page">
      <div className="da-encabezado">
        <p>
          Histórico y comparación entre distritos. Para el estado actual, ve al{" "}
          <a href="/dashboard-ambiental">Dashboard</a>.
        </p>
        <div className="da-encabezado-acciones">
          <span className="pill p-neutral" title={`Consultado ${fechaHoraLima(generadoEn)}`}>
            <span className="dot" style={{ background: "var(--good)" }} />
            Agregados al {fechaCorta(ultimoDato)}
          </span>
          <Segmentado opciones={OPCIONES_DIAS} valor={dias} onCambiar={setDias} etiquetaAria="Periodo" />
        </div>
      </div>

      <DistrictComparison distritos={distritos} seleccion={seleccion} onCambiarSeleccion={setSeleccion} dias={dias} />

      <div className="data-analytics-grid">
        <EcaRanking distritos={distritos} dias={dias} />
        <HourlyPattern distritos={distritos} distritoInicial={seleccion[0]} dias={dias} />
      </div>

      <WeeklyAiSummary distritos={seleccionados} />
    </div>
  );
}
