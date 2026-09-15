import type { EstacionResumen, ParametroCalidadAire } from "../types/dashboard.types";
import { nivelPorEca, porcentajeEca } from "../utils/eca";
import { NIVEL_COLOR_VAR } from "../utils/nivel";
import "./PollutantsGrid.css";

const PARAMETRO_LABEL: Record<ParametroCalidadAire, string> = {
  pm25: "PM2.5",
  pm10: "PM10",
  o3: "O3",
  no2: "NO2",
  so2: "SO2",
  co: "CO",
};

const ORDEN: ParametroCalidadAire[] = ["pm25", "pm10", "o3", "no2", "so2", "co"];

interface PollutantsGridProps {
  estacion: EstacionResumen;
}

/** Grilla de las 6 lecturas en tiempo real de la estación de referencia (ver IncaIndexCard). */
export function PollutantsGrid({ estacion }: PollutantsGridProps) {
  const porParametro = new Map(estacion.mediciones.map((m) => [m.parametro, m]));

  return (
    <div className="card pollutants-grid-card">
      <div className="card-label">
        <span className="small-icon">🧪</span>
        Contaminantes en tiempo real
        <span className="pollutants-grid-nota">promedio móvil 1 h · µg/m³</span>
      </div>

      <div className="pollutants-grid">
        {ORDEN.map((parametro) => {
          const medicion = porParametro.get(parametro);
          if (!medicion) return null;

          const nivel = nivelPorEca(parametro, medicion.valor);
          const pct = porcentajeEca(parametro, medicion.valor);
          const color = NIVEL_COLOR_VAR[nivel];

          const delta =
            medicion.valorAnterior !== undefined && medicion.valorAnterior !== 0
              ? Math.round(((medicion.valor - medicion.valorAnterior) / medicion.valorAnterior) * 100)
              : null;

          return (
            <div key={parametro} className="pollutant-tile">
              <div className="pollutant-tile-head">
                <span className="dot" style={{ background: color }} />
                {PARAMETRO_LABEL[parametro]}
              </div>

              <div className="pollutant-tile-valor">
                <span className="tile-num">{medicion.valor}</span>
                <span className="unit">{medicion.unidad}</span>
              </div>

              <div className="pollutant-tile-meta">
                {delta !== null && (
                  <span className={`delta ${delta > 0 ? "up" : delta < 0 ? "down" : ""}`}>
                    {delta > 0 ? "▲" : delta < 0 ? "▼" : "—"} {Math.abs(delta)}%
                  </span>
                )}
                <span className="pollutant-tile-eca">{pct}% del ECA</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
