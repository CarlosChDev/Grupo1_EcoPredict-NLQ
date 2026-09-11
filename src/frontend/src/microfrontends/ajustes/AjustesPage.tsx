import { useState } from "react";
import { usePageHeader } from "../../shell/layout/usePageHeader";
import { AccesibilidadSection } from "./components/AccesibilidadSection";
import { AparienciaSection } from "./components/AparienciaSection";
import "./AjustesPage.css";

type Seccion = "apariencia" | "accesibilidad";

const SECCIONES: { id: Seccion; nombre: string }[] = [
  { id: "apariencia", nombre: "Apariencia" },
  { id: "accesibilidad", nombre: "Accesibilidad" },
];

/**
 * Microfrontend: Ajustes. Cubre solo las preferencias que el shell aplica de
 * verdad (tema, densidad, vista de inicio, alto contraste, reducir
 * movimiento — ver shell/preferences). No incluye secciones como "Cuenta y
 * acceso" o "Umbrales y alertas": no hay backend de autenticación ni de
 * configuración de umbrales todavía.
 */
export function AjustesPage() {
  usePageHeader({
    titulo: "Ajustes",
    subtitulo: "Preferencias de este dispositivo",
  });

  const [seccion, setSeccion] = useState<Seccion>("apariencia");

  return (
    <div className="ajustes-page">
      <nav className="ajustes-nav">
        {SECCIONES.map((s) => (
          <button
            key={s.id}
            type="button"
            className={`ajustes-nav-item${seccion === s.id ? " active" : ""}`}
            onClick={() => setSeccion(s.id)}
          >
            {s.nombre}
          </button>
        ))}
      </nav>

      <div className="ajustes-content">
        {seccion === "apariencia" ? <AparienciaSection /> : <AccesibilidadSection />}
      </div>
    </div>
  );
}
