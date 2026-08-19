import type { EstacionResumen } from "../types/dashboard.types";
import { NIVEL_COLOR_VAR, NIVEL_LABEL, peorNivel } from "../utils/nivel";
import "./AirQualityCard.css";

interface AirQualityCardProps {
  estaciones: EstacionResumen[];
}

const ICONO_POR_NIVEL = { bueno: "🙂", moderado: "😐", malo: "😷" } as const;

/** Hero: resume el peor nivel de contaminación entre todas las estaciones. */
export function AirQualityCard({ estaciones }: AirQualityCardProps) {
  const niveles = estaciones.flatMap((e) => e.mediciones.map((m) => m.nivel));
  const nivel = peorNivel(niveles);
  const color = NIVEL_COLOR_VAR[nivel];

  return (
    <div className="card card-gradient air-quality-card">
      <div className="card-label">
        <span className="small-icon">📡</span>
        ESTADO GENERAL DEL AIRE
      </div>

      <div className="aq-ring" style={{ borderColor: color, boxShadow: `0 0 16px ${color}33` }}>
        <span className="aq-ring-icon">{ICONO_POR_NIVEL[nivel]}</span>
      </div>

      <div className="aq-status" style={{ color, borderColor: color }}>
        {NIVEL_LABEL[nivel]}
      </div>

      <div className="aq-summary">
        <p>Estaciones monitoreadas</p>
        <strong>{estaciones.length}</strong>
      </div>
    </div>
  );
}
