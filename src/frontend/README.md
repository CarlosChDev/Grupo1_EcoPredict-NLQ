# Frontend — Shell + Microfrontends

Aplicación única (Vite + React + TypeScript) organizada como **Shell/Host +
microfrontends**, tal como se definió en el informe de arquitectura. No es
un monorepo con paquetes separados: es una sola app con carpetas
independientes por responsabilidad, y cada microfrontend se carga en su
propio chunk JS mediante `React.lazy` (code-splitting), sin necesitar
varios servidores de desarrollo.

## Estructura

```text
src/
├── main.tsx                      # punto de entrada
├── styles/
│   └── global.css                # tokens de diseño (colores, tipografía) + reset
│
├── shell/                        # Shell/Host: navegación, layout, integración
│   ├── App.tsx                   # define las rutas y qué microfrontend carga cada una
│   ├── config/
│   │   └── microfrontends.ts     # registro único: id, nombre, ruta, estado
│   ├── layout/
│   │   ├── AppLayout.tsx         # Sidebar + Topbar + <Outlet/>
│   │   ├── Sidebar.tsx
│   │   ├── Topbar.tsx
│   │   └── usePageHeader.ts      # hook para que cada página fije título/subtítulo
│   └── pages/
│       ├── InicioPage.tsx        # landing: tarjetas para entrar a cada microfrontend
│       └── NotFoundPage.tsx
│
└── microfrontends/
    ├── nlq-chat/                 # Microfrontend: NLQ Chat IA — funcional
    │   ├── NlqChatPage.tsx       # punto de entrada del módulo
    │   ├── components/
    │   │   ├── ChatInput.tsx
    │   │   ├── ChatMessageItem.tsx
    │   │   └── DynamicVisualization.tsx  # gráfico (Chart.js) de la serie histórica
    │   ├── hooks/
    │   │   └── useNlqChat.ts     # estado del chat + llamada al webhook
    │   ├── services/
    │   │   └── nlqApi.ts         # fetch tipado al webhook de n8n (FLUJO B)
    │   └── types/
    │       └── nlq.types.ts      # tipos que reflejan el contrato de FLUJO B.json
    │
    ├── dashboard-ambiental/      # Microfrontend: Dashboard Ambiental — SOLO VISTA
    │   ├── DashboardAmbientalPage.tsx
    │   ├── components/
    │   │   ├── AirQualityCard.tsx
    │   │   ├── PollutionIndicator.tsx
    │   │   ├── WeatherSummary.tsx
    │   │   └── AlertsPanel.tsx
    │   ├── data/
    │   │   └── mockDashboardData.ts   # datos de ejemplo — no hay fetch real todavía
    │   ├── utils/
    │   │   └── nivel.ts
    │   └── types/
    │       └── dashboard.types.ts     # calzan con `estaciones`/`mediciones_aire`
    │
    └── estado-sistema/           # Microfrontend: Estado del Sistema — funcional
        ├── EstadoSistemaPage.tsx
        ├── components/
        │   ├── WebhookStatusCard.tsx      # latencia, código HTTP, X-API-Key, botón manual
        │   ├── EnvironmentPanel.tsx       # toggle Local / Producción (OCI)
        │   ├── LastCheckPanel.tsx         # última verificación exitosa
        │   └── HistoryPanel.tsx           # últimas 50 verificaciones
        ├── hooks/
        │   └── useWebhookStatus.ts   # orquesta ping manual, auto-check y entorno activo
        ├── services/
        │   └── statusApi.ts          # cliente HTTP: ping real (con IA) vs reachability (sin IA)
        ├── types/
        │   └── status.types.ts
        └── utils/
            ├── estado.ts              # labels/colores por estado y tipo de ping
            └── historial.ts           # persistencia del historial en localStorage
```

> **Dashboard Ambiental es solo maqueta visual.** `FLUJO A.json` únicamente
> inserta en Postgres (`estaciones`, `mediciones_aire`); no existe todavía
> un webhook n8n que exponga esos datos por HTTP. La página muestra un
> banner de aviso y consume `data/mockDashboardData.ts`. Cuando exista ese
> webhook de lectura, se agrega un `services/dashboardApi.ts` igual que
> `nlq-chat/services/nlqApi.ts` y se reemplazan los imports `*_MOCK`.

## Estado del Sistema

Diagnóstico técnico del webhook de Flujo B, para saber si el problema es el
frontend, n8n o el modelo de IA sin adivinar. Dos tipos de chequeo, porque
un ping real gasta cuota del modelo:

- **Reachability** (automático cada 5 min, y al entrar a la página): manda
  un payload sin `pregunta`. El nodo "Validar entrada" de Flujo B lo
  rechaza con `400` en ~50-100ms, sin llegar al nodo de IA. Solo confirma
  que n8n + el workflow están vivos.
