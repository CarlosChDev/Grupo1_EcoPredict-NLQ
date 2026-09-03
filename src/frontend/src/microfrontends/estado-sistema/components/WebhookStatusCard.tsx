import type { WebhookCheckResult } from "../types/status.types";
import { ESTADO_COLOR_VAR, ESTADO_LABEL } from "../utils/estado";
import "./WebhookStatusCard.css";

interface WebhookStatusCardProps {
  resultado: WebhookCheckResult | null;
  verificando: boolean;
  onProbar: () => void;
}

export function WebhookStatusCard({ resultado, verificando, onProbar }: WebhookStatusCardProps) {
  const estado = verificando ? "verificando" : resultado?.estado ?? "desconocido";
  const color = ESTADO_COLOR_VAR[estado];

  return (
    <div className="card webhook-status-card">
      <div className="webhook-status-header">
        <div className="card-label">
          <span className="small-icon">⚡</span>
          WEBHOOK FLUJO B
        </div>
        <span className="estado-pill" style={{ color, borderColor: color, background: `${color}1a` }}>
          <span className="estado-dot" style={{ background: color }} />
          {ESTADO_LABEL[estado]}
        </span>
      </div>

      <div className="webhook-metrics-grid">
        <div className="metric">
          <p>LATENCIA</p>
          <strong>
            {resultado?.latenciaMs ?? "—"} <span className="unit">ms</span>
          </strong>
        </div>
        <div className="metric">
          <p>ÚLTIMA RESPUESTA</p>
          <strong>{resultado?.codigoHttp ?? "—"}</strong>
        </div>
        <div className="metric">
          <p>X-API-KEY</p>
          <strong>{resultado ? (resultado.apiKeyEnviada ? "✔ presente" : "no configurada") : "—"}</strong>
        </div>
        <div className="metric">
          <p>RATE LIMIT RESTANTE</p>
          <strong>{resultado?.rateLimitRestante ?? "No expuesto"}</strong>
        </div>
      </div>

      {resultado?.mensajeError && <p className="webhook-error-msg">{resultado.mensajeError}</p>}

      <button className="btn-primary" type="button" onClick={onProbar} disabled={verificando}>
        {verificando ? "Probando…" : "Probar conexión ahora"}
      </button>
    </div>
  );
}
