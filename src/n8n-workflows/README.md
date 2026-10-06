## Credenciales a configurar dentro de n8n (no en .env)

| Credencial | Tipo | Header |
|---|---|---|
| OpenAQ API Key | Header Auth | X-API-Key |
| Groq API Key | Header Auth | Authorization: Bearer <key> |
| Gemini API Key | Header Auth | x-goog-api-key |
| PostgreSQL - Escritura | Postgres | host: postgres, user: [nuevo] |
| PostgreSQL - Solo Lectura | Postgres | host: postgres, user: nlq_reader |



## SENAMHI — Snapshot de referencia para QA

**Propósito:** dato de contraste independiente para validar que el bot
no alucina (HU-03/CA5).
**Método:** captura manual (Excel copiado del sitio de SENAMHI).
**Estación:** Campo de Marte
**Parámetros capturados:** PM2.5, PM10, SO2, NO2, O3 (77 lecturas horarias c/u)
**Parámetro descartado:** CO — valor idéntico (3576.5) en todas las horas,
indicando un dato no confiable.
**Rango:** 29 de agosto - 2 de septiembre de 2026.
**Total de registros:** 385
**Aislamiento:** tabla `mediciones_referencia_qa`, separada de
`mediciones_aire`. Verificado que el Flujo B no la consulta.


## Workflow C — Endpoints de estaciones (Dashboard)

**Propósito:** exponer datos de solo lectura para el Dashboard Ambiental, sin depender del bot (Flujo B).
**Auth:** Header Auth (`X-API-Key`) + credencial Postgres `nlq_reader`.

### Endpoints
| Endpoint | Descripción |
|---|---|
| `GET /estaciones` | Última medición por estación (incluye `medidoEn`, `valorAnterior`, `zona`). |
| `GET /estaciones/serie-horaria` | Promedio horario de PM2.5/PM10, últimas 24h. |


**Ubicación:** `HU-23_Flujo_C_estaciones_corregido.json`

# Detección de Anomalías (Flujo A)

M�dulo que analiza automáticamente cada nueva medición de calidad del aire y determina si representa una anomalía, generando una explicación en lenguaje natural mediante IA.

## Cómo funciona

Tras cada ejecución de ingesta (Flujo A), el sistema:

1. **Calcula un z-score** por estación y contaminante, comparando el valor más reciente contra el promedio y desviación de los últimos 30 días (excluyendo el propio valor evaluado de esa línea base)
2. **Clasifica la severidad** con doble criterio:
   - **Alta** — el valor supera el límite legal (D.S. 003-2017-MINAM)
   - **Moderada** — el valor no supera la norma, pero se desvía significativamente (z-score > 2.5) de su propio historial
3. **Evita duplicados** — no vuelve a registrar la misma alerta si ya existe una para esa estación y contaminante dentro de la última hora
4. **Genera un análisis en lenguaje natural** (Groq, con Gemini como respaldo automático), describiendo únicamente la desviación numérica observada

## Por qué doble criterio, no solo estadístico

Se confirmó con un caso real que el z-score por sí solo no basta: una estación que opera crónicamente cerca del límite legal nunca se desviaría de "su propio normal" (z-score cercano a 0), aunque siga violando la norma. El criterio normativo atrapa estos casos que el estadístico no puede ver.

## Restricción de diseño en el análisis con IA

El modelo tiene prohibido explícitamente inventar causas externas (tráfico, incendios, clima) que no se le hayan dado como dato — solo describe la cifra observada. Esta restricción se definió tras detectar, en una maqueta del Dashboard, un ejemplo de alerta que atribuía una causa no verificada.

## Tabla involucrada

`alertas_anomalias` — expuesta al Dashboard a través del endpoint `GET /alertas` (Flujo C).

## Pendientes conocidos

- Normalización de unidades: `mediciones_aire.unidad` mezcla ppm/ppb/µg/m³ para un mismo contaminante — pendiente de resolver antes de confiar plenamente en la comparación contra los umbrales ECA-aire
- Probar el respaldo de Gemini forzando un fallo de Groq