# Microfrontend: Dashboard Ambiental

App independiente (Vite + React) que se monta en `/dashboard-ambiental`
dentro del dominio del shell (ver `src/frontend-shell`).

Consume los webhooks de n8n de FLUJO C: última medición por estación
(`VITE_N8N_ESTACIONES_WEBHOOK_URL`), serie horaria de PM2.5/PM10
(`VITE_N8N_SERIE_HORARIA_WEBHOOK_URL`) y alertas del sistema
(`VITE_N8N_ALERTAS_WEBHOOK_URL`).

## Ejecutar en local

```bash
cp .env.example .env
npm install
npm run dev   # http://localhost:5175/dashboard-ambiental/
```

Para la experiencia integrada, usa `npm run dev:all` desde la raíz del repo.

## Desplegar en Vercel

Proyecto nuevo → **Root Directory**: `src/microfrontends/dashboard-ambiental`
→ Framework: Vite. Configura las variables de entorno de `.env.example` en
Vercel. La URL asignada va en el rewrite `/dashboard-ambiental` de
`frontend-shell/vercel.json`.
