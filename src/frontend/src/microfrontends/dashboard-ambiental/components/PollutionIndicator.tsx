import type { EstacionResumen } from "../types/dashboard.types";
import { NIVEL_COLOR_VAR } from "../utils/nivel";
import "./PollutionIndicator.css";

interface PollutionIndicatorProps {
  estaciones: EstacionResumen[];
}

/** Grilla de estaciones con un chip por parámetro medido y su nivel. */
export function PollutionIndicator({ estaciones }: PollutionIndicatorProps) {
  return (
    <div className="card pollution-indicator">
      <div className="section-heading">
        <span className="heading-icon">🧪</span>
        <strong>Niveles de contaminación por estación</strong>
      </div>

      <div className="pollution-grid">
        {estaciones.map((estacion) => (
          <div key={estacion.id} className="pollution-station">
            <div className="pollution-station-header">
              <strong>{estacion.nombre}</strong>
              {estacion.zona && <span>{estacion.zona}</span>}
            </div>

            <div className="pollution-chips">
              {estacion.mediciones.map((m) => (
                <div
                  key={m.parametro}
                  className="pollution-chip"
                  style={{ borderColor: NIVEL_COLOR_VAR[m.nivel] }}
                >
                  <span className="pollution-chip-param">{m.parametro.toUpperCase()}</span>
                  <span className="pollution-chip-valor" style={{ color: NIVEL_COLOR_VAR[m.nivel] }}>
                    {m.valor} {m.unidad}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
