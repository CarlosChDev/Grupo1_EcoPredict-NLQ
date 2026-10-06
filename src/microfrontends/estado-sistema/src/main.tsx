import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { AppLayout, PreferencesProvider, ThemeProvider } from "@ecopredict/ui-shell";
import { EstadoSistemaPage } from "./EstadoSistemaPage";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeProvider>
      <PreferencesProvider>
        <AppLayout
          titulo="Estado del Sistema"
          subtitulo="Diagnóstico técnico del webhook de Flujo B tras el despliegue"
          activeId="estado-sistema"
        >
          <EstadoSistemaPage />
        </AppLayout>
      </PreferencesProvider>
    </ThemeProvider>
  </StrictMode>,
);
