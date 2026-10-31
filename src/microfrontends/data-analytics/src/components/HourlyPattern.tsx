import { useState } from "react";
import { useRemoteData } from "../hooks/useRemoteData";
import { describirEndpoint, obtenerPatronHorario } from "../services/dataAnalyticsApi";
import type { DiasPeriodo, DistritoDisponible, ParametroAnalitica, PatronHorarioResponse } from "../types/analytics.types";
import { f1, horaDelDia, PARAMETRO_COLOR } from "../utils/formato";
import { Esqueleto, Panel, PanelError, Segmentado } from "./Panel";
import "./HourlyPattern.css";

const OPCIONES_PARAMETRO = [
  { valor: "pm25" as const, etiqueta: "PM2.5" },
  { valor: "pm10" as const, etiqueta: "PM10" },
];

interface HourlyPatternProps {
  distritos: DistritoDisponible[];
  distritoInicial: string;
  dias: DiasPeriodo;
}

/** Bloque 3: concentración promedio por hora del día de un distrito. */
export function HourlyPattern({ distritos, distritoInicial, dias }: HourlyPatternProps) {
  const [distrito, setDistrito] = useState(distritoInicial);
  const [parametro, setParametro] = useState<ParametroAnalitica>("pm25");
  const [estado, reintentar] = useRemoteData(
    (signal) => obtenerPatronHorario(distrito, parametro, dias, signal),
    `${distrito}|${parametro}|${dias}`,
  );

  return (
    <Panel
      numero={3}
      titulo="Patrón horario"
      subtitulo="Concentración promedio por hora del día (hora de Lima)."
      herramientas={
        <Segmentado
          opciones={OPCIONES_PARAMETRO}
          valor={parametro}
          onCambiar={setParametro}
          pequeno
          etiquetaAria="Parámetro del patrón horario"
        />
      }
      endpoint={describirEndpoint("patron-horario", { distrito, parametro, dias })}
      fuente="mediciones_aire"
    >
      <div className="da-hz-top">
        <select
          className="da-sel"
          value={distrito}
          onChange={(e) => setDistrito(e.target.value)}
          aria-label="Distrito del patrón horario"
        >
          {distritos.map((d) => (
            <option key={d.id} value={d.id}>
              {d.nombre}
            </option>
          ))}
        </select>
        <span>Promedio de los últimos {dias} días</span>
      </div>

      {estado.tipo === "cargando" && <Esqueleto alto={230} />}
      {estado.tipo === "error" && (
        <PanelError titulo="No se pudo cargar el patrón horario" mensaje={estado.mensaje} onReintentar={reintentar} />
      )}
      {estado.tipo === "listo" && <ContenidoPatron datos={estado.datos} />}
    </Panel>
  );
}

/** Hora crítica que manda el webhook; si no la manda pero hay datos suficientes, la del promedio más alto. */
function horaCriticaDe(datos: PatronHorarioResponse, conDato: { hora: number; promedio: number }[]): number | null {
  const { horaCritica } = datos;
  if (typeof horaCritica === "number") return horaCritica;
  if (horaCritica && typeof horaCritica.hora === "number") return horaCritica.hora;
  if (!datos.datosSuficientes || conDato.length === 0) return null;
  return conDato.reduce((a, b) => (b.promedio > a.promedio ? b : a)).hora;
}

function ContenidoPatron({ datos }: { datos: PatronHorarioResponse }) {
  const conDato = datos.horas.filter((h): h is { hora: number; promedio: number; n: number } => h.promedio !== null);

  if (conDato.length === 0) {
    return <p className="da-vacio">No hay mediciones de este distrito en el periodo.</p>;
  }

  const pico = horaCriticaDe(datos, conDato);
  const valorDe = (hora: number) => datos.horas.find((h) => h.hora === hora)?.promedio ?? null;
  const valle = datos.datosSuficientes ? conDato.reduce((a, b) => (b.promedio < a.promedio ? b : a)) : null;
  const valorPico = pico !== null ? valorDe(pico) : null;

  return (
    <>
      {!datos.datosSuficientes && (
        <p className="da-aviso da-hz-aviso">
          Datos insuficientes: hay mediciones en {conDato.length} de 24 horas. El gráfico muestra lo disponible,
          pero aún no se calcula la hora crítica.
        </p>
      )}
      <GraficoHorario datos={datos} pico={pico} />
      <div className="da-hstats">
        <div className="da-hs crit">
          <span>Hora crítica</span>
          <b>{pico !== null ? horaDelDia(pico) : "—"}</b>
          {valorPico !== null && (
            <small>
              {f1(valorPico)} {datos.unidad}
            </small>
          )}
        </div>
        <div className="da-hs">
          <span>Hora más limpia</span>
          <b>{valle ? horaDelDia(valle.hora) : "—"}</b>
          {valle && (
            <small>
              {f1(valle.promedio)} {datos.unidad}
            </small>
          )}
        </div>
        <div className="da-hs">
          <span>Pico / valle</span>
          <b>{valorPico !== null && valle && valle.promedio > 0 ? `× ${f1(valorPico / valle.promedio)}` : "—"}</b>
        </div>
      </div>
    </>
  );
}