- **Real** (botón "Probar conexión ahora", manual): manda una pregunta fija
  de verdad, dispara el nodo de IA y mide la latencia real (puede tardar
  varios segundos). Úsalo cuando quieras confirmar que el modelo también
  responde, no solo que el servidor está arriba.

El panel **Entorno** deja elegir entre **Local** (`VITE_N8N_WEBHOOK_URL`) y
**Producción** (`VITE_N8N_WEBHOOK_URL_PROD`, opcional) para diagnosticar
cualquiera de los dos sin cambiar el `.env`. El **Historial** guarda las
últimas 50 verificaciones en `localStorage` del navegador (hora, entorno,
tipo de ping, estado, latencia, código HTTP) — es diagnóstico local de
quien lo mira, no un dato compartido del backend.

**Pendiente:** no incluye maqueta de Figma/HTML como artefacto de diseño
separado (se implementó directo en React a partir de una captura de
referencia).

**Cómo agregar el próximo microfrontend** (Data Analytics): crear
`src/microfrontends/<nombre>/`, agregarlo a `shell/config/microfrontends.ts`
con `estado: "disponible"`, y sumar su ruta en `shell/App.tsx` con
`lazy()`. El Sidebar y la página de Inicio se actualizan solos porque leen
del mismo registro.

## Requisitos previos

1. Levantar la infraestructura local (Postgres + n8n):

   ```bash
   cd infrastructure
   docker compose up -d
   ```

2. Entrar a n8n en <http://localhost:5678> e importar/activar el workflow
   **FLUJO B** (`src/n8n-workflows/FLUJO B.json`). Actívalo con el toggle
   **Active**; queda escuchando en:

   ```text
   http://localhost:5678/webhook/nlq
   ```

## Ejecutar el frontend

```bash
cd src/frontend
cp .env.example .env      # ajusta VITE_N8N_WEBHOOK_URL si hace falta
npm install
npm run dev
```

`VITE_N8N_API_KEY` y `VITE_N8N_WEBHOOK_URL_PROD` son opcionales — solo
hacen falta si el webhook exige un header `X-API-Key`, o si quieres probar
el toggle "Producción" de Estado del Sistema apuntando a un n8n desplegado
en la nube. Ver comentarios en `.env.example`.

Abre <http://localhost:5173>. Verás la página de **Inicio** con las
tarjetas de los cuatro módulos: **NLQ Chat IA**, **Dashboard Ambiental**
(solo maqueta) y **Estado del Sistema** están habilitados; **Data
Analytics** sigue como "Próximamente" (coincide con la Lista de Chequeo
del informe).

## Contrato del webhook NLQ

Request:

```json
{ "pregunta": "string, 5-500 caracteres" }
```

Respuestas posibles (ver `src/n8n-workflows/FLUJO B.json` y
`microfrontends/nlq-chat/types/nlq.types.ts`):

- `200` con datos: `{ ok, codigo_http, texto, modelo_usado, parametro, rango, serie }`
- `200` sin datos: `{ ok, codigo_http, mensaje, sugerencia }`
- `400`: `{ ok: false, codigo_http: 400, errores: string[] }`
- `422`: `{ ok: false, codigo_http: 422, motivo }`

## Troubleshooting

- **`Failed to fetch` / error de red**: confirma que el contenedor de n8n
  está corriendo (`docker ps`) y que `VITE_N8N_WEBHOOK_URL` en `.env`
  apunta al puerto correcto.
- **404 en `/webhook/nlq`** (`"the workflow must be active"`): el workflow
  FLUJO B no está activado — toggle **Active** en la esquina superior
  derecha del editor de n8n.
- **Funciona por `curl`/SSH pero no en el navegador de un despliegue en la
  nube**: `VITE_N8N_WEBHOOK_URL` probablemente apunta a `localhost`. Ese
  valor se hornea en el JS que corre en el navegador de **cada visitante**,
  no en el servidor — "localhost" ahí es la propia PC del visitante. Debe
  ser la IP/dominio público donde vive n8n (ej.
  `http://<ip-publica>:5678/webhook/nlq`), y el proceso del frontend debe
  reiniciarse para releer el `.env` (Vite solo lo lee al arrancar).
- **`blocked by CORS policy` en la consola del navegador**: n8n no está
  devolviendo `Access-Control-Allow-Origin` para el origen del frontend.
  En el editor de n8n, abre el nodo del Webhook → **Options** → agrega
  **"Allowed Origins (CORS)"** con `*` o la URL exacta del frontend. Pasa
  sobre todo con despliegues donde frontend y n8n están en distinto
  puerto/dominio (son orígenes distintos aunque compartan IP).
- **El chat NLQ "no responde" tras dejar Estado del Sistema abierto en
  background**: el chequeo automático de Estado del Sistema es liviano
  (no gasta cuota de IA, ver sección de arriba) — si aun así el chat falla
  con "cuerpo que no es JSON válido", probablemente el proveedor del
  modelo (Gemini/Groq) está limitando por rate limit; reintenta en unos
  segundos.
