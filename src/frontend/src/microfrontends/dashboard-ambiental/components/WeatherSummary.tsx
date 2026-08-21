import type { ClimaResumen } from "../types/dashboard.types";
import "./WeatherSummary.css";

const ICONO_POR_CONDICION: Record<string, string> = {
  Nublado: "☁️",
  Soleado: "☀️",
  Lluvioso: "🌧️",
};

interface WeatherSummaryProps {
  clima: ClimaResumen;
}

/**
 * Aún no hay flujo n8n que ingiera SENAMHI (ver types/dashboard.types.ts),
 * así que esta tarjeta muestra datos simulados hasta que exista esa fuente.
 */
export function WeatherSummary({ clima }: WeatherSummaryProps) {
  return (
    <div className="card weather-summary">
      <div className="section-heading">
        <span className="heading-icon">🌤️</span>
        <strong>Información meteorológica</strong>
        <span className="badge badge-muted weather-mock-badge">Simulado</span>
      </div>

      <div className="weather-main">
        <span className="weather-icon">{ICONO_POR_CONDICION[clima.condicion] ?? "🌡️"}</span>
        <div>
          <strong className="weather-temp">{clima.temperaturaC}°C</strong>
          <span className="weather-condicion">{clima.condicion}</span>
        </div>
      </div>

      <div className="weather-grid">
        <div className="weather-item">
          <span>Humedad</span>
          <strong>{clima.humedadPct}%</strong>
        </div>
        <div className="weather-item">
          <span>Viento</span>
          <strong>{clima.vientoKmh} km/h</strong>
        </div>
      </div>
    </div>
  );
}
