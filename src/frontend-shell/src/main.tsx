import "@ecopredict/ui-shell/src/styles/global.css";

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { PreferencesProvider, ThemeProvider } from "@ecopredict/ui-shell";
import { App } from "./App";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeProvider>
      <PreferencesProvider>
        <App />
      </PreferencesProvider>
    </ThemeProvider>
  </StrictMode>,
);
