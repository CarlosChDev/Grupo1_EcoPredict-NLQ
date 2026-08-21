import type { Alerta } from "../types/dashboard.types";
import { NIVEL_COLOR_VAR, NIVEL_LABEL } from "../utils/nivel";
import "./AlertsPanel.css";

interface AlertsPanelProps {
  alertas: Alerta[];
}

export function AlertsPanel({ alertas }: AlertsPanelProps) {
  return (
    <div className="card alerts-panel">
      <div className="section-heading">
        <span className="heading-icon">🚨</span>
        <strong>Alertas ambientales</strong>
      </div>

      {alertas.length === 0 ? (
        <p className="alerts-empty">Sin alertas activas.</p>
      ) : (
        <div className="alerts-list">
          {alertas.map((alerta) => (
            <div
              key={alerta.id}
              className="alert-item"
              style={{ borderColor: NIVEL_COLOR_VAR[alerta.nivel] }}
            >
              <span className="alert-nivel" style={{ color: NIVEL_COLOR_VAR[alerta.nivel] }}>
                {NIVEL_LABEL[alerta.nivel]}
              </span>
              <p>{alerta.mensaje}</p>
              <span className="alert-meta">
                {alerta.parametro.toUpperCase()} · {alerta.estacion}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
