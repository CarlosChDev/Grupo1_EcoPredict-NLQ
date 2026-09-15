/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_N8N_WEBHOOK_URL: string;
  readonly VITE_N8N_API_KEY?: string;
  readonly VITE_N8N_WEBHOOK_URL_PROD?: string;
  readonly VITE_N8N_ESTACIONES_WEBHOOK_URL?: string;
  readonly VITE_N8N_SERIE_HORARIA_WEBHOOK_URL?: string;
  readonly VITE_N8N_ALERTAS_WEBHOOK_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
