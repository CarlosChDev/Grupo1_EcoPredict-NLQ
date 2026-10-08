import type { ChatMessage } from "../types/nlq.types";
import { esError, tieneSerie } from "../types/nlq.types";
import { DynamicVisualization } from "./DynamicVisualization";
import "./ChatMessageItem.css";

interface ChatMessageItemProps {
  mensaje: ChatMessage;
}

export function ChatMessageItem({ mensaje }: ChatMessageItemProps) {
  if (mensaje.role === "usuario") {
    return (
      <div className="msg me">
        <div className="msg-av">TÚ</div>
        <div className="bubble">{mensaje.texto}</div>
      </div>
    );
  }

  const respuesta = mensaje.respuesta;

  return (
    <div className="msg ai">
      <div className="msg-av">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
          <path d="M12 3v3M12 18v3M3 12h3M18 12h3M6 6l2 2M16 16l2 2M6 18l2-2M16 8l2-2" />
          <circle cx="12" cy="12" r="3" />
        </svg>
      </div>
      <div className="bubble">
        {respuesta && esError(respuesta) && (
          <p className="chat-error">
            {respuesta.codigo_http === 400
              ? respuesta.errores.join(" ")
              : respuesta.motivo}
          </p>
        )}

        {respuesta && respuesta.ok && "mensaje" in respuesta && (
          <p>{respuesta.mensaje}</p>
        )}

        {respuesta && tieneSerie(respuesta) && (
          <>
            <p>{respuesta.texto}</p>
            <span className="chat-modelo">Modelo: {respuesta.modelo_usado}</span>
            <DynamicVisualization respuesta={respuesta} />
          </>
        )}

        {respuesta && respuesta.ok && !tieneSerie(respuesta) && !("mensaje" in respuesta) && (
          <div className="chat-respuesta-generica">
            <p>
              {"texto" in respuesta
                ? (respuesta as any).texto
                : `Consulta recibida con éxito: "${(respuesta as any).consulta?.pregunta || mensaje.texto}"`}
            </p>
            {(respuesta as any).consulta && (
              <div style={{ marginTop: "8px", fontSize: "0.85rem", opacity: 0.9 }}>
                <span>📍 Ciudad: <strong>{(respuesta as any).consulta.ciudad || "Lima"}</strong></span> &bull;{" "}
                <span>🧪 Parámetro: <strong>{((respuesta as any).consulta.parametro || "PM2.5").toUpperCase()}</strong></span>
              </div>
            )}
            {(respuesta as any).etapa && (
              <span className="chat-modelo" style={{ marginTop: "6px", display: "inline-block" }}>
                Estado: {(respuesta as any).etapa}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
