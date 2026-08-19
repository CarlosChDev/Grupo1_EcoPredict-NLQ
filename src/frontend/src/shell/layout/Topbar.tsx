import { useEffect, useState } from "react";
import "./Topbar.css";

interface TopbarProps {
  titulo: string;
  subtitulo: string;
}

export function Topbar({ titulo, subtitulo }: TopbarProps) {
  const [ahora, setAhora] = useState(new Date());

  useEffect(() => {
    const id = setInterval(() => setAhora(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <header className="topbar">
      <div className="title">
        <h1>{titulo}</h1>
        <p>{subtitulo}</p>
      </div>

      <div className="top-actions">
        <div className="time">
          <strong>
            {ahora.toLocaleTimeString("es-PE", { hour: "2-digit", minute: "2-digit" })}
          </strong>
          <span>
            {ahora.toLocaleDateString("es-PE", {
              weekday: "long",
              day: "numeric",
              month: "long",
            })}
          </span>
        </div>

        <div className="avatar">EP</div>
      </div>
    </header>
  );
}
