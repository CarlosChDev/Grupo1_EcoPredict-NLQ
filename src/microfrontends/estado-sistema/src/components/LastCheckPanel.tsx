import { useEffect, useState } from "react";
import { formatearRelativo } from "../utils/estado";
import "./LastCheckPanel.css";

interface LastCheckPanelProps {
  ultimaExitosa: Date | null;
}

export function LastCheckPanel({ ultimaExitosa }: LastCheckPanelProps) {
  const [, forceTick] = useState(0);

  // Refresca el "hace X minutos" aunque no haya una verificación nueva.
  useEffect(() => {
    const id = setInterval(() => forceTick((n) => n + 1), 30_000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="card last-check-panel">
      <div className="card-label">
        <span className="small-icon">🕒</span>
        ÚLTIMA VERIFICACIÓN EXITOSA
      </div>

      {ultimaExitosa ? (
        <>
          <div className="last-check-ok">
            <span className="check-icon">✔</span>
            {ultimaExitosa.toLocaleString("es-PE", {
              day: "2-digit",
              month: "short",
              year: "numeric",
              hour: "2-digit",
              minute: "2-digit",
            })}
          </div>
          <p className="last-check-relative">{formatearRelativo(ultimaExitosa)} · automática cada 5 min</p>
        </>
      ) : (
        <p className="last-check-relative">Todavía no hay una verificación exitosa.</p>
      )}
    </div>
  );
}
