import type { HistorialEntry } from "../types/status.types";
import { ESTADO_COLOR_VAR, ESTADO_LABEL, ESTADO_PILL_CLASS, TIPO_LABEL } from "../utils/estado";
import "./HistoryPanel.css";

interface HistoryPanelProps {
  historial: HistorialEntry[];
}

export function HistoryPanel({ historial }: HistoryPanelProps) {
  return (
    <div className="card history-panel">
      <div className="card-label">
        <span className="small-icon">📜</span>
        Historial de verificaciones
      </div>

      {historial.length === 0 ? (
        <p className="history-empty">Todavía no hay verificaciones registradas.</p>
      ) : (
        <div className="history-timeline">
          {historial.map((h) => (
            <div key={h.id} className="history-row">
              <div className="history-time">
                {h.timestamp?.toLocaleTimeString("es-PE", {
                  hour: "2-digit",
                  minute: "2-digit",
                  second: "2-digit",
                }) ?? "—"}
              </div>
              <span className="dot" style={{ background: ESTADO_COLOR_VAR[h.estado] }} />
              <div className="history-detail">
                <span className={`pill ${ESTADO_PILL_CLASS[h.estado]}`}>{ESTADO_LABEL[h.estado]}</span>
                <span className="history-tag">{h.entorno === "local" ? "Local" : "Producción"}</span>
                <span className="history-tag">{TIPO_LABEL[h.tipo]}</span>
                <span className="history-tag">{h.latenciaMs ?? "—"} ms</span>
                <span className="history-tag">HTTP {h.codigoHttp ?? "—"}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
