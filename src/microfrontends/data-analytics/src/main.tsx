import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { AppLayout, PreferencesProvider, ThemeProvider } from "@ecopredict/ui-shell";
import { DataAnalyticsPage } from "./DataAnalyticsPage";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeProvider>
      <PreferencesProvider>
        <AppLayout
          titulo="Data Analytics"
          subtitulo="Comparativo entre distritos, ranking de excedencias del ECA, patrón horario y resumen semanal"
          activeId="data-analytics"
        >
          <DataAnalyticsPage />
        </AppLayout>
      </PreferencesProvider>
    </ThemeProvider>
  </StrictMode>,
);
