import type { EstacionResumen } from "../types/dashboard.types";
import { nivelPorEca } from "../utils/eca";
import { NIVEL_COLOR_VAR } from "../utils/nivel";
import "./StationRanking.css";

interface StationRankingProps {
  estaciones: EstacionResumen[];
}

/** Ranking de estaciones por PM2.5 (el parámetro más citado en el ECA-Aire). */
export function StationRanking({ estaciones }: StationRankingProps) {
  const conPm25 = estaciones
    .map((estacion) => ({
      estacion,
      pm25: estacion.mediciones.find((m) => m.parametro === "pm25"),
    }))
    .filter((e): e is { estacion: EstacionResumen; pm25: NonNullable<typeof e.pm25> } => Boolean(e.pm25))
    .sort((a, b) => b.pm25.valor - a.pm25.valor);

  const maxValor = Math.max(1, ...conPm25.map((e) => e.pm25.valor));
  const medidoMasReciente = Math.max(...conPm25.map((e) => new Date(e.pm25.medidoEn).getTime()));

  return (
    <div className="card station-ranking-card">
      <div className="section-heading">Estaciones por PM2.5</div>

      <div className="station-ranking-list">
        {conPm25.map(({ estacion, pm25 }) => {
          const nivel = nivelPorEca("pm25", pm25.valor);
          const color = NIVEL_COLOR_VAR[nivel];
          const esAntiguo = medidoMasReciente - new Date(pm25.medidoEn).getTime() > 60 * 60 * 1000;

          return (
            <div key={estacion.id} className="station-ranking-item">
              <div className="station-ranking-head">
                <span className="station-ranking-nombre">{estacion.nombre}</span>
                {esAntiguo && (
                  <span className="badge badge-muted">
                    último dato{" "}
                    {new Date(pm25.medidoEn).toLocaleTimeString("es-PE", {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                )}
                <span className="station-ranking-valor" style={{ color }}>
                  {pm25.valor}
                </span>
              </div>
              <div className="bar-track">
                <div
                  className="bar-fill"
                  style={{ width: `${Math.round((pm25.valor / maxValor) * 100)}%`, background: color }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
