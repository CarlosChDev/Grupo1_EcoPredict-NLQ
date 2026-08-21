import { Link } from "react-router-dom";
import { usePageHeader } from "../layout/usePageHeader";
import "./NotFoundPage.css";

export function NotFoundPage() {
  usePageHeader({
    titulo: "Página no encontrada",
    subtitulo: "La ruta solicitada no existe",
  });

  return (
    <div className="card not-found-card">
      <p>404 — Esta ruta no corresponde a ningún microfrontend registrado.</p>
      <Link to="/" className="btn btn-primary">
        Volver a Inicio
      </Link>
    </div>
  );
}
