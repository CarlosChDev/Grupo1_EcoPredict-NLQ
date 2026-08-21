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
import type { NlqRespuestaConDatos } from "../types/nlq.types";
import "./DynamicVisualization.css";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

interface DynamicVisualizationProps {
  respuesta: NlqRespuestaConDatos;
}

/**
 * Grafica la `serie` que devuelve el nodo "Armar payload (texto + grafico)"
 * de FLUJO B: puntos {x: fecha, y: valor, estacion}. Si hay varias
 * estaciones en la serie, cada una se dibuja como su propio dataset.
 */
export function DynamicVisualization({ respuesta }: DynamicVisualizationProps) {
  const { serie, parametro, rango } = respuesta;

  const estaciones = Array.from(new Set(serie.map((p) => p.estacion)));
  const etiquetas = Array.from(new Set(serie.map((p) => p.x))).sort();

  const colores = ["#00d69d", "#00c9dd", "#ffc000", "#ff4d55", "#9860ed"];

  const data = {
    labels: etiquetas.map((iso) => new Date(iso).toLocaleDateString("es-PE")),
    datasets: estaciones.map((estacion, i) => ({
      label: estacion,
      data: etiquetas.map((iso) => serie.find((p) => p.x === iso && p.estacion === estacion)?.y ?? null),
      borderColor: colores[i % colores.length],
      backgroundColor: colores[i % colores.length],
      tension: 0.3,
      spanGaps: true,
    })),
  };

  return (
    <div className="dynamic-visualization">
      <div className="dv-header">
        <strong>{parametro.toUpperCase()}</strong>
        <span>
          {rango.desde} → {rango.hasta}
        </span>
      </div>
      <div className="dv-chart">
        <Line
          data={data}
          options={{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: estaciones.length > 1, labels: { color: "#8996aa" } },
            },
            scales: {
              x: { ticks: { color: "#8996aa" }, grid: { color: "#18253b" } },
              y: { ticks: { color: "#8996aa" }, grid: { color: "#18253b" } },
            },
          }}
        />
      </div>
    </div>
  );
}
