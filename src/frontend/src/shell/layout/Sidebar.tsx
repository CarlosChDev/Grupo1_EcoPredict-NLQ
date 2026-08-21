import { NavLink } from "react-router-dom";
import { microfrontends } from "../config/microfrontends";
import "./Sidebar.css";

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="logo">
        <div className="logo-icon">🌿</div>
        <div className="logo-text">
          <strong>EcoPredict</strong>
          <span>NLQ</span>
        </div>
      </div>

      <div className="section-title">NAVEGACIÓN</div>

      <NavLink to="/" end className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}>
        <span className="icon">🏠</span>
        <span>Inicio</span>
      </NavLink>

      {microfrontends.map((mf) =>
        mf.estado === "disponible" ? (
          <NavLink
            key={mf.id}
            to={mf.ruta}
            className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}
          >
            <span className="icon">{mf.icono}</span>
            <span>{mf.nombre}</span>
          </NavLink>
        ) : (
          <div key={mf.id} className="nav-item disabled">
            <span className="icon">{mf.icono}</span>
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
