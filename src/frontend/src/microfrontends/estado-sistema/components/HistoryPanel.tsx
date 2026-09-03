import type { HistorialEntry } from "../types/status.types";
import { ESTADO_COLOR_VAR, ESTADO_LABEL, TIPO_LABEL } from "../utils/estado";
import "./HistoryPanel.css";

interface HistoryPanelProps {
  historial: HistorialEntry[];
}

export function HistoryPanel({ historial }: HistoryPanelProps) {
  return (
    <div className="card history-panel">
      <div className="card-label">
        <span className="small-icon">📜</span>
        HISTORIAL DE VERIFICACIONES
      </div>

      {historial.length === 0 ? (
        <p className="history-empty">Todavía no hay verificaciones registradas.</p>
      ) : (
        <div className="history-table-wrap">
          <table className="history-table">
            <thead>
              <tr>
                <th>Hora</th>
                <th>Entorno</th>
                <th>Estado</th>
                <th>Tipo</th>
                <th>Latencia</th>
                <th>HTTP</th>
              </tr>
            </thead>
            <tbody>
              {historial.map((h) => {
                const color = ESTADO_COLOR_VAR[h.estado];
                return (
                  <tr key={h.id}>
                    <td>
                      {h.timestamp?.toLocaleTimeString("es-PE", {
                        hour: "2-digit",
                        minute: "2-digit",
                        second: "2-digit",
                      }) ?? "—"}
                    </td>
                    <td className="history-tipo">{h.entorno === "local" ? "Local" : "Producción"}</td>
                    <td>
                      <span className="history-estado" style={{ color }}>
                        <span className="history-dot" style={{ background: color }} />
                        {ESTADO_LABEL[h.estado]}
                      </span>
                    </td>
                    <td className="history-tipo">{TIPO_LABEL[h.tipo]}</td>
                    <td>{h.latenciaMs ?? "—"} ms</td>
                    <td>{h.codigoHttp ?? "—"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
