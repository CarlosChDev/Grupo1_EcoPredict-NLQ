import {
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  Tooltip,
} from "chart.js";
import { Line } from "react-chartjs-2";
import type { PuntoSerieHoraria } from "../types/dashboard.types";
import { ECA_LIMITE } from "../utils/eca";
import "./PmTrendChart.css";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

interface PmTrendChartProps {
  serie: PuntoSerieHoraria[];
}

/** PM2.5 y PM10 de las últimas 24 horas, con el límite ECA-Aire de PM2.5 como referencia. */
export function PmTrendChart({ serie }: PmTrendChartProps) {
  const raiz = document.documentElement;
  const cssVar = (nombre: string) => getComputedStyle(raiz).getPropertyValue(nombre).trim();
  const colorTexto = cssVar("--ink-2");
  const colorGrid = cssVar("--grid");
  const colorPm25 = cssVar("--aqua");
  const colorPm10 = cssVar("--accent");
  const colorEca = cssVar("--crit");

  const etiquetas = serie.map((p) =>
    new Date(p.horaIso).toLocaleTimeString("es-PE", { hour: "2-digit", minute: "2-digit" }),
  );

  const data = {
    labels: etiquetas,
    datasets: [
      {
        label: "PM2.5",
        data: serie.map((p) => p.pm25),
        borderColor: colorPm25,
        backgroundColor: colorPm25,
        tension: 0.3,
        pointRadius: 0,
      },
      {
        label: "PM10",
        data: serie.map((p) => p.pm10),
        borderColor: colorPm10,
        backgroundColor: colorPm10,
        tension: 0.3,
        pointRadius: 0,
      },
      {
        label: "ECA-Aire PM2.5 (50)",
        data: serie.map(() => ECA_LIMITE.pm25),
        borderColor: colorEca,
        borderDash: [6, 4],
        pointRadius: 0,
        borderWidth: 1.5,
      },
    ],
  };

  return (
    <div className="card pm-trend-chart-card">
      <div className="card-label">
        <span className="small-icon">📈</span>
        PM2.5 y PM10 · últimas 24 horas
        <span className="pm-trend-nota">pasa el cursor por el gráfico</span>
      </div>

      <div className="pm-trend-chart">
        <Line
          data={data}
          options={{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { position: "top", align: "end", labels: { color: colorTexto, boxWidth: 10 } },
            },
            scales: {
              x: { ticks: { color: colorTexto, maxTicksLimit: 8 }, grid: { color: colorGrid } },
              y: { ticks: { color: colorTexto }, grid: { color: colorGrid } },
            },
          }}
        />
      </div>
    </div>
  );
}
