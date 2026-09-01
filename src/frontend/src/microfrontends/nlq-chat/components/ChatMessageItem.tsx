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
      <div className="chat-message usuario">
        <div className="chat-bubble">{mensaje.texto}</div>
      </div>
    );
  }

  const respuesta = mensaje.respuesta;

  return (
    <div className="chat-message asistente">
      <div className="chat-avatar">🤖</div>
      <div className="chat-bubble">
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
