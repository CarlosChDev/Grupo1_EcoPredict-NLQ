# Microfrontend: Data Analytics (HU-23 — Panel de Analítica Ambiental, Fase 2)

App independiente (Vite + React) que se monta en `/data-analytics` dentro
del dominio del shell (ver `src/frontend-shell`).

Histórico y comparación entre distritos — para el estado actual está el
Dashboard Ambiental. Consume los webhooks del **flujo de analítica** en n8n
(`/webhook/analitica/...`). Cada bloque pide sus propios datos, así que si
uno falla los demás siguen funcionando:

| Bloque | Componente | Webhook |
| --- | --- | --- |
| Lista de distritos (chips, selector) | `DataAnalyticsPage` | `GET /distritos` |
| 1. Comparativo entre distritos (2 a 4) | `DistrictComparison` | `GET /comparativo?distritos=ate,santa-anita&dias=7` |
| 2. Ranking de excedencias del ECA | `EcaRanking` | `GET /ranking-eca?parametro=pm25&dias=7` |
| 3. Patrón horario | `HourlyPattern` | `GET /patron-horario?distrito=ate&parametro=pm25&dias=7` |
| 4. Resumen interpretativo (IA) | `WeeklyAiSummary` | `GET /resumen-ia?distrito=ate` (una llamada por distrito) |

- El selector **Últimos 7 / 30 días** afecta a los bloques 1 a 3; el
  resumen de IA siempre es de la última semana generada.
- Los distritos con pocos datos (`datosSuficientes7/30 = false`) se
  muestran con borde punteado y se pueden elegir igual; el comparativo
  indica "Sin datos suficientes" en su tarjeta.
- Si `patron-horario` devuelve `datosSuficientes: false`, el gráfico
  muestra las horas que sí tienen dato, pero no calcula la hora crítica.
- Los gráficos son SVG propios (sin Chart.js) para cortar la línea en los
  días/horas sin dato.

## Ejecutar en local

```bash
cp .env.example .env   # y completa VITE_N8N_API_KEY
npm install
npm run dev   # http://localhost:5178/data-analytics/
```

Para la experiencia integrada (Sidebar navegando entre módulos), usa
`npm run dev:all` desde la raíz del repo.

## Variables de entorno

- `VITE_N8N_ANALITICA_BASE_URL`: base de los webhooks, p.ej.
  `http://144.22.203.51/webhook/analitica`. Usa el nginx del puerto 80
  (agrega CORS); el puerto 5678 de n8n no está expuesto.
- `VITE_N8N_API_KEY`: valor del header `X-API-Key` que exige n8n.

## Desplegar en Vercel

Proyecto nuevo → **Root Directory**: `src/microfrontends/data-analytics` →
Framework: Vite. Configura las variables de entorno de arriba en Vercel. La
URL asignada va en el rewrite `/data-analytics` de
`frontend-shell/vercel.json`.
