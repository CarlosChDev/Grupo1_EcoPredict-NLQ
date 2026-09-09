import { Suspense, lazy } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AppLayout } from "./layout/AppLayout";
import { InicioPage } from "./pages/InicioPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { microfrontends } from "./config/microfrontends";
import { usePreferences } from "./preferences/usePreferences";

// Cada microfrontend se carga bajo demanda: entra a su propio chunk JS y
// solo se descarga cuando el usuario navega a su ruta.
const NlqChatPage = lazy(() =>
  import("../microfrontends/nlq-chat/NlqChatPage").then((m) => ({
    default: m.NlqChatPage,
  })),
);

const DashboardAmbientalPage = lazy(() =>
  import("../microfrontends/dashboard-ambiental/DashboardAmbientalPage").then((m) => ({
    default: m.DashboardAmbientalPage,
  })),
);

const EstadoSistemaPage = lazy(() =>
  import("../microfrontends/estado-sistema/EstadoSistemaPage").then((m) => ({
    default: m.EstadoSistemaPage,
  })),
);

const AjustesPage = lazy(() =>
  import("../microfrontends/ajustes/AjustesPage").then((m) => ({
    default: m.AjustesPage,
  })),
);

/** Respeta Ajustes › Apariencia › "Vista de inicio" al entrar a "/". */
function IndexRoute() {
  const { vistaInicio } = usePreferences();
  if (vistaInicio === "inicio") return <InicioPage />;

  const destino = microfrontends.find((mf) => mf.id === vistaInicio);
  return <Navigate to={destino?.ruta ?? "/"} replace />;
}

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route index element={<IndexRoute />} />
          <Route
            path="nlq-chat"
            element={
              <Suspense fallback={<div className="card">Cargando NLQ Chat IA…</div>}>
                <NlqChatPage />
              </Suspense>
            }
          />
          <Route
            path="dashboard-ambiental"
            element={
              <Suspense fallback={<div className="card">Cargando Dashboard Ambiental…</div>}>
                <DashboardAmbientalPage />
              </Suspense>
            }
          />
          <Route
            path="estado-sistema"
            element={
              <Suspense fallback={<div className="card">Cargando Estado del Sistema…</div>}>
                <EstadoSistemaPage />
              </Suspense>
            }
          />
          <Route
            path="ajustes"
            element={
              <Suspense fallback={<div className="card">Cargando Ajustes…</div>}>
                <AjustesPage />
              </Suspense>
            }
          />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
