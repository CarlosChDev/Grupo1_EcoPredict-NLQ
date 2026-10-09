import type { AlertaSistema, SeveridadAlerta } from "../types/dashboard.types";
import { haceTiempo } from "../utils/tiempo";
import "./SystemAlerts.css";

const COLOR_VAR: Record<SeveridadAlerta, string> = {
  info: "var(--good)",
  baja: "var(--good)",
  moderada: "var(--mod)",
  alta: "var(--bad)",
  critica: "var(--crit)",
};

interface SystemAlertsProps {
  alertas: AlertaSistema[];
}

/** Alertas de la tabla `alertas_anomalias` (webhook GET /alertas de FLUJO C). */
export function SystemAlerts({ alertas }: SystemAlertsProps) {
  return (
    <div className="card system-alerts-card">
      <div className="card-label">
        <span className="small-icon">⚠️</span>
        Alertas del Sistema
      </div>

      {alertas.length === 0 ? (
        <p className="system-alerts-vacio">Sin alertas activas.</p>
      ) : (
        <div className="system-alerts-list">
          {alertas.map((alerta, i) => {
            const color = COLOR_VAR[alerta.severidad] ?? "var(--ink-3)";
            return (
              <div key={`${alerta.evento_en}-${i}`} className="system-alert-item">
                <div className="system-alert-head">
                  <span className="dot" style={{ background: color }} />
                  <span className="system-alert-titulo" style={{ color }}>
                    {alerta.titulo}
                  </span>
                </div>
                <p className="system-alert-mensaje">{alerta.mensaje}</p>
                <span className="system-alert-tiempo">{haceTiempo(alerta.evento_en)}</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
