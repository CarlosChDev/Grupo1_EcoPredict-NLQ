import { useEffect } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { microfrontends, usePreferences } from "@ecopredict/ui-shell";
import { InicioPage } from "./pages/InicioPage";
import { NotFoundPage } from "./pages/NotFoundPage";

/**
 * Respeta Ajustes › Apariencia › "Vista de inicio" al entrar a "/". Ya no es
 * un <Navigate> interno de React Router: el destino vive en otro despliegue
 * (otro microfrontend), así que hace falta una navegación real de
 * navegador.
 */
function IndexRoute() {
  const { vistaInicio } = usePreferences();

  useEffect(() => {
    if (vistaInicio === "inicio") return;
    const destino = microfrontends.find((mf) => mf.id === vistaInicio);
    if (destino) window.location.replace(destino.ruta);
  }, [vistaInicio]);

  if (vistaInicio !== "inicio") return null;
  return <InicioPage />;
}

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<IndexRoute />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}
