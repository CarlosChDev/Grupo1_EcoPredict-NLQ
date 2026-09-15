import type { EstacionResumen } from "../types/dashboard.types";
import { ECA_LIMITE, nivelPorIndice, porcentajeEca } from "../utils/eca";
import { NIVEL_COLOR_VAR, NIVEL_LABEL, NIVEL_PILL_CLASS } from "../utils/nivel";
import "./IncaIndexCard.css";

const PARAMETRO_LABEL: Record<string, string> = {
  pm25: "PM2.5",
  pm10: "PM10",
  no2: "NO2",
  so2: "SO2",
  o3: "O3",
  co: "CO",
};

interface IncaIndexCardProps {
  estacion: EstacionResumen;
}

/**
 * Índice INCA de la estación de referencia: toma el % del ECA-Aire más alto
 * entre sus contaminantes medidos (el contaminante que domina es el que fija
 * el índice general, como en los índices de calidad del aire estándar).
 */
export function IncaIndexCard({ estacion }: IncaIndexCardProps) {
  const conPorcentaje = estacion.mediciones.map((m) => ({
    ...m,
    pct: porcentajeEca(m.parametro, m.valor),
  }));
  const dominante = conPorcentaje.reduce(
    (peor, actual) => (actual.pct > peor.pct ? actual : peor),
    conPorcentaje[0],
  );
  const indice = dominante?.pct ?? 0;
  const nivel = nivelPorIndice(indice);
  const color = NIVEL_COLOR_VAR[nivel];

  const radio = 46;
  const circunferencia = 2 * Math.PI * radio;
  const avance = Math.min(indice, 500) / 500;
  const posicionGauge = `${Math.min(indice, 500) / 5}%`;

  const actualizado = new Date(estacion.mediciones[0]?.medidoEn ?? Date.now()).toLocaleTimeString("es-PE", {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className="card inca-card">
      <div className="card-label">
        <span className="small-icon">📡</span>
        Índice INCA · {estacion.nombre}
      </div>

      <div className="inca-main">
        <div className="inca-numero">
          <strong className="inca-valor" style={{ color }}>
            {indice}
          </strong>
          <div className="inca-nivel">
            <span className={`pill ${NIVEL_PILL_CLASS[nivel]}`}>{NIVEL_LABEL[nivel]}</span>
            <span className="inca-actualizado">actualizado {actualizado}</span>
          </div>
        </div>

        <svg className="inca-ring" width="100" height="100" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r={radio} className="inca-ring-track" />
          <circle
            cx="50"
            cy="50"
            r={radio}
            className="inca-ring-fill"
            stroke={color}
            strokeDasharray={circunferencia}
            strokeDashoffset={circunferencia * (1 - avance)}
          />
          <text x="50" y="46" className="inca-ring-label">
            INCA
          </text>
          <text x="50" y="63" className="inca-ring-valor" fill={color}>
            {indice}
          </text>
        </svg>
      </div>

      <div className="inca-gauge">
        <div className="inca-gauge-track">
          <span className="inca-gauge-marker" style={{ left: posicionGauge }} />
        </div>
        <div className="inca-gauge-scale">
          <span>0</span>
          <span>50</span>
          <span>100</span>
          <span>500</span>
        </div>
      </div>

      {dominante && (
        <p className="inca-mensaje">
          {nivel === "malo" &&
            "Grupos sensibles deben evitar actividad física prolongada al aire libre. "}
          {PARAMETRO_LABEL[dominante.parametro]}{" "}
          {dominante.pct > 100
            ? `supera el ECA-Aire nacional de ${ECA_LIMITE[dominante.parametro]} ${dominante.unidad}.`
            : `se acerca al ECA-Aire nacional de ${ECA_LIMITE[dominante.parametro]} ${dominante.unidad}.`}
        </p>
      )}
    </div>
  );
}
