import type { AlertaSistema, SeveridadAlerta } from "../types/analytics.types";
import { haceTiempo } from "../utils/tiempo";
import "./AlertsPanel.css";

const COLOR_VAR: Record<SeveridadAlerta, string> = {
  info: "var(--good)",
  baja: "var(--good)",
  moderada: "var(--mod)",
  alta: "var(--bad)",
  critica: "var(--crit)",
};

interface AlertsPanelProps {
  alertas: AlertaSistema[];
}

/**
 * HU-03, tarea 5: panel de alertas con sus factores asociados, consumiendo
 * GET /alertas. `alerta.mensaje` ES la columna `analisis_llm` de
 * `alertas_anomalias` (ver services/dataAnalyticsApi.ts) — por eso ya
 * "reutiliza analisis_llm" sin necesitar un campo nuevo.
 */
export function AlertsPanel({ alertas }: AlertsPanelProps) {
  return (
    <div className="card alerts-panel-card">
      <div className="card-label">
        <span className="small-icon">⚠️</span>
        Alertas y factores asociados
      </div>

      {alertas.length === 0 ? (
        <p className="alerts-panel-vacio">Sin alertas activas.</p>
      ) : (
        <div className="alerts-panel-list">
          {alertas.map((alerta, i) => {
            const color = COLOR_VAR[alerta.severidad] ?? "var(--ink-3)";
            return (
              <div key={`${alerta.evento_en}-${i}`} className="alerts-panel-item">
                <div className="alerts-panel-head">
                  <span className="dot" style={{ background: color }} />
                  <span className="alerts-panel-titulo" style={{ color }}>
                    {alerta.titulo}
                  </span>
                  <span className={`pill alerts-panel-severidad-${alerta.severidad}`}>{alerta.severidad}</span>
                </div>
                <p className="alerts-panel-mensaje">{alerta.mensaje}</p>
                <span className="alerts-panel-tiempo">{haceTiempo(alerta.evento_en)}</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
