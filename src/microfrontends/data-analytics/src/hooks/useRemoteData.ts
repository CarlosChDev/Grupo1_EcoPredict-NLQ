import { useCallback, useEffect, useState } from "react";
import { DataAnalyticsApiError } from "../services/dataAnalyticsApi";

export type EstadoRemoto<T> =
  | { tipo: "cargando" }
  | { tipo: "error"; mensaje: string }
  | { tipo: "listo"; datos: T };

/**
 * Carga `cargar` cada vez que cambia `clave` (y al llamar a `reintentar`).
 * Cancela la petición anterior para que una respuesta lenta no pise a la
 * más reciente al cambiar rápido de periodo o distrito.
 */
export function useRemoteData<T>(
  cargar: ((signal: AbortSignal) => Promise<T>) | null,
  clave: string,
): [EstadoRemoto<T>, () => void] {
  const [estado, setEstado] = useState<EstadoRemoto<T>>({ tipo: "cargando" });
  const [intento, setIntento] = useState(0);

  useEffect(() => {
    if (!cargar) return;
    const control = new AbortController();
    setEstado({ tipo: "cargando" });

    cargar(control.signal)
      .then((datos) => {
        if (!control.signal.aborted) setEstado({ tipo: "listo", datos });
      })
      .catch((err) => {
        if (control.signal.aborted) return;
        const mensaje = err instanceof DataAnalyticsApiError ? err.message : "Error inesperado al cargar los datos.";
        setEstado({ tipo: "error", mensaje });
      });

    return () => control.abort();
    // `cargar` se recrea en cada render; `clave` resume sus dependencias.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clave, intento]);

  const reintentar = useCallback(() => setIntento((i) => i + 1), []);
  return [estado, reintentar];
}
