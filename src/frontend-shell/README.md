# Frontend Shell

Landing (`/`) del sistema. Es un despliegue de Vercel **independiente**
del resto de microfrontends (`src/microfrontends/*`): solo contiene la
página de Inicio, la de 404, y — vía `vercel.json` — los `rewrites` que
enrutan `/nlq-chat`, `/dashboard-ambiental`, `/estado-sistema` y `/ajustes`
hacia los despliegues de Vercel de cada uno de esos microfrontends. Para el
visitante todo vive en un solo dominio; para el equipo son 5 proyectos de
Vercel que se despliegan por separado.

El layout compartido (Sidebar/Topbar), el tema y las preferencias del
usuario viven en el paquete de workspace `@ecopredict/ui-shell`
(`packages/ui-shell`), del que este proyecto y cada microfrontend dependen.

## Ejecutar en local

Necesita el resto de microfrontends corriendo en sus puertos fijos para que
la navegación del Sidebar funcione (el `server.proxy` de `vite.config.ts`
replica en local los mismos `rewrites` que usa Vercel en producción):

```bash
# desde la raíz del repo
npm install
npm run dev:all
```

O por separado:

```bash
cd src/frontend-shell
npm install
npm run dev        # http://localhost:5173
```

## Desplegar en Vercel

1. Crear un proyecto nuevo en vercel.com apuntando a este repo.
2. **Root Directory**: `src/frontend-shell`.
3. Framework preset: Vite (detectado automático). Build command / Output
   directory por defecto (`npm run build` / `dist`) están bien.
4. Repetir esto para cada microfrontend en `src/microfrontends/*`
   (ver el README de cada uno) **antes** de confirmar las URLs de abajo.
5. Una vez creados los 5 proyectos, actualizar los `destination` de
   `vercel.json` con las URLs reales que Vercel asignó a cada proyecto
   (por defecto `<nombre-del-proyecto>.vercel.app`; los nombres usados aquí
   son placeholders: `ecopredict-nlq-chat`, `ecopredict-dashboard-ambiental`,
   `ecopredict-estado-sistema`, `ecopredict-ajustes`, `ecopredict-data-analytics`).

Como el repo usa npm workspaces, Vercel instala dependencias desde la raíz
del repo (detecta el `package.json`/`package-lock.json` raíz) aunque el
"Root Directory" del proyecto sea un subdirectorio — así `@ecopredict/ui-shell`
se resuelve sin necesidad de publicarlo a ningún registro.
