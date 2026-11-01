import { useState } from "react";
import { useRemoteData } from "../hooks/useRemoteData";
import { describirEndpoint, obtenerComparativo } from "../services/dataAnalyticsApi";
import type {
  DiasPeriodo,
  DistritoComparado,
  DistritoDisponible,
  ParametroAnalitica,
  ResumenParametro,
} from "../types/analytics.types";
import { f1, fechaCorta, PARAMETRO_COLOR, PARAMETRO_LABEL, rangoFechas } from "../utils/formato";
import { Esqueleto, Panel, PanelError } from "./Panel";
import { Sparkline } from "./Sparkline";
import "./DistrictComparison.css";

const MIN_DISTRITOS = 2;
const MAX_DISTRITOS = 4;
const PARAMETROS: ParametroAnalitica[] = ["pm25", "pm10"];

interface DistrictComparisonProps {
  distritos: DistritoDisponible[];
  seleccion: string[];
  onCambiarSeleccion: (ids: string[]) => void;
  dias: DiasPeriodo;
}

/** Bloque 1: promedio del periodo frente al anterior, de 2 a 4 distritos. */
export function DistrictComparison({ distritos, seleccion, onCambiarSeleccion, dias }: DistrictComparisonProps) {
  const [aviso, setAviso] = useState("");
  const [estado, reintentar] = useRemoteData(
    (signal) => obtenerComparativo(seleccion, dias, signal),
    `${seleccion.join(",")}|${dias}`,
  );

  const alternar = (id: string) => {
    if (seleccion.includes(id)) {
      if (seleccion.length <= MIN_DISTRITOS) return setAviso("Se necesitan al menos 2 distritos para comparar.");
      onCambiarSeleccion(seleccion.filter((x) => x !== id));
    } else {
      if (seleccion.length >= MAX_DISTRITOS) return setAviso("Máximo 4 distritos a la vez: quita uno primero.");
      onCambiarSeleccion([...seleccion, id]);
    }
    setAviso("");
  };

  return (
    <Panel
      numero={1}
      titulo="Comparativo entre distritos"
      subtitulo="Elige de 2 a 4 distritos. Promedio del periodo frente al periodo anterior."
      herramientas={
        estado.tipo === "listo" && (
          <span className="pill p-neutral">
            {rangoFechas(estado.datos.periodo.desde, estado.datos.periodo.hasta)} vs.{" "}
            {rangoFechas(estado.datos.periodoAnterior.desde, estado.datos.periodoAnterior.hasta)}
          </span>
        )
      }
      endpoint={describirEndpoint("comparativo", { distritos: seleccion.join(","), dias })}
      fuente="analitica_diaria"
    >
      <div className="da-chips">
        {distritos.map((d) => {
          const suficiente = dias === 7 ? d.datosSuficientes7 : d.datosSuficientes30;
          const activo = seleccion.includes(d.id);
          return (
            <button
              key={d.id}
              type="button"
              className={`da-chip ${activo ? "on" : ""} ${suficiente ? "" : "pocos"}`}
              aria-pressed={activo}
              title={suficiente ? undefined : `Pocos datos en los últimos ${dias} días (último: ${fechaCorta(d.ultimoDato)})`}
              onClick={() => alternar(d.id)}
            >
              {d.nombre}
            </button>
          );
        })}
      </div>
      <p className="da-hint" aria-live="polite">{aviso}</p>

      {estado.tipo === "cargando" && (
        <div className="da-zgrid">
          {seleccion.map((id) => (
            <Esqueleto key={id} alto={190} />
          ))}
        </div>
      )}
      {estado.tipo === "error" && (
        <PanelError titulo="No se pudo cargar el comparativo" mensaje={estado.mensaje} onReintentar={reintentar} />
      )}
      {estado.tipo === "listo" && (
        <>
          <div className="da-zgrid">
            {estado.datos.distritos.map((d) => (
              <TarjetaDistrito key={d.id} distrito={d} dias={estado.datos.dias} />
            ))}
          </div>
          <div className="da-leyenda">
            <span>
              <i className="da-leyenda-eca" /> límite ECA 24 h
            </span>
            <span>
              <i className="da-leyenda-exc" /> día que excedió
            </span>
          </div>
        </>
      )}
    </Panel>
  );
}

function TarjetaDistrito({ distrito, dias }: { distrito: DistritoComparado; dias: DiasPeriodo }) {
  const { parametros } = distrito;

  if (!distrito.datosSuficientes || !parametros) {
    return (
      <div className="da-zc da-zc-vacia">
        <div className="da-zc-h">
          <b>{distrito.nombre}</b>
        </div>
        <p className="da-vacio">
          Sin datos suficientes en los últimos {dias} días
          {distrito.ultimoDato ? ` · último dato ${fechaCorta(distrito.ultimoDato)}` : ""}.
        </p>
      </div>
    );
  }

  return (
    <div className="da-zc">
      <div className="da-zc-h">
        <b>{distrito.nombre}</b>
        <span>
          {parametros.pm25.diasConDato} de {dias} días con dato
        </span>
      </div>
      {PARAMETROS.map((p) => (
        <FilaParametro
          key={p}
          parametro={p}
          resumen={parametros[p]}
          valores={distrito.serie.map((s) => s[p])}
          fechas={distrito.serie.map((s) => fechaCorta(s.fecha))}
        />
      ))}
    </div>
  );
}

function FilaParametro({
  parametro,
  resumen,
  valores,
  fechas,
}: {
  parametro: ParametroAnalitica;
  resumen: ResumenParametro;
  valores: (number | null)[];
  fechas: string[];
}) {
  const { promedio, anterior, variacionPct, tendencia } = resumen;
  const claseDelta = tendencia === "sube" ? "up" : tendencia === "baja" ? "down" : "flat";
  const flecha = tendencia === "sube" ? "▲" : tendencia === "baja" ? "▼" : "●";

  return (
    <div className="da-prow">
      <div>
        <div className="da-plabel" style={{ color: PARAMETRO_COLOR[parametro] }}>
          {PARAMETRO_LABEL[parametro]}
        </div>
        <div className="tile-num">
          {promedio === null ? "—" : f1(promedio)}
          <span className="unit">{resumen.unidad}</span>
        </div>
      </div>
      <div className="da-pmeta">
        {variacionPct !== null ? (
          <span className={`da-delta ${claseDelta}`}>
            {flecha} {f1(Math.abs(variacionPct))} %
          </span>
        ) : (
          <span className="da-delta flat">sin periodo anterior</span>
        )}
        {anterior !== null && <span>antes {f1(anterior)}</span>}
        {tendencia && <span>· {tendencia}</span>}
        {resumen.diasExcedidos > 0 && (
          <span className="da-pexc">
            {resumen.diasExcedidos} día{resumen.diasExcedidos > 1 ? "s" : ""} sobre el ECA
          </span>
        )}
      </div>
      <Sparkline
        valores={valores}
        etiquetas={fechas}
        limite={resumen.limiteEca}
        color={PARAMETRO_COLOR[parametro]}
        unidad={resumen.unidad}
      />
    </div>
  );
}
