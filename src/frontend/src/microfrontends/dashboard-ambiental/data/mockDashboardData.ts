import type { Alerta, ClimaResumen, EstacionResumen } from "../types/dashboard.types";

/**
 * Datos de ejemplo SOLO para maquetar la vista. Los valores respetan los
 * rangos físicos válidos que usa "Filtrar lecturas invalidas" en FLUJO A,
 * para que la maqueta se vea realista. Reemplazar por datos reales cuando
 * exista un webhook de lectura (ver nota en dashboard.types.ts).
 */
export const ESTACIONES_MOCK: EstacionResumen[] = [
  {
    id: 1,
    nombre: "SAN BORJA",
    zona: "Lima Centro",
    mediciones: [
      { parametro: "pm25", valor: 38, unidad: "ug/m3", medidoEn: "2026-08-19T09:00:00Z", nivel: "moderado" },
      { parametro: "pm10", valor: 61, unidad: "ug/m3", medidoEn: "2026-08-19T09:00:00Z", nivel: "moderado" },
      { parametro: "no2", valor: 22, unidad: "ug/m3", medidoEn: "2026-08-19T09:00:00Z", nivel: "bueno" },
      { parametro: "o3", valor: 18, unidad: "ug/m3", medidoEn: "2026-08-19T09:00:00Z", nivel: "bueno" },
    ],
  },
  {
    id: 2,
    nombre: "ATE",
    zona: "Lima Este",
    mediciones: [
      { parametro: "pm25", valor: 64, unidad: "ug/m3", medidoEn: "2026-08-19T09:00:00Z", nivel: "malo" },
      { parametro: "pm10", valor: 98, unidad: "ug/m3", medidoEn: "2026-08-19T09:00:00Z", nivel: "malo" },
      { parametro: "so2", valor: 12, unidad: "ug/m3", medidoEn: "2026-08-19T09:00:00Z", nivel: "bueno" },
    ],
  },
  {
    id: 3,
    nombre: "CALLAO",
    zona: "Callao",
    mediciones: [
      { parametro: "pm25", valor: 21, unidad: "ug/m3", medidoEn: "2026-08-19T09:00:00Z", nivel: "bueno" },
      { parametro: "co", valor: 410, unidad: "ug/m3", medidoEn: "2026-08-19T09:00:00Z", nivel: "bueno" },
    ],
  },
];

export const ALERTAS_MOCK: Alerta[] = [
  {
    id: "a1",
    nivel: "malo",
    parametro: "pm25",
    estacion: "ATE",
    mensaje: "PM2.5 superó el umbral saludable en las últimas 3 horas.",
  },
  {
    id: "a2",
    nivel: "moderado",
    parametro: "pm10",
    estacion: "SAN BORJA",
    mensaje: "PM10 en nivel moderado, monitorear tendencia.",
  },
];

export const CLIMA_MOCK: ClimaResumen = {
  temperaturaC: 19,
  humedadPct: 82,
  vientoKmh: 14,
  condicion: "Nublado",
};
