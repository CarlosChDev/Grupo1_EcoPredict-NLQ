# Microfrontend: NLQ Chat IA

App independiente (Vite + React) que se monta en `/nlq-chat` dentro del
dominio del shell (ver `src/frontend-shell`), vía `vercel.json` (rewrites en
producción) o el proxy de dev de `frontend-shell/vite.config.ts` (local).

Responsabilidad: capturar la pregunta del usuario, enviarla al webhook de
n8n (FLUJO B), mostrar la respuesta generada por IA y graficar la serie
histórica cuando la haya.

## Ejecutar en local

```bash
cp .env.example .env      # o usa el .env ya presente con valores de OCI
npm install
npm run dev               # http://localhost:5174/nlq-chat/ (nota la barra final)
```

Para ver la experiencia integrada (Sidebar navegando entre módulos) corre
`npm run dev:all` desde la raíz del repo en vez de este `npm run dev` suelto.

## Variables de entorno

- `VITE_N8N_WEBHOOK_URL` (requerida): webhook de FLUJO B.
- `VITE_N8N_API_KEY` (opcional): header `X-API-Key` si el webhook lo exige.

## Desplegar en Vercel

Proyecto nuevo → **Root Directory**: `src/microfrontends/nlq-chat` →
Framework: Vite. Configura las mismas variables de entorno de arriba en
Vercel (Project Settings → Environment Variables). La URL que Vercel asigne
a este proyecto es la que debe ir en el rewrite `/nlq-chat` de
`frontend-shell/vercel.json`.
