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
    └── dashboard-ambiental/      # Microfrontend: Dashboard Ambiental — SOLO VISTA
        ├── DashboardAmbientalPage.tsx
        ├── components/
        │   ├── AirQualityCard.tsx
        │   ├── PollutionIndicator.tsx
        │   ├── WeatherSummary.tsx
        │   └── AlertsPanel.tsx
        ├── data/
        │   └── mockDashboardData.ts   # datos de ejemplo — no hay fetch real todavía
        ├── utils/
        │   └── nivel.ts
        └── types/
            └── dashboard.types.ts     # calzan con `estaciones`/`mediciones_aire`
```

> **Dashboard Ambiental es solo maqueta visual.** `FLUJO A.json` únicamente
> inserta en Postgres (`estaciones`, `mediciones_aire`); no existe todavía
> un webhook n8n que exponga esos datos por HTTP. La página muestra un
> banner de aviso y consume `data/mockDashboardData.ts`. Cuando exista ese
> webhook de lectura, se agrega un `services/dashboardApi.ts` igual que
> `nlq-chat/services/nlqApi.ts` y se reemplazan los imports `*_MOCK`.

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

Abre <http://localhost:5173>. Verás la página de **Inicio** con las
tarjetas de los tres módulos; solo **NLQ Chat IA** está habilitado, los
otros dos aparecen como "Próximamente" (coincide con la Lista de Chequeo
del informe: Dashboard Ambiental y Data Analytics siguen pendientes).

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
- **404 en `/webhook/nlq`**: el workflow FLUJO B no está activado.
