/**
 * Registro único de microfrontends. El Sidebar y la página de Inicio (en
 * frontend-shell) leen de aquí. Cada `ruta` es absoluta porque, a
 * diferencia de una SPA con rutas internas, cada microfrontend es un
 * despliegue de Vercel independiente montado en esa ruta vía rewrites
 * (ver `vercel.json` de frontend-shell) — navegar entre ellos es una
 * recarga completa de página, no una transición de React Router.
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
      "Resumen por distrito con categoría ECA y tendencia, gráfico de PM2.5/PM10 de 24h, y alertas con sus factores.",
    icono: "📈",
    ruta: "/data-analytics",
    estado: "disponible",
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
  {
    id: "ajustes",
    nombre: "Ajustes",
    descripcion: "Preferencias de apariencia y accesibilidad de este dispositivo.",
    icono: "⚙️",
    ruta: "/ajustes",
    estado: "disponible",
  },
];
