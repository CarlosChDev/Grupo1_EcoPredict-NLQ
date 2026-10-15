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
## Consultas ambiguas con RAG y pgvector (HU-02)

El bot responde preguntas de **normativa** (por ejemplo, «¿es peligroso este nivel de PM2.5?») buscando en una base de conocimiento verificada, en lugar de depender de lo que el modelo recuerde. El RAG se usa **solo en normativa**: en la evaluación fue donde aportó, y en lugares la lista fija funcionó mejor (ver resultados).

### Qué se vectoriza

La tabla `documentos_rag` guarda conocimiento revisado: el catálogo de estaciones y zonas, y la normativa ECA para aire (D.S. 003-2017-MINAM). Cada fila tiene su embedding de 768 dimensiones (`gemini-embedding-001`) y un índice HNSW por distancia coseno. Se descartó vectorizar `logs_consultas_nlq`, porque son respuestas anteriores que nadie verificó y de las que nada dependía.

### Cómo responde el Flujo B

1. El paso de intención clasifica la pregunta como `datos` o `normativa`. Si hay duda, se trata como `datos`.
2. Si es de normativa, se vectoriza la pregunta y se traen los **cinco candidatos** más cercanos por coseno.
3. Un modelo selector (Groq, con Gemini de respaldo) elige cuál responde la pregunta, o contesta «ninguna».
4. El sistema valida que el id elegido esté entre los candidatos y responde **citando la fuente**. Si no hay candidato, el bot dice que no tiene el dato en vez de citar una norma equivocada.

Los lugares (estaciones y zonas) no usan RAG: se resuelven con una lista de zonas, nombres de estación y alias.

### Seguridad y continuidad

- El modelo **nunca genera SQL**. Las consultas son sentencias fijas con parámetros.
- El Flujo B las ejecuta con el rol `nlq_reader`, que solo tiene permiso de lectura sobre `documentos_rag`.
- Si falla la vectorización de la pregunta, el flujo reintenta tres veces y luego sigue por un camino alterno.

### Componentes

- **Migración:** `src/database/migrations/003_pgvector_rag.sql` (extensión `vector`, tabla `documentos_rag` e índices). La base pasó de `postgres:16-alpine` a `pgvector/pgvector:pg16-bookworm`; antes del cambio se hizo un respaldo completo con `pg_dumpall` y se ensayó todo en un contenedor aparte.
- **Workflow de vectorización (n8n):** lee las filas sin vector, genera el embedding con Gemini y guarda el vector. Corre una vez al día, no en tiempo real.
- **Evaluación:** scripts y datos en `src/evaluation/rag/`.

### Resultados de la evaluación

| Tipo de consulta | Método | Aciertos | Falsos aceptados |
|---|---|---|---|
| Lugares | Lista fija | 24 de 25 | 0 de 56 |
| Lugares | RAG sin piso de similitud | — | 56 de 56 |
| Lugares | RAG con piso 0,65 | — | 32 de 56 |
| Normativa | Solo similitud | 27 de 27 | 12 de 32 |
| Normativa | RAG + selector | 24 de 27 | 2 de 32 |

«Falsos aceptados» son preguntas sin respuesta posible que el sistema aceptó igual. Ningún umbral de similitud separó bien los aciertos de los errores, por eso en normativa se usa el selector, a costa de 3 aciertos de 27.

**Limitación:** las preguntas de evaluación las generó una IA o las escribieron compañeros de sistemas. Los resultados apoyan el diseño, pero falta confirmarlo con preguntas de ciudadanos reales.


## Observabilidad de la IA con Langfuse 

Cada llamada a Groq y Gemini en los Flujos A y B queda registrada en [Langfuse](https://langfuse.com) con su modelo, tokens, latencia, costo, prompt, respuesta y error. Así se puede ver cuánto gasta y cuánto tarda la IA, y saber si un fallo vino del modelo principal (Groq) o del de respaldo (Gemini).

### Cómo funciona

n8n no tiene integración nativa con Langfuse, así que las llamadas se envían por OpenTelemetry (OTLP/HTTP con JSON) a Langfuse Cloud, región US. Todo pasa por un único sub-workflow:

- **`Langfuse - registrar.json`**: sub-workflow que recibe los datos de una llamada, arma el registro OTLP y lo envía a Langfuse.
- **`Workflow A v4.json`**: Flujo A con el registro del análisis de anomalías.
- **`Workflow B V5.json`**: Flujo B con el registro de la intención, el embedding de la pregunta, el selector del RAG y la respuesta.

En cada flujo, los nodos `LF · …` salen en una rama lateral desde el nodo de Groq (salida correcta y de error) y desde el de Gemini. Todos desembocan en un nodo Execute Workflow, «Registrar en Langfuse», que llama al sub-workflow.

### Qué se registra

| Paso | Flujo | Proveedor principal → respaldo |
|---|---|---|
| `intencion` | B | Groq → Gemini |
| `rag_embedding` | B | Gemini (sin respaldo) |
| `rag_eleccion` | B | Groq → Gemini |
| `respuesta` | B | Groq → Gemini |
| `analisis_anomalia` | A | Groq → Gemini |

- Todas las llamadas de una misma ejecución de n8n quedan en una sola traza («Flujo A» o «Flujo B»).
- Si una llamada falla, queda con nivel `ERROR` y el mensaje del error. La llamada de Gemini que responde por un fallo de Groq lleva `es_fallback = true`. Las etiquetas `proveedor:groq` y `proveedor:gemini` sirven para filtrar.
- El Flujo C no llama a ningún modelo, por eso no se registra.
- Los embeddings no devuelven tokens: de ellos se ve la latencia y los errores, no el costo.

### Configuración

1. En n8n, crear una credencial **Basic Auth** llamada `Langfuse`: usuario = public key (`pk-lf-…`), contraseña = secret key (`sk-lf-…`). Las claves **no** van en los JSON ni en el repositorio.
2. Importar `Langfuse - registrar.json` y, en el nodo «Armar span OTLP», dejar `LANGFUSE_HOST` con la URL de la región (`https://us.cloud.langfuse.com`).
3. En el nodo «Enviar a Langfuse», seleccionar la credencial `Langfuse`.
4. En los nodos «Registrar en Langfuse» de los Flujos A y B, elegir el sub-workflow importado.
5. En Langfuse, **Project Settings → Models**: cargar el precio por token de `openai/gpt-oss-120b` (Groq no viene en la lista) y comprobar que `gemini-3.5-flash-lite` tenga precio. Hay que hacerlo antes de generar tráfico, porque los cambios solo afectan a las llamadas posteriores.

### Continuidad del servicio

El registro no puede tumbar el bot: va por una rama lateral, el nodo Execute Workflow no espera al sub-workflow y tiene «On Error: Continue», y el envío tiene un tiempo máximo de 5 segundos.

### Privacidad

Langfuse es un servicio externo y recibe los prompts y respuestas completos, **incluida la pregunta escrita por el ciudadano**. No se envían IP, chat_id ni nombres de suscriptores. El acceso a la cuenta debe limitarse al equipo.

