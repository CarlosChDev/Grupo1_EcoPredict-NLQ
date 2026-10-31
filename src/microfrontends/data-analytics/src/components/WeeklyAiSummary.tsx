import { useRemoteData } from "../hooks/useRemoteData";
import { DataAnalyticsApiError, describirEndpoint, obtenerResumenIa } from "../services/dataAnalyticsApi";
import type { DistritoRef, ResumenIaResponse } from "../types/analytics.types";
import { etiquetaModelo, fechaHoraLima, rangoFechas } from "../utils/formato";
import { Esqueleto, Panel, PanelError } from "./Panel";
import "./WeeklyAiSummary.css";

type ResultadoResumen = { distrito: DistritoRef } & (
  | { ok: true; datos: ResumenIaResponse }
  | { ok: false; mensaje: string }
);

/**
 * El webhook acepta un distrito por llamada, así que se pide uno por cada
 * distrito del comparativo; si uno falla, los demás se muestran igual.
 */
function cargarResumenes(distritos: DistritoRef[], signal: AbortSignal): Promise<ResultadoResumen[]> {
  return Promise.all(
    distritos.map((distrito) =>
      obtenerResumenIa(distrito.id, signal).then(
        (datos): ResultadoResumen => ({ distrito, ok: true, datos }),
        (err): ResultadoResumen => {
          if (signal.aborted) throw err;
          const mensaje = err instanceof DataAnalyticsApiError ? err.message : "Error inesperado.";
          return { distrito, ok: false, mensaje };
        },
      ),
    ),
  );
}

/** Bloque 4: resumen semanal redactado por IA de cada distrito seleccionado. */
export function WeeklyAiSummary({ distritos }: { distritos: DistritoRef[] }) {
  const [estado, reintentar] = useRemoteData(
    (signal) => cargarResumenes(distritos, signal),
    distritos.map((d) => d.id).join(","),
  );

  const semana =
    estado.tipo === "listo"
      ? estado.datos.find((r): r is ResultadoResumen & { ok: true } => r.ok && r.datos.semana !== null)?.datos.semana
      : null;

  return (
    <Panel
      numero={4}
      titulo={
        <>
          Resumen interpretativo de la semana <span className="da-tag da-tag-ia">IA</span>
        </>
      }
      subtitulo="Un texto por distrito seleccionado en el comparativo. Se genera una vez por semana."
      herramientas={semana && <span className="pill p-neutral">Semana {rangoFechas(semana.inicio, semana.fin)}</span>}
      endpoint={describirEndpoint("resumen-ia", { distrito: distritos.map((d) => d.id).join(",") })}
      fuente="analitica_insights"
    >
      {estado.tipo === "cargando" && (
        <div className="da-iagrid">
          {distritos.map((d) => (
            <Esqueleto key={d.id} alto={150} />
          ))}
        </div>
      )}
      {estado.tipo === "error" && (
        <PanelError
          titulo="El resumen de la semana no está disponible"
          mensaje={`${estado.mensaje} Los bloques 1 a 3 siguen funcionando porque leen sus propias tablas.`}
          onReintentar={reintentar}
        />
      )}
      {estado.tipo === "listo" && (
        <>
          <p className="da-ia-nota">
            <span aria-hidden="true">✦</span>
            Redactado por IA solo a partir de los agregados semanales; no consulta datos crudos ni genera SQL.
          </p>
          <div className="da-iagrid">
            {estado.datos.map((r) =>
              r.ok ? (
                <TarjetaResumen key={r.distrito.id} datos={r.datos} />
              ) : (
                <PanelError
                  key={r.distrito.id}
                  titulo={`${r.distrito.nombre}: resumen no disponible`}
                  mensaje={r.mensaje}
                  onReintentar={reintentar}
                />
              ),
            )}
          </div>
        </>
      )}
    </Panel>
  );
}

function TarjetaResumen({ datos }: { datos: ResumenIaResponse }) {
  return (
    <article className="da-iac">
      <div className="da-iac-h">
        <b>{datos.distrito.nombre}</b>
        {datos.semana && <span className="da-tag">{rangoFechas(datos.semana.inicio, datos.semana.fin)}</span>}
      </div>
      {datos.disponible && datos.resumen ? (
        <p>{datos.resumen}</p>
      ) : (
        <p className="da-vacio">Todavía no hay un resumen semanal para este distrito.</p>
      )}
      {(datos.modelo || datos.resumenGeneradoEn) && (
        <div className="da-iac-f">
          {datos.modelo && <span className="da-tag">{etiquetaModelo(datos.modelo)}</span>}
          {datos.resumenGeneradoEn && (
            <span className="da-tag">generado {fechaHoraLima(datos.resumenGeneradoEn)}</span>
          )}
        </div>
      )}
    </article>
  );
}
