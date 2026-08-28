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
      </div>
    </div>
  );
}
