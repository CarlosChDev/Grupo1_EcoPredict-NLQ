import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { AppLayout, PreferencesProvider, ThemeProvider } from "@ecopredict/ui-shell";
import { DashboardAmbientalPage } from "./DashboardAmbientalPage";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeProvider>
      <PreferencesProvider>
        <AppLayout
          titulo="Panel de calidad del aire"
          subtitulo="Lima Metropolitana · datos horarios"
          activeId="dashboard-ambiental"
        >
          <DashboardAmbientalPage />
        </AppLayout>
      </PreferencesProvider>
    </ThemeProvider>
  </StrictMode>,
);
