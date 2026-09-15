import { usePageHeader } from "../../shell/layout/usePageHeader";
import { ChatInput } from "./components/ChatInput";
import { ChatMessageItem } from "./components/ChatMessageItem";
import { useNlqChat } from "./hooks/useNlqChat";
import "./NlqChatPage.css";

/**
 * Microfrontend: NLQ Chat IA.
 * Responsabilidad (ver informe §4.2.3): capturar la pregunta del usuario,
 * enviarla al webhook de n8n, mostrar la respuesta generada por IA y
 * graficar la serie histórica cuando la haya.
 */
export function NlqChatPage() {
  usePageHeader({
    titulo: "NLQ Chat IA",
    subtitulo: "Pregunta en español y n8n consulta la base de datos ambiental",
  });

  const { mensajes, estado, errorRed, enviarPregunta } = useNlqChat();

  return (
    <div className="nlq-chat-page">
      <div className="card nlq-chat-card">
        <div className="nlq-chat-head">
          <div className="nlq-chat-avatar">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
              <path d="M12 3v3M12 18v3M3 12h3M18 12h3M6 6l2 2M16 16l2 2M6 18l2-2M16 8l2-2" />
              <circle cx="12" cy="12" r="3" />
            </svg>
          </div>
          <div>
            <strong>Asistente EcoPredict</strong>
            <div className="nlq-chat-status">
              <span className="live-pulse" />
              conectado al flujo NLQ de n8n
            </div>
          </div>
        </div>

        <div className="chat-window">
          {mensajes.length === 0 && (
            <p className="chat-empty">Aún no se ha enviado ninguna consulta. Prueba con un ejemplo de abajo.</p>
          )}

          {mensajes.map((m) => (
            <ChatMessageItem key={m.id} mensaje={m} />
          ))}

          {estado === "cargando" && <p className="chat-loading">n8n está procesando la consulta…</p>}

          {estado === "error" && errorRed && <p className="chat-error-red">{errorRed}</p>}
        </div>

        <ChatInput deshabilitado={estado === "cargando"} onEnviar={enviarPregunta} />
      </div>
    </div>
  );
}
