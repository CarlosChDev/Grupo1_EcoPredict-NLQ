# Frontend — Scaffold NLQ

Prueba de concepto mínima: un input de lenguaje natural que llama directamente
al webhook local de n8n (`HU-04 · Flujo base NLQ`). Su único objetivo es
validar la comunicación frontend ↔ backend antes de construir la interfaz
definitiva — no está pensado como UI final.

Stack: Vite + React + TypeScript.

## Requisitos previos

1. Levantar la infraestructura local (Postgres + n8n):

   ```bash
   cd infrastructure
   docker compose up -d
   ```

2. Entrar a n8n en <http://localhost:5678> y crear la cuenta owner (solo la
   primera vez).

3. Importar el workflow base si no está ya en el editor:
   `src/n8n-workflows/templates/flujo-n8n-base.json` (menú **⋮ → Import from
   File**).

4. **Activar el workflow** con el toggle **Active** (arriba a la derecha).
   Esto deja el webhook escuchando de forma permanente en:

   ```text
   http://localhost:5678/webhook/nlq
   ```

   Alternativa mientras se edita el workflow sin activarlo: usar la ruta de
   prueba `http://localhost:5678/webhook-test/nlq`, pero hay que pulsar
   **"Listen for test event"** en el nodo Webhook antes de cada llamada (solo
   responde a una petición por click).

## Ejecutar el frontend

```bash
cd src/frontend
cp .env.example .env      # ajusta VITE_N8N_WEBHOOK_URL si hace falta
npm install
npm run dev
```

Abre <http://localhost:5173>, escribe una pregunta, elige ciudad/parámetro y
pulsa "Enviar al webhook". La respuesta cruda del workflow (JSON) se muestra
debajo del formulario — sirve para confirmar que el viaje
`input → fetch → n8n → Postgres/validación → respuesta` funciona de punta a
punta.

## Payload esperado por el webhook

```json
{
  "pregunta": "string, 5-500 caracteres",
  "ciudad": "string (default: Lima)",
  "parametro": "pm25 | pm10 | no2 | so2 | o3 | co"
}
```

El nodo "Validar y parsear consulta" del workflow devuelve `codigo_http: 400`
y una lista de `errores` si el payload no cumple estas reglas.

## Troubleshooting

- **`Failed to fetch` / error de red**: confirma que el contenedor `aire_n8n`
  está corriendo (`docker ps`) y que `VITE_N8N_WEBHOOK_URL` en `.env` apunta al
  puerto correcto.
- **404 en `/webhook/nlq`**: el workflow no está activado. Actívalo o cambia
  la URL a la ruta de prueba (`/webhook-test/nlq`) y pulsa "Listen for test
  event" antes de reenviar.
- **Error de CORS en la consola del navegador**: el nodo Webhook de n8n
  responde `Access-Control-Allow-Origin` automáticamente para el origen que
  hace la petición, así que no debería ocurrir en local. Si aparece, revisa
  que no haya un proxy/reverse-proxy intermedio quitando esa cabecera.
