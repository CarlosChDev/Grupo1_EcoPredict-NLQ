# Microfrontend: Data Analytics (HU-03 — Panel de Analítica Ambiental, Fase 1)

App independiente (Vite + React) que se monta en `/data-analytics` dentro
del dominio del shell (ver `src/frontend-shell`).

Reutiliza los **mismos webhooks de n8n (FLUJO C)** que ya consume
`dashboard-ambiental` — la HU-03 no crea flujos nuevos, solo una vista
distinta sobre los mismos datos:

- **Resumen por distrito** (`DistrictSummaryTable`): PM2.5, PM10, categoría
  ECA (peor nivel entre los parámetros medidos) e indicador de tendencia
  (▲/▼ contra la lectura anterior) por estación, vía `GET /estaciones`.
  > El esquema de `estaciones` no tiene un campo "distrito" — `zona` es el
  > tipo de área (`industrial`/`residencial`/`urbana`), no un distrito de
  > Lima. Esta tabla usa cada **estación** como proxy de la zona geográfica
  > que representa, que es la granularidad real que expone hoy el backend.
  > Si más adelante agregan un campo `distrito` real a `estaciones`, solo
  > hay que sumar esa columna aquí.
- **Gráfico de tendencia** (`PmTrendChart`): PM2.5/PM10 de las últimas 24h,
  vía `GET /estaciones/serie-horaria`.
- **Alertas y factores asociados** (`AlertsPanel`): `GET /alertas`. El
  campo `mensaje` de cada alerta **es** la columna `analisis_llm` de
  `alertas_anomalias` (o un mensaje generado si el LLM no escribió ninguno)
  — por eso ya "reutiliza analisis_llm" tal como pide la HU, sin necesitar
  un campo nuevo. Si no hay alertas, se muestra el estado vacío "Sin
  alertas activas.".

## Ejecutar en local

```bash
cp .env.example .env   # o usa el .env ya presente con los valores de OCI
npm install
npm run dev   # http://localhost:5178/data-analytics/
```

Para la experiencia integrada (Sidebar navegando entre módulos), usa
`npm run dev:all` desde la raíz del repo.

## Variables de entorno

Las mismas 3 que usa `dashboard-ambiental` (ver `.env.example`):
`VITE_N8N_ESTACIONES_WEBHOOK_URL`, `VITE_N8N_SERIE_HORARIA_WEBHOOK_URL`,
`VITE_N8N_ALERTAS_WEBHOOK_URL`, y opcionalmente `VITE_N8N_API_KEY`.

## Desplegar en Vercel

Proyecto nuevo → **Root Directory**: `src/microfrontends/data-analytics` →
Framework: Vite. Configura las variables de entorno de arriba en Vercel. La
URL asignada va en el rewrite `/data-analytics` de
`frontend-shell/vercel.json`.
