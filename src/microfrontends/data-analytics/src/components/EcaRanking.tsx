import { useState } from "react";
import { useRemoteData } from "../hooks/useRemoteData";
import { describirEndpoint, obtenerRankingEca } from "../services/dataAnalyticsApi";
import type { DiasPeriodo, DistritoDisponible, FilaRanking, ParametroAnalitica } from "../types/analytics.types";
import { f1, nombreDesdeId, PARAMETRO_LABEL } from "../utils/formato";
import { Esqueleto, Panel, PanelError, Segmentado } from "./Panel";
import "./EcaRanking.css";

const OPCIONES_PARAMETRO = [
  { valor: "pm25" as const, etiqueta: "PM2.5" },
  { valor: "pm10" as const, etiqueta: "PM10" },
];

interface EcaRankingProps {
  distritos: DistritoDisponible[];
  dias: DiasPeriodo;
}

/**
 * Bloque 2: distritos ordenados por días sobre el ECA de 24 h (orden que
 * ya devuelve el webhook). La barra muestra la lectura máxima del periodo
 * frente al límite, marcado con una línea vertical.
 */
export function EcaRanking({ distritos, dias }: EcaRankingProps) {
  const [parametro, setParametro] = useState<ParametroAnalitica>("pm25");
  const [estado, reintentar] = useRemoteData(
    (signal) => obtenerRankingEca(parametro, dias, signal),
    `${parametro}|${dias}`,
  );

  const nombreDe = (id: string) => distritos.find((d) => d.id === id)?.nombre ?? nombreDesdeId(id);

  return (
    <Panel
      numero={2}
      titulo="Ranking de excedencias del ECA"
      subtitulo="¿Qué zonas son las más problemáticas? Días sobre el límite de 24 h."
      herramientas={
        <Segmentado
          opciones={OPCIONES_PARAMETRO}
          valor={parametro}
          onCambiar={setParametro}
          pequeno
          etiquetaAria="Parámetro del ranking"
        />
      }
      endpoint={describirEndpoint("ranking-eca", { parametro, dias })}
      fuente="analitica_diaria"
    >
      {estado.tipo === "cargando" && <Esqueleto alto={26} cantidad={7} />}
      {estado.tipo === "error" && (
        <PanelError titulo="No se pudo cargar el ranking" mensaje={estado.mensaje} onReintentar={reintentar} />
      )}
      {estado.tipo === "listo" && (
        <>
          <div className="da-leyenda da-rk-leyenda">
            <span>
              Límite ECA 24 h de {PARAMETRO_LABEL[estado.datos.parametro]}:{" "}
              <b>
                {estado.datos.limiteEca} {estado.datos.unidad}
              </b>
            </span>
            <span>Periodo: {estado.datos.dias} días</span>
            {estado.datos.criterio === "referencial" && <span>Comparación referencial</span>}
          </div>

          {estado.datos.ranking.length === 0 ? (
            <p className="da-vacio">Ningún distrito tiene datos suficientes en este periodo.</p>
          ) : (
            <ol className="da-rk">
              {estado.datos.ranking.map((fila) => (
                <FilaRk
                  key={fila.distrito.id}
                  fila={fila}
                  limite={estado.datos.limiteEca}
                  escala={Math.max(estado.datos.limiteEca * 1.25, ...estado.datos.ranking.map((r) => r.maximo))}
                />
              ))}
            </ol>
          )}

          {estado.datos.sinDatosSuficientes.length > 0 && (
            <p className="da-rk-sin">
              Sin datos suficientes: {estado.datos.sinDatosSuficientes.map(nombreDe).join(", ")}.
            </p>
          )}
        </>
      )}
    </Panel>
  );
}

function FilaRk({ fila, limite, escala }: { fila: FilaRanking; limite: number; escala: number }) {
  const color = fila.diasExcedidos > 0 ? "var(--crit)" : fila.maximo > limite ? "var(--mod)" : "var(--good)";

  return (
    <li className={fila.diasExcedidos > 0 && fila.posicion <= 3 ? "top" : ""}>
      <span className="da-rk-pos">{fila.posicion}</span>
      <span className="da-rk-nm">{fila.distrito.nombre}</span>
      <span
        className="da-rk-bar"
        title={`Lectura máxima ${f1(fila.maximo)} · promedio ${f1(fila.promedio)} · límite ${limite}`}
      >
        <i style={{ width: `${Math.max((fila.maximo / escala) * 100, 2)}%`, background: color }} />
        <em style={{ left: `${(limite / escala) * 100}%` }} />
      </span>
      <span className="da-rk-mx">
        <b>
          {fila.diasExcedidos} de {fila.diasConDato} días
        </b>
        máx. {f1(fila.maximo)}
      </span>
    </li>
  );
}
