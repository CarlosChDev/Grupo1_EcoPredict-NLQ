import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./shell/App";
import { PreferencesProvider } from "./shell/preferences/PreferencesContext";
import { ThemeProvider } from "./shell/theme/ThemeContext";
import "./styles/global.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeProvider>
      <PreferencesProvider>
        <App />
      </PreferencesProvider>
    </ThemeProvider>
  </StrictMode>,
);
