import type { ReactNode } from "react";
import "./Panel.css";

interface PanelProps {
  numero: number;
  titulo: ReactNode;
  subtitulo: string;
  herramientas?: ReactNode;
  /** Endpoint que alimenta el bloque, p.ej. "GET /analitica/ranking-eca?...". */
  endpoint: string;
  fuente: string;
  children: ReactNode;
  className?: string;
}

/** Tarjeta numerada con cabecera, cuerpo y pie (endpoint + tabla fuente). */
export function Panel({ numero, titulo, subtitulo, herramientas, endpoint, fuente, children, className }: PanelProps) {
  return (
    <section className={`card da-panel ${className ?? ""}`}>
      <header className="da-panel-h">
        <h2>
          <span className="da-panel-num">{numero}</span>
          {titulo}
        </h2>
        {herramientas && <div className="da-panel-tools">{herramientas}</div>}
        <p className="da-panel-sub">{subtitulo}</p>
      </header>
      <div className="da-panel-b">{children}</div>
      <footer className="da-panel-f">
        <code>{endpoint}</code>
        <span>fuente: {fuente}</span>
      </footer>
    </section>
  );
}

interface SegmentadoProps<T extends string | number> {
  opciones: { valor: T; etiqueta: string }[];
  valor: T;
  onCambiar: (valor: T) => void;
  pequeno?: boolean;
  etiquetaAria: string;
}

export function Segmentado<T extends string | number>({
  opciones,
  valor,
  onCambiar,
  pequeno,
  etiquetaAria,
}: SegmentadoProps<T>) {
  return (
    <div className={`da-seg ${pequeno ? "da-seg-sm" : ""}`} role="group" aria-label={etiquetaAria}>
      {opciones.map((o) => (
        <button
          key={o.valor}
          type="button"
          className={o.valor === valor ? "on" : ""}
          aria-pressed={o.valor === valor}
          onClick={() => onCambiar(o.valor)}
        >
          {o.etiqueta}
        </button>
      ))}
    </div>
  );
}

export function Esqueleto({ alto, cantidad = 1 }: { alto: number; cantidad?: number }) {
  return (
    <div className="da-sk-lista" aria-hidden="true">
      {Array.from({ length: cantidad }, (_, i) => (
        <div key={i} className="da-sk" style={{ height: alto }} />
      ))}
    </div>
  );
}

export function PanelError({ titulo, mensaje, onReintentar }: { titulo: string; mensaje: string; onReintentar: () => void }) {
  return (
    <div className="da-err" role="alert">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
        <circle cx="12" cy="12" r="10" />
        <path d="M12 8v4M12 16h.01" />
      </svg>
      <div>
        <b>{titulo}</b>
        <p>{mensaje}</p>
        <button type="button" className="da-btn" onClick={onReintentar}>
          Reintentar
        </button>
      </div>
    </div>
  );
}
