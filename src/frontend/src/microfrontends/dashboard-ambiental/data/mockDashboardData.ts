import type { EstacionResumen, PuntoSerieHoraria } from "../types/dashboard.types";

/**
 * Datos de ejemplo SOLO para maquetar la vista. Los valores respetan los
 * rangos físicos válidos que usa "Filtrar lecturas invalidas" en FLUJO A,
 * para que la maqueta se vea realista. Reemplazar por datos reales cuando
 * exista un webhook de lectura (ver nota en dashboard.types.ts).
 */
const MEDIDO_EN = "2026-09-09T14:00:00Z";

export const ESTACIONES_MOCK: EstacionResumen[] = [
  {
    id: 1,
    nombre: "SANTA ANITA",
    zona: "Lima Este",
    mediciones: [
      { parametro: "pm25", valor: 41, valorAnterior: 37, unidad: "µg/m³", medidoEn: MEDIDO_EN },
      { parametro: "pm10", valor: 86, valorAnterior: 80, unidad: "µg/m³", medidoEn: MEDIDO_EN },
      { parametro: "o3", valor: 54, valorAnterior: 59, unidad: "µg/m³", medidoEn: MEDIDO_EN },
      { parametro: "no2", valor: 38, valorAnterior: 37, unidad: "µg/m³", medidoEn: MEDIDO_EN },
      { parametro: "so2", valor: 11, valorAnterior: 11.5, unidad: "µg/m³", medidoEn: MEDIDO_EN },
      { parametro: "co", valor: 0.9, valorAnterior: 0.9, unidad: "mg/m³", medidoEn: MEDIDO_EN },
    ],
  },
  {
    id: 2,
    nombre: "HUACHIPA",
    zona: "Lima Este",
    mediciones: [
      { parametro: "pm25", valor: 63, valorAnterior: 55, unidad: "µg/m³", medidoEn: MEDIDO_EN },
      { parametro: "pm10", valor: 101, valorAnterior: 95, unidad: "µg/m³", medidoEn: MEDIDO_EN },
    ],
  },
  {
    id: 3,
    nombre: "ATE",
    zona: "Lima Este",
    mediciones: [
      { parametro: "pm25", valor: 38, valorAnterior: 40, unidad: "µg/m³", medidoEn: MEDIDO_EN },
      { parametro: "so2", valor: 12, valorAnterior: 12, unidad: "µg/m³", medidoEn: MEDIDO_EN },
    ],
  },
  {
    id: 4,
    nombre: "SAN JUAN DE LURIGANCHO",
    zona: "Lima Este",
    mediciones: [{ parametro: "pm25", valor: 34, valorAnterior: 36, unidad: "µg/m³", medidoEn: MEDIDO_EN }],
  },
  {
    id: 5,
    nombre: "PUENTE PIEDRA",
    zona: "Lima Norte",
    mediciones: [
      { parametro: "pm25", valor: 29, valorAnterior: 30, unidad: "µg/m³", medidoEn: "2026-09-09T09:12:00Z" },
    ],
  },
];

/** Serie horaria agregada (promedio de estaciones) de las últimas 24 horas, para el gráfico PM2.5/PM10. */
export const SERIE_PM_MOCK: PuntoSerieHoraria[] = [
  { horaIso: "2026-09-08T15:00:00Z", pm25: 32, pm10: 48 },
  { horaIso: "2026-09-08T16:00:00Z", pm25: 30, pm10: 45 },
  { horaIso: "2026-09-08T17:00:00Z", pm25: 34, pm10: 50 },
  { horaIso: "2026-09-08T18:00:00Z", pm25: 41, pm10: 58 },
  { horaIso: "2026-09-08T19:00:00Z", pm25: 55, pm10: 68 },
  { horaIso: "2026-09-08T20:00:00Z", pm25: 68, pm10: 78 },
  { horaIso: "2026-09-08T21:00:00Z", pm25: 78, pm10: 84 },
  { horaIso: "2026-09-08T22:00:00Z", pm25: 74, pm10: 82 },
  { horaIso: "2026-09-08T23:00:00Z", pm25: 66, pm10: 79 },
  { horaIso: "2026-09-09T00:00:00Z", pm25: 58, pm10: 74 },
  { horaIso: "2026-09-09T01:00:00Z", pm25: 50, pm10: 70 },
  { horaIso: "2026-09-09T02:00:00Z", pm25: 45, pm10: 66 },
  { horaIso: "2026-09-09T03:00:00Z", pm25: 40, pm10: 62 },
  { horaIso: "2026-09-09T04:00:00Z", pm25: 38, pm10: 60 },
  { horaIso: "2026-09-09T05:00:00Z", pm25: 43, pm10: 63 },
  { horaIso: "2026-09-09T06:00:00Z", pm25: 52, pm10: 70 },
  { horaIso: "2026-09-09T07:00:00Z", pm25: 61, pm10: 76 },
  { horaIso: "2026-09-09T08:00:00Z", pm25: 70, pm10: 88 },
  { horaIso: "2026-09-09T09:00:00Z", pm25: 79, pm10: 96 },
  { horaIso: "2026-09-09T10:00:00Z", pm25: 72, pm10: 90 },
  { horaIso: "2026-09-09T11:00:00Z", pm25: 65, pm10: 84 },
  { horaIso: "2026-09-09T12:00:00Z", pm25: 58, pm10: 80 },
  { horaIso: "2026-09-09T13:00:00Z", pm25: 48, pm10: 78 },
  { horaIso: "2026-09-09T14:00:00Z", pm25: 41, pm10: 86 },
];
