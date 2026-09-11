import { usePreferences } from "../../../shell/preferences/usePreferences";
import "./AparienciaSection.css";

export function AccesibilidadSection() {
  const { altoContraste, setAltoContraste, reducirMovimiento, setReducirMovimiento } = usePreferences();

  return (
    <div className="card ajustes-section">
      <div className="ajustes-section-header">
        <h2>Accesibilidad</h2>
        <p>Pensado para que el panel se lea bien en cualquier condición.</p>
      </div>

      <div className="ajustes-row">
        <div className="ajustes-row-label">
          <strong>Alto contraste</strong>
          <span>Sube el contraste de bordes y texto secundario, y desactiva el vidrio esmerilado.</span>
        </div>
        <button
          type="button"
          role="switch"
          aria-checked={altoContraste}
          className={`toggle${altoContraste ? " active" : ""}`}
          onClick={() => setAltoContraste(!altoContraste)}
        >
          <span className="toggle-knob" />
        </button>
      </div>

      <div className="ajustes-row">
        <div className="ajustes-row-label">
          <strong>Reducir movimiento</strong>
          <span>Desactiva animaciones y transiciones, más allá de la preferencia del sistema.</span>
        </div>
        <button
          type="button"
          role="switch"
          aria-checked={reducirMovimiento}
          className={`toggle${reducirMovimiento ? " active" : ""}`}
          onClick={() => setReducirMovimiento(!reducirMovimiento)}
        >
          <span className="toggle-knob" />
        </button>
      </div>
    </div>
  );
}
