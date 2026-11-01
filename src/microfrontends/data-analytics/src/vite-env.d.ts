/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Base de los webhooks del flujo de analítica, p.ej. http://host/webhook/analitica */
  readonly VITE_N8N_ANALITICA_BASE_URL?: string;
  readonly VITE_N8N_API_KEY?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
