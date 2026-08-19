import { usePageHeader } from "../../shell/layout/usePageHeader";
import { AirQualityCard } from "./components/AirQualityCard";
import { AlertsPanel } from "./components/AlertsPanel";
import { PollutionIndicator } from "./components/PollutionIndicator";
import { WeatherSummary } from "./components/WeatherSummary";
import { ALERTAS_MOCK, CLIMA_MOCK, ESTACIONES_MOCK } from "./data/mockDashboardData";
import "./DashboardAmbientalPage.css";

/**
 * Microfrontend: Dashboard Ambiental (ver informe §4.2.2).
 *
 * SOLO VISTA: todavía no existe un webhook n8n de lectura para
 * `estaciones`/`mediciones_aire` (FLUJO A únicamente inserta), así que
 * esta página consume datos de ejemplo (`data/mockDashboardData.ts`) en
 * vez de hacer fetch. El día que ese webhook exista, se reemplazan los
 * imports de `*_MOCK` por una llamada real siguiendo el mismo patrón de
 * `microfrontends/nlq-chat/services/nlqApi.ts`.
 */
export function DashboardAmbientalPage() {
  usePageHeader({
    titulo: "Dashboard Ambiental",
    subtitulo: "Estado actual de la calidad del aire y alertas",
  });

  return (
    <div className="dashboard-page">
      <div className="dashboard-mock-banner">
        Vista de maqueta — datos de ejemplo. Falta conectar el webhook de lectura en n8n.
      </div>

      <div className="dashboard-top-grid">
        <AirQualityCard estaciones={ESTACIONES_MOCK} />
        <WeatherSummary clima={CLIMA_MOCK} />
        <AlertsPanel alertas={ALERTAS_MOCK} />
      </div>

      <PollutionIndicator estaciones={ESTACIONES_MOCK} />
    </div>
  );
}
