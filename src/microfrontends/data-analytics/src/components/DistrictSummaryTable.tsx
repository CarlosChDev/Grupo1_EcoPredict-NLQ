import type { EstacionResumen, MedicionParametro } from "../types/analytics.types";
import { nivelPorEca } from "../utils/eca";
import { NIVEL_COLOR_VAR, NIVEL_LABEL, NIVEL_PILL_CLASS, peorNivel } from "../utils/nivel";
import { haceTiempo } from "../utils/tiempo";
import "./DistrictSummaryTable.css";

function indicadorTendencia(medicion?: MedicionParametro) {
  if (!medicion || medicion.valorAnterior === undefined || medicion.valorAnterior === null) {
    return <span className="tendencia tendencia-sin-dato">—</span>;
  }

  const delta = medicion.valor - medicion.valorAnterior;
  if (delta === 0) return <span className="tendencia tendencia-estable">— estable</span>;

  const subio = delta > 0;
  return (
    <span className={`tendencia ${subio ? "tendencia-sube" : "tendencia-baja"}`}>
      {subio ? "▲" : "▼"} {Math.abs(Math.round((delta / medicion.valorAnterior) * 100))}%
    </span>
  );
}

interface DistrictSummaryTableProps {
  estaciones: EstacionResumen[];
}

/**
 * HU-03, tarea 3: "Resumen por distrito" con categoría ECA e indicador de
 * tendencia, consumiendo GET /estaciones.
 *
 * El esquema de `estaciones` no tiene un campo "distrito" (`zona` es
 * 'industrial'/'residencial'/'urbana', no un distrito de Lima) — esta
 * tabla usa cada estación como proxy de la zona geográfica que representa,
 * que es la granularidad real que expone el backend hoy.
 */
export function DistrictSummaryTable({ estaciones }: DistrictSummaryTableProps) {
  return (
    <div className="card district-summary-card">
      <div className="card-label">
        <span className="small-icon">🗺️</span>
        Resumen por distrito (estación · zona de monitoreo)
      </div>

      <div className="district-summary-table-wrap">
        <table className="district-summary-table">
          <thead>
            <tr>
              <th>Estación</th>
              <th>Zona</th>
              <th>PM2.5</th>
              <th>PM10</th>
              <th>Categoría ECA</th>
              <th>Actualizado</th>
            </tr>
          </thead>
          <tbody>
            {estaciones.map((estacion) => {
              const pm25 = estacion.mediciones.find((m) => m.parametro === "pm25");
              const pm10 = estacion.mediciones.find((m) => m.parametro === "pm10");

              const niveles = estacion.mediciones.map((m) => nivelPorEca(m.parametro, m.valor));
              const categoria = peorNivel(niveles);
              const color = NIVEL_COLOR_VAR[categoria];

              const masReciente = estacion.mediciones.reduce<string | null>(
                (acc, m) => (!acc || m.medidoEn > acc ? m.medidoEn : acc),
                null,
              );

              return (
                <tr key={estacion.id}>
                  <td className="district-summary-nombre">{estacion.nombre}</td>
                  <td className="district-summary-zona">{estacion.zona ?? "—"}</td>
                  <td>
                    {pm25 ? (
                      <>
                        <span className="tile-num district-summary-valor">{pm25.valor}</span>{" "}
                        <span className="unit">{pm25.unidad}</span> {indicadorTendencia(pm25)}
                      </>
                    ) : (
                      "—"
                    )}
                  </td>
                  <td>
                    {pm10 ? (
                      <>
                        <span className="tile-num district-summary-valor">{pm10.valor}</span>{" "}
                        <span className="unit">{pm10.unidad}</span> {indicadorTendencia(pm10)}
                      </>
                    ) : (
                      "—"
                    )}
                  </td>
                  <td>
                    <span className={`pill ${NIVEL_PILL_CLASS[categoria]}`} style={{ color }}>
                      {NIVEL_LABEL[categoria]}
                    </span>
                  </td>
                  <td className="district-summary-tiempo">{masReciente ? haceTiempo(masReciente) : "—"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
