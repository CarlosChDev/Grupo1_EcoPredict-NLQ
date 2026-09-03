/**
 * Registro único de microfrontends. El Sidebar y la página de Inicio leen
 * de aquí — para agregar un microfrontend nuevo (Dashboard Ambiental, Data
 * Analytics) solo hace falta añadir una entrada y su ruta en `shell/App.tsx`.
 */
export interface MicrofrontendConfig {
  id: string;
  nombre: string;
  descripcion: string;
  icono: string;
  ruta: string;
  estado: "disponible" | "proximamente";
}

export const microfrontends: MicrofrontendConfig[] = [
  {
    id: "nlq-chat",
    nombre: "NLQ Chat IA",
    descripcion:
      "Pregunta en lenguaje natural por la calidad del aire y recibe una respuesta redactada por IA junto con su gráfico de la serie histórica.",
    icono: "💬",
    ruta: "/nlq-chat",
    estado: "disponible",
  },
  {
    id: "dashboard-ambiental",
    nombre: "Dashboard Ambiental",
    descripcion:
      "Indicadores de calidad del aire en tiempo real, alertas y estado meteorológico. Por ahora es solo vista: falta el webhook n8n de lectura.",
    icono: "📊",
    ruta: "/dashboard-ambiental",
    estado: "disponible",
  },
  {
    id: "data-analytics",
    nombre: "Data Analytics",
    descripcion:
      "Gráficos históricos, tendencias y comparación de zonas o periodos.",
    icono: "📈",
    ruta: "/data-analytics",
    estado: "proximamente",
  },
  {
    id: "estado-sistema",
    nombre: "Estado del Sistema",
    descripcion:
      "Diagnóstico técnico del webhook de Flujo B: latencia, código de respuesta y verificación automática.",
    icono: "⚡",
    ruta: "/estado-sistema",
    estado: "disponible",
  },
];
