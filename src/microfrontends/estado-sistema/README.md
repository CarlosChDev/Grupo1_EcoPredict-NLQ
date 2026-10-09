# Microfrontend: Estado del Sistema

App independiente (Vite + React) que se monta en `/estado-sistema` dentro
del dominio del shell (ver `src/frontend-shell`).

Diagnóstico técnico del webhook de Flujo B: cada "Probar conexión" (manual
o automática cada 5 min) dispara el flujo con una pregunta fija y mide
latencia/status reales.

## Ejecutar en local

```bash
cp .env.example .env
npm install
npm run dev   # http://localhost:5176/estado-sistema/
```

Para la experiencia integrada, usa `npm run dev:all` desde la raíz del repo.

## Desplegar en Vercel

Proyecto nuevo → **Root Directory**: `src/microfrontends/estado-sistema` →
Framework: Vite. Configura las variables de entorno de `.env.example` en
Vercel. La URL asignada va en el rewrite `/estado-sistema` de
`frontend-shell/vercel.json`.
