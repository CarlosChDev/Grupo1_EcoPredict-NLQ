import { AppLayout } from "@ecopredict/ui-shell";
import "./NotFoundPage.css";

export function NotFoundPage() {
  return (
    <AppLayout
      titulo="Página no encontrada"
      subtitulo="La ruta solicitada no existe"
      activeId="inicio"
    >
      <div className="card not-found-card">
        <p>404 — Esta ruta no corresponde a ningún microfrontend registrado.</p>
        <a href="/" className="btn btn-primary">
          Volver a Inicio
        </a>
      </div>
    </AppLayout>
  );
}
