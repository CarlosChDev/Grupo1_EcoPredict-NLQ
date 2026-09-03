import { useCallback, useState } from "react";
import { NlqApiError, preguntarNlq } from "../services/nlqApi";
import type { ChatMessage } from "../types/nlq.types";

export type EstadoEnvio = "idle" | "cargando" | "ok" | "error";

/**
 * crypto.randomUUID() solo existe en contexto seguro (HTTPS o localhost).
 * En producción por HTTP plano (ej. IP pública sin TLS) no está disponible
 * y lanza TypeError, tumbando el envío del chat sin que se vea nada.
 */
function generarId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

export function useNlqChat() {
  const [mensajes, setMensajes] = useState<ChatMessage[]>([]);
  const [estado, setEstado] = useState<EstadoEnvio>("idle");
  const [errorRed, setErrorRed] = useState("");

  const enviarPregunta = useCallback(async (pregunta: string) => {
    const texto = pregunta.trim();
    if (!texto) return;

    const mensajeUsuario: ChatMessage = {
      id: generarId(),
      role: "usuario",
      texto,
      timestamp: new Date(),
    };
    setMensajes((prev) => [...prev, mensajeUsuario]);
    setEstado("cargando");
    setErrorRed("");

    try {
      const respuesta = await preguntarNlq({ pregunta: texto });

      const mensajeAsistente: ChatMessage = {
        id: generarId(),
        role: "asistente",
        texto: "texto" in respuesta ? respuesta.texto : "",
        timestamp: new Date(),
        respuesta,
      };
      setMensajes((prev) => [...prev, mensajeAsistente]);
      setEstado(respuesta.ok ? "ok" : "error");
    } catch (err) {
      setEstado("error");
      setErrorRed(err instanceof NlqApiError ? err.message : "Error inesperado.");
    }
  }, []);

  return { mensajes, estado, errorRed, enviarPregunta };
}
