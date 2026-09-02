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