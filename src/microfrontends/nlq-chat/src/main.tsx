import "@ecopredict/ui-shell/src/styles/global.css";

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import {
  AppLayout,
  PreferencesProvider,
  ThemeProvider,
} from "@ecopredict/ui-shell";
import { NlqChatPage } from "./NlqChatPage";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeProvider>
      <PreferencesProvider>
        <AppLayout
          titulo="NLQ Chat IA"
          subtitulo="Pregunta en español y n8n consulta la base de datos ambiental"
          activeId="nlq-chat"
        >
          <NlqChatPage />
        </AppLayout>
      </PreferencesProvider>
    </ThemeProvider>
  </StrictMode>,
);
