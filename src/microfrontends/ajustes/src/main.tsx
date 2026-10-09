import "@ecopredict/ui-shell/src/styles/global.css";

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import {
  AppLayout,
  PreferencesProvider,
  ThemeProvider,
} from "@ecopredict/ui-shell";
import { AjustesPage } from "./AjustesPage";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeProvider>
      <PreferencesProvider>
        <AppLayout
          titulo="Ajustes"
          subtitulo="Preferencias de este dispositivo"
          activeId="ajustes"
        >
          <AjustesPage />
        </AppLayout>
      </PreferencesProvider>
    </ThemeProvider>
  </StrictMode>,
);
