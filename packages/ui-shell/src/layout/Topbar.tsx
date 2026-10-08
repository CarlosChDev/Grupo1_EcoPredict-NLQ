import { useEffect, useState } from "react";
import { useTheme } from "../theme/useTheme";
import "./Topbar.css";

interface TopbarProps {
  titulo: string;
  subtitulo: string;
}

const ICONOS_TEMA = {
  light: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
    </svg>
  ),
  dark: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5Z" />
    </svg>
  ),
  system: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <circle cx="12" cy="12" r="9" />
      <path d="M12 3a9 9 0 0 0 0 18Z" fill="currentColor" stroke="none" />
    </svg>
  ),
} as const;

const ETIQUETA_TEMA = { light: "Tema claro", dark: "Tema oscuro", system: "Tema del sistema" } as const;

export function Topbar({ titulo, subtitulo }: TopbarProps) {
  const [ahora, setAhora] = useState(new Date());
  const { mode, ciclar } = useTheme();

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

        <button
          type="button"
          className="ctrl-icon theme-toggle"
          onClick={ciclar}
          title={ETIQUETA_TEMA[mode]}
          aria-label={ETIQUETA_TEMA[mode]}
        >
          {ICONOS_TEMA[mode]}
        </button>

        <div className="avatar">EP</div>
      </div>
    </header>
  );
}
