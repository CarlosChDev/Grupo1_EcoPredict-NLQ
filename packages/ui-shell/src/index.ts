export { AppLayout } from "./layout/AppLayout";
export type { AppLayoutProps } from "./layout/AppLayout";
export { Sidebar } from "./layout/Sidebar";
export { Topbar } from "./layout/Topbar";
export { TelegramBubble } from "./widgets/TelegramBubble";

export { ThemeProvider } from "./theme/ThemeContext";
export type { ThemeMode } from "./theme/ThemeContext";
export { useTheme } from "./theme/useTheme";

export { PreferencesProvider } from "./preferences/PreferencesContext";
export type { Densidad, VistaInicio, PreferencesState } from "./preferences/PreferencesContext";
export { usePreferences } from "./preferences/usePreferences";

export { microfrontends } from "./registry";
export type { MicrofrontendConfig } from "./registry";

import "./styles/global.css";