const W = 640;
const H = 230;
const M = { l: 38, r: 12, t: 18, b: 28 };

function GraficoHorario({ datos, pico }: { datos: PatronHorarioResponse; pico: number | null }) {
  const color = PARAMETRO_COLOR[datos.parametro];
  const valores = datos.horas.map((h) => h.promedio);
  const maxDato = Math.max(...valores.filter((v): v is number => v !== null));
  // Múltiplo de 20 para que las 4 divisiones del eje caigan en números redondos.
  const max = Math.max(Math.ceil((maxDato * 1.15) / 20) * 20, 20);
  const X = (h: number) => M.l + (h / 23) * (W - M.l - M.r);
  const Y = (v: number) => M.t + (1 - v / max) * (H - M.t - M.b);

  // Tramos de horas consecutivas con dato; una hora vacía corta la línea.
  const tramos: number[][] = [];
  valores.forEach((v, h) => {
    if (v === null) return;
    const ultimo = tramos[tramos.length - 1];
    if (ultimo && ultimo[ultimo.length - 1] === h - 1) ultimo.push(h);
    else tramos.push([h]);
  });

  const valorPico = pico !== null ? valores[pico] : null;

  return (
    <svg className="da-hchart" viewBox={`0 0 ${W} ${H}`} role="img"
      aria-label={`Promedio horario de ${datos.parametro === "pm25" ? "PM2.5" : "PM10"} en ${datos.distrito.nombre}`}>
      {[0, 1, 2, 3, 4].map((k) => {
        const v = (max * k) / 4;
        return (
          <g key={k}>
            <line x1={M.l} x2={W - M.r} y1={Y(v)} y2={Y(v)} className="da-hc-grid" />
            <text x={M.l - 6} y={Y(v) + 4} textAnchor="end" className="da-hc-eje">
              {Math.round(v)}
            </text>
          </g>
        );
      })}
      {Array.from({ length: 8 }, (_, i) => i * 3).map((h) => (
        <text key={h} x={X(h)} y={H - 8} textAnchor="middle" className="da-hc-eje">
          {horaDelDia(h)}
        </text>
      ))}

      {/* Horas punta de tránsito en Lima */}
      <rect x={X(6.5)} y={M.t} width={X(9.5) - X(6.5)} height={H - M.t - M.b} className="da-hc-punta" />
      <rect x={X(17.5)} y={M.t} width={X(20.5) - X(17.5)} height={H - M.t - M.b} className="da-hc-punta" />

      {tramos.map((t) => {
        const puntos = t.map((h) => `${X(h).toFixed(1)},${Y(valores[h]!).toFixed(1)}`).join(" ");
        return (
          <g key={t[0]}>
            {t.length > 1 && (
              <>
                <polygon points={`${X(t[0])},${Y(0)} ${puntos} ${X(t[t.length - 1])},${Y(0)}`} fill={color}
                  fillOpacity={0.14} />
                <polyline points={puntos} fill="none" stroke={color} strokeWidth={2.2} strokeLinejoin="round" />
              </>
            )}
            {t.map((h) => (
              <circle key={h} cx={X(h)} cy={Y(valores[h]!)} r={3} fill={color} />
            ))}
          </g>
        );
      })}

      {pico !== null && valorPico !== null && (
        <g>
          <line x1={X(pico)} x2={X(pico)} y1={Y(valorPico)} y2={Y(0)} className="da-hc-pico-linea" />
          <circle cx={X(pico)} cy={Y(valorPico)} r={5} className="da-hc-pico" />
          <text x={X(pico) + (pico > 18 ? -8 : 8)} y={Math.max(Y(valorPico) - 8, 12)}
            textAnchor={pico > 18 ? "end" : "start"} className="da-hc-pico-txt">
            Hora crítica {horaDelDia(pico)}
          </text>
        </g>
      )}

      {datos.horas.map((h) => (
        <rect key={h.hora} x={X(h.hora) - 12} y={M.t} width={24} height={H - M.t - M.b} fill="transparent">
          <title>
            {h.promedio === null
              ? `${horaDelDia(h.hora)} · sin dato`
              : `${horaDelDia(h.hora)} · ${f1(h.promedio)} ${datos.unidad} (${h.n} mediciones)`}
          </title>
        </rect>
      ))}
    </svg>
  );
}
