import { usePageHeader } from "../../shell/layout/usePageHeader";
import { IncaIndexCard } from "./components/IncaIndexCard";
import { PmTrendChart } from "./components/PmTrendChart";
import { PollutantsGrid } from "./components/PollutantsGrid";
import { StationRanking } from "./components/StationRanking";
import { ESTACIONES_MOCK, SERIE_PM_MOCK } from "./data/mockDashboardData";
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
    titulo: "Panel de calidad del aire",
    subtitulo: "Lima Metropolitana · datos horarios",
  });

  const estacionReferencia = ESTACIONES_MOCK[0];

  return (
    <div className="dashboard-page">
      <div className="dashboard-mock-banner">
        Vista de maqueta — datos de ejemplo. Falta conectar el webhook de lectura en n8n.
      </div>

      <div className="dashboard-top-grid">
        <IncaIndexCard estacion={estacionReferencia} />
        <PollutantsGrid estacion={estacionReferencia} />
      </div>

      <div className="dashboard-bottom-grid">
        <PmTrendChart serie={SERIE_PM_MOCK} />
        <StationRanking estaciones={ESTACIONES_MOCK} />
      </div>
    </div>
  );
}
