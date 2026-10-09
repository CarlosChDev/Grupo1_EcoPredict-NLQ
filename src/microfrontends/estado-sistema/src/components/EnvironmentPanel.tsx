import { urlDeEntorno } from "../services/statusApi";
import type { Entorno } from "../types/status.types";
import "./EnvironmentPanel.css";

interface EnvironmentPanelProps {
  entorno: Entorno;
  onCambiarEntorno: (entorno: Entorno) => void;
}

export function EnvironmentPanel({ entorno, onCambiarEntorno }: EnvironmentPanelProps) {
  const urlProd = urlDeEntorno("produccion");
  const urlActual = urlDeEntorno(entorno) ?? "";
  const esHttps = urlActual.startsWith("https://");

  return (
    <div className="card environment-panel">
      <div className="card-label">
        <span className="small-icon">🌐</span>
        ENTORNO
      </div>

      <div className="env-toggle">
        <button
          className={`env-toggle-btn${entorno === "local" ? " active" : ""}`}
          type="button"
          onClick={() => onCambiarEntorno("local")}
        >
          Local
        </button>
        <button
          className={`env-toggle-btn${entorno === "produccion" ? " active" : ""}`}
          type="button"
          onClick={() => onCambiarEntorno("produccion")}
          disabled={!urlProd}
          title={urlProd ? undefined : "Falta VITE_N8N_WEBHOOK_URL_PROD en el .env"}
        >
          Producción
        </button>
      </div>

      <div className="env-url">{urlActual || "Sin definir — revisa .env"}</div>

      <div className="env-badges">
        <span className="badge badge-teal">{entorno === "local" ? "Local" : "Oracle Cloud"}</span>
        <span className="badge badge-teal">{esHttps ? "HTTPS" : "HTTP"}</span>
      </div>
    </div>
  );
}
