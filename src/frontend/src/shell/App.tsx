import { Suspense, lazy } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AppLayout } from "./layout/AppLayout";
import { InicioPage } from "./pages/InicioPage";
import { NotFoundPage } from "./pages/NotFoundPage";

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

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route index element={<InicioPage />} />
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
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
