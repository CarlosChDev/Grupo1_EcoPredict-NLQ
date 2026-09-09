import { NavLink } from "react-router-dom";
import { microfrontends } from "../config/microfrontends";
import "./Sidebar.css";

const ICONO_INICIO = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 11.5 12 4l9 7.5" />
    <path d="M5 10v9.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V10" />
  </svg>
);

const ICONO_PANEL = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <rect x="3" y="3" width="7" height="9" rx="1.5" />
    <rect x="14" y="3" width="7" height="5" rx="1.5" />
    <rect x="14" y="12" width="7" height="9" rx="1.5" />
    <rect x="3" y="16" width="7" height="5" rx="1.5" />
  </svg>
);

const ICONOS_POR_ID: Record<string, JSX.Element> = {
  "nlq-chat": (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 12a8 8 0 0 1-8 8H4l2-3a8 8 0 1 1 15-5Z" />
      <circle cx="9.5" cy="12" r=".8" fill="currentColor" />
      <circle cx="13" cy="12" r=".8" fill="currentColor" />
      <circle cx="16.5" cy="12" r=".8" fill="currentColor" />
    </svg>
  ),
  "dashboard-ambiental": ICONO_PANEL,
  "data-analytics": (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 3v16a2 2 0 0 0 2 2h16" />
      <path d="M7 15l3.5-4.5 3 3L20 6" />
    </svg>
  ),
  "estado-sistema": (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="4" width="18" height="7" rx="2" />
      <rect x="3" y="14" width="18" height="6" rx="2" />
      <path d="M7 7.5h.01M7 17h.01" />
    </svg>
  ),
  ajustes: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.7 1.7 0 0 0 .34 1.87l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.7 1.7 0 0 0-1.87-.34 1.7 1.7 0 0 0-1.04 1.56V21a2 2 0 1 1-4 0v-.09A1.7 1.7 0 0 0 9 19.35a1.7 1.7 0 0 0-1.87.34l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.7 1.7 0 0 0 4.65 15a1.7 1.7 0 0 0-1.56-1.04H3a2 2 0 1 1 0-4h.09A1.7 1.7 0 0 0 4.65 9a1.7 1.7 0 0 0-.34-1.87l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.7 1.7 0 0 0 9 4.65a1.7 1.7 0 0 0 1.04-1.56V3a2 2 0 1 1 4 0v.09a1.7 1.7 0 0 0 1.04 1.56 1.7 1.7 0 0 0 1.87-.34l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.7 1.7 0 0 0 19.35 9a1.7 1.7 0 0 0 1.56 1.04H21a2 2 0 1 1 0 4h-.09a1.7 1.7 0 0 0-1.56 1.04Z" />
    </svg>
  ),
};

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="logo">
        <div className="logo-icon">
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.1" strokeLinecap="round">
            <path d="M3 8h11a3 3 0 1 0-3-3" />
            <path d="M3 16h14a3 3 0 1 1-3 3" />
            <path d="M3 12h18" />
          </svg>
        </div>
        <div className="logo-text">
          <strong>EcoPredict</strong>
          <span>NLQ</span>
        </div>
      </div>

      <div className="section-title">NAVEGACIÓN</div>

      <NavLink to="/" end className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}>
        <span className="icon">{ICONO_INICIO}</span>
        <span>Inicio</span>
      </NavLink>

      {microfrontends.map((mf) =>
        mf.estado === "disponible" ? (
          <NavLink
            key={mf.id}
            to={mf.ruta}
            className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}
          >
            <span className="icon">{ICONOS_POR_ID[mf.id] ?? mf.icono}</span>
            <span>{mf.nombre}</span>
          </NavLink>
        ) : (
          <div key={mf.id} className="nav-item disabled">
            <span className="icon">{ICONOS_POR_ID[mf.id] ?? mf.icono}</span>
            <span>{mf.nombre}</span>
            <span className="soon-badge">Pronto</span>
          </div>
        ),
      )}

      <div className="stream">
        <div className="stream-title">
          <span className="live-pulse"></span>
          n8n WEBHOOK
        </div>
        <p>{import.meta.env.VITE_N8N_WEBHOOK_URL || "Sin definir — revisa .env"}</p>
        <div className="stream-badges">
          <span className="badge badge-teal">n8n</span>
          <span className="badge badge-teal">Postgres</span>
        </div>
      </div>

      <div className="version">Shell/Host · React + Vite</div>
    </aside>
  );
}
