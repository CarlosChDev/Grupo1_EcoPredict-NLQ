import { useCallback, useState } from "react";
import { NlqApiError, preguntarNlq } from "../services/nlqApi";
import type { ChatMessage } from "../types/nlq.types";

export type EstadoEnvio = "idle" | "cargando" | "ok" | "error";

export function useNlqChat() {
  const [mensajes, setMensajes] = useState<ChatMessage[]>([]);
  const [estado, setEstado] = useState<EstadoEnvio>("idle");
  const [errorRed, setErrorRed] = useState("");

  const enviarPregunta = useCallback(async (pregunta: string) => {
    const texto = pregunta.trim();
    if (!texto) return;

    const mensajeUsuario: ChatMessage = {
      id: crypto.randomUUID(),
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
        id: crypto.randomUUID(),
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
