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
          subtitulo="Resumen por distrito, tendencia de PM2.5/PM10 y alertas con sus factores"
          activeId="data-analytics"
        >
          <DataAnalyticsPage />
        </AppLayout>
      </PreferencesProvider>
    </ThemeProvider>
  </StrictMode>,
);
