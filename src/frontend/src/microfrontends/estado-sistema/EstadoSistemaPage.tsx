import { useState } from "react";
import { usePageHeader } from "../../shell/layout/usePageHeader";
import { EnvironmentPanel } from "./components/EnvironmentPanel";
import { HistoryPanel } from "./components/HistoryPanel";
import { LastCheckPanel } from "./components/LastCheckPanel";
import { WebhookStatusCard } from "./components/WebhookStatusCard";
import { useWebhookStatus } from "./hooks/useWebhookStatus";
import type { Entorno } from "./types/status.types";
import "./EstadoSistemaPage.css";

/**
 * Microfrontend: Estado del Sistema.
 *
 * A diferencia de Dashboard Ambiental, esta página SÍ hace fetch real: cada
 * "Probar conexión" (manual o automática cada 5 min) dispara Flujo B con una
 * pregunta fija y mide latencia/status reales — no hay datos de maqueta acá.
 *
 * El toggle Local/Producción solo alimenta este diagnóstico: el chat NLQ
 * real (microfrontends/nlq-chat) sigue usando VITE_N8N_WEBHOOK_URL fijo.
 */
export function EstadoSistemaPage() {
  usePageHeader({
    titulo: "Estado del Sistema",
    subtitulo: "Diagnóstico técnico del webhook de Flujo B tras el despliegue",
  });

  const [entorno, setEntorno] = useState<Entorno>("local");
  const { resultado, verificando, ultimaExitosa, historial, verificar } = useWebhookStatus(entorno);

  return (
    <div className="estado-sistema-page">
      <div className="estado-sistema-grid">
        <WebhookStatusCard resultado={resultado} verificando={verificando} onProbar={verificar} />

        <div className="estado-sistema-side">
          <EnvironmentPanel entorno={entorno} onCambiarEntorno={setEntorno} />
          <LastCheckPanel ultimaExitosa={ultimaExitosa} />
        </div>
      </div>

      <HistoryPanel historial={historial} />
    </div>
  );
}
