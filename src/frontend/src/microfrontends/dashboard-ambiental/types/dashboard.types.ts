/**
 * Tipos de vista para Dashboard Ambiental.
 *
 * IMPORTANTE: todavía no existe un webhook n8n que exponga estos datos
 * (FLUJO A solo INSERTA en `estaciones`/`mediciones_aire`, no expone
 * lectura por HTTP — ver src/n8n-workflows/FLUJO A.json). Estas formas
 * están pensadas para calzar 1:1 con esas tablas cuando ese webhook
 * exista; mientras tanto la página consume `data/mockDashboardData.ts`.
 */

export type ParametroCalidadAire = "pm25" | "pm10" | "no2" | "so2" | "o3" | "co";

export type NivelEstado = "bueno" | "moderado" | "malo";

export interface MedicionParametro {
  parametro: ParametroCalidadAire;
  valor: number;
  unidad: string;
  medidoEn: string;
  nivel: NivelEstado;
}

export interface EstacionResumen {
  id: number;
  nombre: string;
  zona: string | null;
  mediciones: MedicionParametro[];
}

export interface Alerta {
  id: string;
  nivel: NivelEstado;
  parametro: ParametroCalidadAire;
  estacion: string;
  mensaje: string;
}

/**
 * Aún no hay ninguna fuente meteorológica conectada (Figura 1 del informe
 * menciona SENAMHI como fuente futura, pero ningún flujo n8n la ingiere
 * todavía). Estructura provisional para no bloquear la maqueta visual.
 */
export interface ClimaResumen {
  temperaturaC: number;
  humedadPct: number;
  vientoKmh: number;
  condicion: string;
}
