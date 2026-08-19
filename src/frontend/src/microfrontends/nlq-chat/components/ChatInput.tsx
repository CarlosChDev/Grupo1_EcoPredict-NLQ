import { FormEvent, useState } from "react";
import "./ChatInput.css";

const EJEMPLOS = [
  "¿Cómo estuvo el PM2.5 esta semana?",
  "¿Cual fue el nivel de monoxido de carbono esta semana?",
  "Muéstrame el ozono del último mes",
];

interface ChatInputProps {
  deshabilitado: boolean;
  onEnviar: (pregunta: string) => void;
}

export function ChatInput({ deshabilitado, onEnviar }: ChatInputProps) {
  const [pregunta, setPregunta] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!pregunta.trim() || deshabilitado) return;
    onEnviar(pregunta);
    setPregunta("");
  }

  return (
    <form onSubmit={handleSubmit} className="chat-input-form">
      <div className="chips">
        {EJEMPLOS.map((ejemplo) => (
          <button
            key={ejemplo}
            type="button"
            className="chip"
            onClick={() => setPregunta(ejemplo)}
            disabled={deshabilitado}
          >
            {ejemplo}
          </button>
        ))}
      </div>

      <div className="chat-input-row">
        <textarea
          value={pregunta}
          onChange={(e) => setPregunta(e.target.value)}
          placeholder="Pregunta sobre calidad del aire en lenguaje natural…"
          rows={2}
          required
          disabled={deshabilitado}
        />
        <button type="submit" className="btn-primary" disabled={deshabilitado}>
          {deshabilitado ? "Enviando…" : "Enviar"}
        </button>
      </div>
    </form>
  );
}
