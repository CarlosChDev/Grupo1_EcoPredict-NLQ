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
