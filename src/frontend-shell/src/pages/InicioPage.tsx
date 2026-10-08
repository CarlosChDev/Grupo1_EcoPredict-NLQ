import { AppLayout, microfrontends } from "@ecopredict/ui-shell";
import "./InicioPage.css";

export function InicioPage() {
  return (
    <AppLayout
      titulo="Bienvenida a EcoPredict - NLQ"
      subtitulo="Elige un módulo para empezar a explorar los datos ambientales"
      activeId="inicio"
    >
      <div className="inicio-page">
        <div className="card card-gradient inicio-hero">
          <span className="badge badge-teal">Shell / Host React</span>
          <h2>Consulta y analiza la calidad del aire de Lima</h2>
          <p>
            EcoPredict - NLQ integra fuentes de datos ambientales, automatización con n8n e
            inteligencia artificial. Cada módulo de abajo es un microfrontend independiente,
            desplegado y versionado por su cuenta.
          </p>
        </div>

        <div className="inicio-grid">
          {microfrontends.map((mf) => {
            const disponible = mf.estado === "disponible";
            const contenido = (
              <>
                <div className="inicio-card-icon">{mf.icono}</div>
                <h3>{mf.nombre}</h3>
                <p>{mf.descripcion}</p>
                <span className={`badge ${disponible ? "badge-teal" : "badge-muted"}`}>
                  {disponible ? "Disponible" : "Próximamente"}
                </span>
              </>
            );

            return disponible ? (
              <a key={mf.id} href={mf.ruta} className="card inicio-card">
                {contenido}
              </a>
            ) : (
              <div key={mf.id} className="card inicio-card disabled">
                {contenido}
              </div>
            );
          })}
        </div>
      </div>
    </AppLayout>
  );
}
