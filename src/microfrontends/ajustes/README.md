# Microfrontend: Ajustes

App independiente (Vite + React) que se monta en `/ajustes` dentro del
dominio del shell (ver `src/frontend-shell`).

Cubre las preferencias que `@ecopredict/ui-shell` aplica de verdad: tema,
densidad, vista de inicio, alto contraste y reducir movimiento. No requiere
variables de entorno.

## Ejecutar en local

```bash
npm install
npm run dev   # http://localhost:5177/ajustes/
```

Para la experiencia integrada, usa `npm run dev:all` desde la raíz del repo.

## Desplegar en Vercel

Proyecto nuevo → **Root Directory**: `src/microfrontends/ajustes` →
Framework: Vite. La URL asignada va en el rewrite `/ajustes` de
`frontend-shell/vercel.json`.
