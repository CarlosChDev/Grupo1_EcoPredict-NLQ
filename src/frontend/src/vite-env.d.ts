/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_N8N_WEBHOOK_URL: string;
  readonly VITE_N8N_API_KEY?: string;
  readonly VITE_N8N_WEBHOOK_URL_PROD?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
