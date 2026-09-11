import type { WebhookCheckResult } from "../types/status.types";
import { ESTADO_COLOR_VAR, ESTADO_LABEL, ESTADO_PILL_CLASS } from "../utils/estado";
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
          Webhook Flujo B
        </div>
        <span className={`pill ${ESTADO_PILL_CLASS[estado]}`}>
          <span className="dot" style={{ background: color }} />
          {ESTADO_LABEL[estado]}
        </span>
      </div>

      <div className="webhook-metrics-grid">
        <div className="metric">
          <span className="eyebrow">Latencia</span>
          <strong className="tile-num">
            {resultado?.latenciaMs ?? "—"} <span className="unit">ms</span>
          </strong>
        </div>
        <div className="metric">
          <span className="eyebrow">Última respuesta</span>
          <strong className="tile-num">{resultado?.codigoHttp ?? "—"}</strong>
        </div>
        <div className="metric">
          <span className="eyebrow">X-API-Key</span>
          <strong className="metric-text">{resultado ? (resultado.apiKeyEnviada ? "✔ presente" : "no configurada") : "—"}</strong>
        </div>
        <div className="metric">
          <span className="eyebrow">Rate limit restante</span>
          <strong className="metric-text">{resultado?.rateLimitRestante ?? "No expuesto"}</strong>
        </div>
      </div>

      {resultado?.mensajeError && <p className="webhook-error-msg">{resultado.mensajeError}</p>}

      <button className="btn-primary" type="button" onClick={onProbar} disabled={verificando}>
        {verificando ? "Probando…" : "Probar conexión ahora"}
      </button>
    </div>
  );
}
