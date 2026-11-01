import type {
  ComparativoResponse,
  DiasPeriodo,
  DistritosResponse,
  ParametroAnalitica,
  PatronHorarioResponse,
  RankingEcaResponse,
  ResumenIaResponse,
} from "../types/analytics.types";

const BASE_URL = import.meta.env.VITE_N8N_ANALITICA_BASE_URL?.replace(/\/+$/, "");
const API_KEY = import.meta.env.VITE_N8N_API_KEY;

export class DataAnalyticsApiError extends Error {}

type Parametros = Record<string, string | number>;

/** Ruta legible del endpoint (sin host), para el pie de cada bloque. */
export function describirEndpoint(ruta: string, parametros: Parametros = {}): string {
  const query = new URLSearchParams(Object.entries(parametros).map(([k, v]) => [k, String(v)])).toString();
  // URLSearchParams escapa las comas; se dejan legibles en la vista.
  return `GET /analitica/${ruta}${query ? `?${query.replace(/%2C/g, ",")}` : ""}`;
}

async function pedirJson<T>(
  ruta: string,
  parametros: Parametros,
  mensajeErrorGenerico: string,
  signal?: AbortSignal,
): Promise<T> {
  if (!BASE_URL) {
    throw new DataAnalyticsApiError("VITE_N8N_ANALITICA_BASE_URL no está configurada. Revisa el archivo .env.");
  }

  const url = new URL(`${BASE_URL}/${ruta}`);
  for (const [clave, valor] of Object.entries(parametros)) url.searchParams.set(clave, String(valor));

  const headers: Record<string, string> = {};
  if (API_KEY) headers["X-API-Key"] = API_KEY;

  let res: Response;
  try {
    res = await fetch(url, { headers, signal });
  } catch (err) {
    if (signal?.aborted) throw err;
    throw new DataAnalyticsApiError("No se pudo contactar al webhook de n8n.");
  }

  let json: unknown;
  try {
    json = await res.json();
  } catch {
    throw new DataAnalyticsApiError(
      res.ok ? "El webhook respondió con un cuerpo que no es JSON válido." : `${mensajeErrorGenerico} (${res.status})`,
    );
  }

  const cuerpo = json as { ok?: boolean; mensaje?: string } | null;
  if (!res.ok || cuerpo?.ok === false) {
    const sufijo = res.ok ? "" : ` (${res.status})`;
    throw new DataAnalyticsApiError(`${cuerpo?.mensaje ?? mensajeErrorGenerico}${sufijo}`);
  }

  return json as T;
}

/** Ver el flujo de analítica en n8n (`/webhook/analitica/...`). */
export function obtenerDistritos(signal?: AbortSignal): Promise<DistritosResponse> {
  return pedirJson("distritos", {}, "Error al consultar los distritos.", signal);
}

export function obtenerComparativo(
  distritos: string[],
  dias: DiasPeriodo,
  signal?: AbortSignal,
): Promise<ComparativoResponse> {
  return pedirJson(
    "comparativo",
    { distritos: distritos.join(","), dias },
    "Error al consultar el comparativo entre distritos.",
    signal,
  );
}

export function obtenerRankingEca(
  parametro: ParametroAnalitica,
  dias: DiasPeriodo,
  signal?: AbortSignal,
): Promise<RankingEcaResponse> {
  return pedirJson("ranking-eca", { parametro, dias }, "Error al consultar el ranking de excedencias.", signal);
}

export function obtenerPatronHorario(
  distrito: string,
  parametro: ParametroAnalitica,
  dias: DiasPeriodo,
  signal?: AbortSignal,
): Promise<PatronHorarioResponse> {
  return pedirJson(
    "patron-horario",
    { distrito, parametro, dias },
    "Error al consultar el patrón horario.",
    signal,
  );
}

/** El webhook acepta un solo distrito por llamada. */
export function obtenerResumenIa(distrito: string, signal?: AbortSignal): Promise<ResumenIaResponse> {
  return pedirJson("resumen-ia", { distrito }, "Error al consultar el resumen de la semana.", signal);
}
