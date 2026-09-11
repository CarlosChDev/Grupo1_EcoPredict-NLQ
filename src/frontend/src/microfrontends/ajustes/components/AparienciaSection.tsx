import type { Densidad, VistaInicio } from "../../../shell/preferences/PreferencesContext";
import { usePreferences } from "../../../shell/preferences/usePreferences";
import type { ThemeMode } from "../../../shell/theme/ThemeContext";
import { useTheme } from "../../../shell/theme/useTheme";
import "./AparienciaSection.css";

const TEMAS: { id: ThemeMode; nombre: string }[] = [
  { id: "light", nombre: "Claro" },
  { id: "dark", nombre: "Oscuro" },
  { id: "system", nombre: "Sistema" },
];

const DENSIDADES: { id: Densidad; nombre: string }[] = [
  { id: "compacta", nombre: "Compacta" },
  { id: "normal", nombre: "Normal" },
  { id: "amplia", nombre: "Amplia" },
];

const VISTAS_INICIO: { id: VistaInicio; nombre: string }[] = [
  { id: "inicio", nombre: "Inicio" },
  { id: "dashboard-ambiental", nombre: "Panel de calidad del aire" },
  { id: "nlq-chat", nombre: "Asistente IA" },
  { id: "estado-sistema", nombre: "Estado del sistema" },
];

export function AparienciaSection() {
  const { mode, setMode } = useTheme();
  const { densidad, setDensidad, vistaInicio, setVistaInicio } = usePreferences();

  return (
    <div className="card ajustes-section">
      <div className="ajustes-section-header">
        <h2>Apariencia</h2>
        <p>Cómo se ve EcoPredict en este dispositivo. Los cambios se aplican al instante.</p>
      </div>

      <div className="ajustes-row">
        <div className="ajustes-row-label">
          <strong>Tema</strong>
          <span>Claro, oscuro o siguiendo el sistema operativo.</span>
        </div>
        <div className="segmented">
          {TEMAS.map((t) => (
            <button
              key={t.id}
              type="button"
              className={`segmented-option${mode === t.id ? " active" : ""}`}
              onClick={() => setMode(t.id)}
            >
              {t.nombre}
            </button>
          ))}
        </div>
      </div>

      <div className="ajustes-row">
        <div className="ajustes-row-label">
          <strong>Densidad de la interfaz</strong>
          <span>Ajusta el espaciado de tarjetas y paneles.</span>
        </div>
        <div className="segmented">
          {DENSIDADES.map((d) => (
            <button
              key={d.id}
              type="button"
              className={`segmented-option${densidad === d.id ? " active" : ""}`}
              onClick={() => setDensidad(d.id)}
            >
              {d.nombre}
            </button>
          ))}
        </div>
      </div>

      <div className="ajustes-row">
        <div className="ajustes-row-label">
          <strong>Vista de inicio</strong>
          <span>Pantalla que se abre al entrar.</span>
        </div>
        <select value={vistaInicio} onChange={(e) => setVistaInicio(e.target.value as VistaInicio)}>
          {VISTAS_INICIO.map((v) => (
            <option key={v.id} value={v.id}>
              {v.nombre}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
