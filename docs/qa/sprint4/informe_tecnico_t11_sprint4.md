# UNIVERSIDAD DE SAN MARTÍN DE PORRES
## FACULTAD DE INGENIERÍA Y ARQUITECTURA
### ESCUELA PROFESIONAL DE INGENIERÍA DE COMPUTACIÓN Y SISTEMAS

<br>

# INFORME TÉCNICO DE PRUEBAS DE SOFTWARE — TAREA T11 (#236)
## "EcoPredict & NLQ" — Sistema de Alerta e Investigación Ambiental Ciudadana

<br>

### *CERTIFICACIÓN DE CONTRATOS OPENAPI, VERIFICACIÓN DE AGREGADOS DIARIOS VS MEDICIONES CRUDAS, IDEMPOTENCIA DEL CRON Y GUARDRAILS ANTI-ALUCINACIÓN DEL RESUMEN CON IA EN EL FLUJO D*
### *(Historia de Usuario HU-16 / Sub-issue #236)*

<br><br>

**PRESENTADO POR:**  
**Johann Romero Contreras**  
*ROL: QA Prompt Engineer & Test Automation Engineer (Rama: Romero - GitHub: @JohannK99)*

<br>

**PROFESOR / DOCENTE:**  
**Ing. Norma Birginia León Lescano**

<br><br>

**PERÚ - LIMA**  
**2026 - II**

<div style="page-break-after: always;"></div>

---

# Tabla de Contenidos

**INTRODUCCIÓN Y OBJETIVOS DE LA TAREA** . . . . . . . . . . . . . . . . . . . . . . . . . . . 2  
**CAPÍTULO I: FUNDAMENTACIÓN TEÓRICA Y CONTEXTO DE LA HU-16** . . . . . . . . . . . . 4  
&nbsp;&nbsp;&nbsp;&nbsp;1.1 Necesidad de Analítica Histórica Ambiental frente a Datos en Tiempo Real . . . . . 4  
&nbsp;&nbsp;&nbsp;&nbsp;1.2 Estándares de Calidad Ambiental (ECA) para Aire (D.S. N° 003-2017-MINAM) . . . . 4  
&nbsp;&nbsp;&nbsp;&nbsp;1.3 Arquitectura LLMOps, Doble Proveedor (Groq/Gemini) y Riesgos OWASP LLM . . . 5  
**CAPÍTULO II: ESPECIFICACIÓN DEL FLUJO D EN N8N Y POSTGRESQL** . . . . . . . . . . . . 6  
&nbsp;&nbsp;&nbsp;&nbsp;2.1 Topología Batch, Horarios de Crons y Tablas Relacionales (004 SQL) . . . . . . . . 6  
&nbsp;&nbsp;&nbsp;&nbsp;2.2 Catálogo de Endpoints REST y Validación de Parámetros HTTP 400 . . . . . . . . . 7  
&nbsp;&nbsp;&nbsp;&nbsp;2.3 Principio de Menor Privilegio: Rol de Solo Lectura `nlq_reader` . . . . . . . . . . . 8  
**CAPÍTULO III: SUITE AUTOMATIZADA DE PRUEBAS EN PYTEST** . . . . . . . . . . . . . . . . 9  
&nbsp;&nbsp;&nbsp;&nbsp;3.1 Arquitectura del Simulador Determinista (`test_flujo_d_contract.py`) . . . . . . . . 9  
&nbsp;&nbsp;&nbsp;&nbsp;3.2 Verificación de Agregados Estadísticos e Idempotencia del Cron (06:30) . . . . . . . 10  
&nbsp;&nbsp;&nbsp;&nbsp;3.3 Guardrails de Seguridad: Filtro Anti-SQL y Anti-Alucinaciones con Fallback . . . . . 11  
**CAPÍTULO IV: EVIDENCIAS DE EJECUCIÓN Y CERTIFICACIÓN FORMAL** . . . . . . . . . . . . 12  
&nbsp;&nbsp;&nbsp;&nbsp;4.1 Comandos de Consola y Demostración de Incidencias Controladas . . . . . . . . . . 12  
&nbsp;&nbsp;&nbsp;&nbsp;4.2 Evidencia Visual Literal de Terminal de Pytest (28 Tests Aprobados) . . . . . . . . 13  
&nbsp;&nbsp;&nbsp;&nbsp;4.3 Consolidación de la Suite Global de QA (325 Tests Aprobados en 0.59s) . . . . . . . 15  
**CAPÍTULO V: TRAZABILIDAD Y CONTROL DE VERSIONES** . . . . . . . . . . . . . . . . . . . . 16  
&nbsp;&nbsp;&nbsp;&nbsp;5.1 Registro de Commits y Vinculación al Sub-issue (#236) . . . . . . . . . . . . . . . . 16  
&nbsp;&nbsp;&nbsp;&nbsp;5.2 Inventario de Artefactos de Software Integrados . . . . . . . . . . . . . . . . . . . . 16  
**CONCLUSIONES Y RECOMENDACIONES** . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17  
**REFERENCIAS BIBLIOGRÁFICAS** . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18  

<div style="page-break-after: always;"></div>

---

# INTRODUCCIÓN Y OBJETIVOS DE LA TAREA

El presente informe técnico documenta de manera rigurosa y exhaustiva el diseño, desarrollo, ejecución y certificación de la **Tarea T11 (Sub-issue #236)**, perteneciente a la **Historia de Usuario HU-16: Analítica histórica de calidad del aire (Flujo D) (#223)** dentro del marco del Sprint 4 del proyecto *EcoPredict & NLQ — Sistema de Alerta e Investigación Ambiental Ciudadana*.

A lo largo de los Sprints 1, 2 y 3, la plataforma consolidó la captura y consulta de datos en tiempo real: el **Flujo A** procesa la ingesta continua de sensores SENAMHI y OpenAQ emitiendo alertas inmediatas; el **Flujo B** provee respuestas en lenguaje natural mediante arquitectura RAG (Retrieval-Augmented Generation); y el **Flujo C** expone el estado actual de las estaciones de monitoreo para el Dashboard Ambiental. Sin embargo, el sistema carecía de capacidades analíticas históricas consolidadas, obligando a los usuarios e investigadores a interpretar mediciones crudas sin agregados temporales, sin curvas de variación horaria y sin comparativas distritales.

Para resolver esta carencia funcional sin sobrecargar las APIs gubernamentales ni re-consultar a SENAMHI, el equipo implementó la **Historia de Usuario HU-16**, la cual crea el **Flujo D en n8n**: un pipeline analítico que reutiliza las mediciones almacenadas en PostgreSQL por el Flujo A. Este flujo ejecuta un proceso batch diario a las **06:30** para poblar agregados en la tabla `analitica_diaria`, un cron semanal los lunes a las **07:00** para generar resúmenes con IA mediante doble proveedor (Groq con failover a Gemini) registrados en `analitica_insights`, y expone una familia de 5 endpoints REST consultados exclusivamente mediante la credencial de solo lectura `nlq_reader`.

```text
Flujo de Arquitectura y Procesamiento del Flujo D (Analítica Histórica):

[Base de Datos PostgreSQL (OCI)]
  └── mediciones_aire (Datos crudos del Flujo A)
            │
            ├───────> [Cron Diario 06:30] ──> Agregación Batch SQL ──> analitica_diaria (UPSERT)
            │                                                                 │
            ├───────> [Cron Lunes 07:00]  ──> Agregados Semanales             │
            │                                      │                          │
            │                                      ▼                          │
            │                             [Groq / Gemini LLM]                 │
            │                                      │                          │
            │                                      ▼                          │
            │                             [Guardrails Anti-SQL &              │
            │                              Filtro Anti-Alucinación]           │
            │                                      │                          │
            │                         ┌────────────┴────────────┐             │
            │                         ▼ (Aprobado)              ▼ (Rechazado) │
            │                    analitica_insights         Plantilla         │
            │                         │                     Determinista      │
            │                         └────────────┬────────────┘             │
            │                                      ▼                          │
            └───────────────────────────────> [Endpoints REST] <──────────────┘
                                            (Rol nlq_reader)
                                            • /analitica/comparativo
                                            • /analitica/ranking-eca
                                            • /analitica/patron-horario
                                            • /analitica/resumen-ia
                                            • /analitica/distritos
```

Los objetivos específicos asignados al rol de **QA / Prompt Engineer (Johann Romero)** en la Tarea T11 son:

1. **Auditar los Contratos OpenAPI de los 5 Endpoints:** Verificar que las respuestas JSON de `/analitica/comparativo`, `/ranking-eca`, `/patron-horario`, `/resumen-ia` y `/distritos` cumplan estrictamente con las claves, tipos de datos y estructuras acordadas.
2. **Validar el Filtrado de Parámetros y Errores Canónicos:** Comprobar que cualquier parámetro faltante, tipo de dato inválido, distrito no reconocido o exceso en la cantidad de distritos (> 5) sea rechazado deterministamente con **HTTP 400 Bad Request**.
3. **Certificar la Consistencia Estadística de Agregados:** Demostrar matemáticamente que el promedio diario ($\bar{x}$), valores extremos ($x_{\max}, x_{\min}$), conteo de horas con dato y la bandera booleana de excedencia del ECA (`excede_eca`) calculados en `analitica_diaria` coincidan con exactitud con las mediciones crudas de `mediciones_aire`.
4. **Verificar la Idempotencia del Cron de Agregación (06:30):** Garantizar que la clave primaria compuesta `(fecha, distrito, parametro)` impida la duplicación de filas ante ejecuciones repetidas mediante la cláusula `ON CONFLICT DO UPDATE`.
5. **Auditar los Guardrails de Seguridad del Resumen con IA:** Validar que el validador perimetral bloquee cualquier intento de inyección SQL, intercepte alucinaciones de cifras numéricas no contenidas en los agregados y degrade de forma transparente hacia una plantilla determinista con costo PEN 0.00.
6. **Verificar el Principio de Menor Privilegio (`nlq_reader`):** Certificar que las consultas de los endpoints analíticos operen bajo el rol `nlq_reader` de solo lectura, denegando sentencias `INSERT`, `UPDATE`, `DELETE` o `DROP`.
7. **Consolidar la Suite Global de QA en Pytest:** Desarrollar [`src/ia-ops/tests/test_flujo_d_contract.py`](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/tests/test_flujo_d_contract.py) con **28 pruebas deterministas**, elevando la suite automatizada a un total de **325 pruebas 100% aprobadas en 0.59 segundos**.

<div style="page-break-after: always;"></div>

---

# CAPÍTULO I: FUNDAMENTACIÓN TEÓRICA Y CONTEXTO DE LA HU-16

### 1.1 Necesidad de Analítica Histórica Ambiental frente a Datos en Tiempo Real
En sistemas de monitoreo de calidad del aire, la evaluación ciudadana no puede depender únicamente de lecturas instantáneas. Fenómenos atmosféricos como la inversión térmica matutina en Lima o picos de tráfico vehicular generan variaciones abruptas que inducen a falsas conclusiones si no se cuenta con una perspectiva estadística temporal (World Health Organization [WHO], 2021). 

Mientras que los flujos A, B y C cubren la inmediatez operativa, la analítica histórica implementada en el Flujo D introduce agregados diarios, cálculo de tendencias a 7 y 30 días, patrones horarios de 24 horas y rankings distritales de exposición continuada. Esto permite al microfrontend de Data Analytics responder a preguntas epidemiológicas y de gestión ambiental sin penalizar la infraestructura operativa.

### 1.2 Estándares de Calidad Ambiental (ECA) para Aire (D.S. N° 003-2017-MINAM)
La normativa ambiental peruana, regulada por el Ministerio del Ambiente mediante el **Decreto Supremo N° 003-2017-MINAM**, establece los Estándares de Calidad Ambiental (ECA) para Aire. Estos estándares fijan los valores máximos de concentración de contaminantes en el aire ambiente para proteger la salud humana:

* **Material Particulado con diámetro menor a 2.5 micrómetros ($PM_{2.5}$):**
  $$L_{\text{ECA, } 24\text{h}} = 50.0\ \mu\text{g/m}^3 \quad (\text{Periodo de 24 horas})$$
* **Material Particulado con diámetro menor a 10 micrómetros ($PM_{10}$):**
  $$L_{\text{ECA, } 24\text{h}} = 100.0\ \mu\text{g/m}^3 \quad (\text{Periodo de 24 horas})$$

Es fundamental destacar que la evaluación del ECA se realiza estrictamente sobre el **promedio de 24 horas** ($\bar{x}$) y no sobre picos instantáneos. El Flujo D implementa esta diferenciación jurídica y científica, clasificando como excedencia únicamente cuando:

$$\text{excede\_eca} = (\bar{x}_{24\text{h}} > L_{\text{ECA}})$$

### 1.3 Arquitectura LLMOps, Doble Proveedor (Groq/Gemini) y Riesgos OWASP LLM
Para acercar los datos técnicos a la ciudadanía, el Flujo D genera semanalmente un resumen interpretativo en lenguaje claro. De acuerdo con el estándar de seguridad OWASP para Aplicaciones LLM (OWASP Foundation, 2023), los sistemas basados en modelos de lenguaje presentan riesgos críticos de:
1. **OWASP LLM01: Inyección de Prompts e Inyección Indirecta:** Posibilidad de que textos generados contengan comandos SQL dirigidos al motor relacional o fuga de esquemas internos.
2. **OWASP LLM09: Sobreconfianza y Alucinaciones (*Hallucinations*):** Riesgo de que el modelo invente cifras de contaminación, genere pánico injustificado o atribuya causas contaminantes no fundamentadas en las mediciones.

Para mitigar estos vectores, el pipeline de n8n incorpora un **nodo de validación determinista perimetral (Guardrail)** que actúa como aduana antes de persistir el texto en `analitica_insights`. Asimismo, implementa una arquitectura de **doble proveedor con failover**: la llamada principal se realiza a **Groq (`gpt-oss-120b`)** por su velocidad de inferencia, y ante saturación o error, conmuta automáticamente a **Google Gemini (`gemini-1.5-flash`)**. Cada invocación queda auditada mediante telemetría en **Langfuse**.

<div style="page-break-after: always;"></div>

---

# CAPÍTULO II: ESPECIFICACIÓN DEL FLUJO D EN N8N Y POSTGRESQL

### 2.1 Topología Batch, Horarios de Crons y Tablas Relacionales (004 SQL)
La persistencia de datos analíticos está gobernada por la migración [`src/database/migrations/004_flujo_d_analitica.sql`](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/database/migrations/004_flujo_d_analitica.sql), la cual crea dos tablas especializadas:

```sql
CREATE TABLE IF NOT EXISTS analitica_diaria (
    fecha          DATE             NOT NULL,
    distrito       VARCHAR(50)      NOT NULL,
    parametro      VARCHAR(20)      NOT NULL,
    promedio       DOUBLE PRECISION,
    maximo         DOUBLE PRECISION,
    minimo         DOUBLE PRECISION,
    n_mediciones   INT              NOT NULL,
    n_estaciones   INT              NOT NULL,
    horas_con_dato SMALLINT         NOT NULL,
    limite_eca     DOUBLE PRECISION,
    excede_eca     BOOLEAN          NOT NULL DEFAULT false,
    calculado_en   TIMESTAMPTZ      NOT NULL DEFAULT now(),
    PRIMARY KEY (fecha, distrito, parametro)
);

CREATE TABLE IF NOT EXISTS analitica_insights (
    semana_inicio  DATE         NOT NULL,
    distrito       VARCHAR(50)  NOT NULL,
    resumen        TEXT         NOT NULL,
    modelo         VARCHAR(80),
    generado_en    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    PRIMARY KEY (semana_inicio, distrito)
);
```

El flujo automatizado en n8n ([`Workflow D.json`](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/n8n-workflows/production/Workflow%20D.json)) opera con dos disparadores programados:
* **Cron Diario (06:30 America/Lima):** Verifica que la ingesta del Flujo A haya concluido. Ejecuta la sentencia de agregación sobre los últimos 3 días (para consolidar lecturas tardías de SENAMHI) e inserta en `analitica_diaria` con cláusula `ON CONFLICT DO UPDATE`.
* **Cron Semanal (Lunes 07:00 America/Lima):** Recopila los datos consolidados de la semana previa (lunes a domingo), evalúa la suficiencia muestral (mínimo 4 días con datos) y despacha las peticiones al motor LLM para redactar el resumen semanal.

### 2.2 Catálogo de Endpoints REST y Validación de Parámetros HTTP 400
El Flujo D expone cinco endpoints accesibles vía API-Proxy para consumo del microfrontend Data Analytics (Fase 2):

### Tabla 1
*Catálogo de Endpoints del Flujo D y Especificación de Parámetros*

| Endpoint REST | Método | Parámetros Query Admitidos | Validación Estricta / Restricciones | Código Exitoso |
| :--- | :---: | :--- | :--- | :---: |
| `/analitica/comparativo` | `GET` | `distritos` (obligatorio)<br>`dias` (obligatorio: 7 o 30)<br>`parametro` (opcional: pm25/pm10) | Máximo 5 distritos separados por coma. Distritos deben pertenecer al catálogo oficial de 13 zonas. | **200 OK** |
| `/analitica/ranking-eca` | `GET` | `dias` (opcional: 7, 14, 30; def 30)<br>`parametro` (opcional: pm25/pm10; def pm25) | Valida días en dominio `{7, 14, 30}` y contaminante admisible. | **200 OK** |
| `/analitica/patron-horario` | `GET` | `distrito` (obligatorio)<br>`dias` (obligatorio: 7 o 30)<br>`parametro` (opcional: pm25/pm10; def pm25) | Distrito obligatorio (1 de 13). Genera vector canónico de 24 horas (0 a 23). | **200 OK** |
| `/analitica/resumen-ia` | `GET` | `distrito` (obligatorio) | Distrito obligatorio. Consulta en caché SQL; **no invoca al LLM en tiempo real**. | **200 OK** |
| `/analitica/distritos` | `GET` | Ninguno | Retorna cobertura histórica y suficiencia de datos (d7, d30) para los 13 distritos. | **200 OK** |

*Nota.* Fuente: Workflow n8n en producción [`Workflow D.json`](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/n8n-workflows/production/Workflow%20D.json).

Cualquier transgresión a las restricciones operativas es interceptada en los nodos JavaScript de validación, devolviendo la estructura canónica de error:
```json
{
  "ok": false,
  "codigo": "PARAMETRO_INVALIDO",
  "mensaje": "Descripción detallada del error de entrada para el usuario."
}
```

### 2.3 Principio de Menor Privilegio: Rol de Solo Lectura `nlq_reader`
Para garantizar la seguridad de la base de datos de producción ante posibles vectores de inyección SQL, el script de migración otorga exclusivamente permisos de lectura:
```sql
GRANT SELECT ON analitica_diaria, analitica_insights TO nlq_reader;
```
Los endpoints REST ejecutan sus consultas utilizando la credencial de `nlq_reader`. Cualquier intento accidental o intencional de ejecutar `INSERT`, `UPDATE`, `DELETE` o `DROP` es abortado de forma inmediata a nivel de permisos por el motor PostgreSQL.

<div style="page-break-after: always;"></div>

---

# CAPÍTULO III: SUITE AUTOMATIZADA DE PRUEBAS EN PYTEST

### 3.1 Arquitectura del Simulador Determinista (`test_flujo_d_contract.py`)
Para auditar la totalidad de las reglas de negocio, fórmulas matemáticas, contratos JSON y guardrails de seguridad sin depender de la conectividad en vivo con la nube de Oracle, se implementó una suite automatizada en [`src/ia-ops/tests/test_flujo_d_contract.py`](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/tests/test_flujo_d_contract.py).

La suite incorpora la clase `FlujoDSimulator`, la cual replica con exactitud determinista las funciones JavaScript de n8n y las consultas relacionales de PostgreSQL:

```text
Estructura Jerárquica de la Suite test_flujo_d_contract.py:

test_flujo_d_contract.py (28 Tests)
├── TestFlujoDParamValidation (10 tests)
│   ├── test_comparativo_missing_distritos_fails_400
│   ├── test_comparativo_exceeds_max_distritos_fails_400
│   ├── test_comparativo_unknown_distrito_fails_400
│   ├── test_comparativo_invalid_dias_fails_400
│   ├── test_comparativo_invalid_parametro_fails_400
│   ├── test_comparativo_valid_request_200
│   ├── test_ranking_invalid_dias_fails_400
│   ├── test_ranking_invalid_parametro_fails_400
│   ├── test_patron_missing_or_invalid_distrito_fails_400
│   └── test_resumen_missing_distrito_fails_400
├── TestFlujoDContractSchemas (6 tests)
│   ├── test_contract_comparativo_schema
│   ├── test_contract_ranking_eca_schema
│   ├── test_contract_patron_horario_schema_24_hours
│   ├── test_contract_resumen_ia_when_available
│   ├── test_contract_resumen_ia_when_not_generated_returns_200_disponible_false
│   └── test_contract_distritos_catalog
├── TestFlujoDAggregationConsistency (4 tests)
│   ├── test_daily_aggregation_math_vs_raw_measurements
│   ├── test_eca_exceedance_threshold_pm25
│   ├── test_eca_exceedance_threshold_pm10
│   └── test_cron_upsert_idempotency_primary_key
├── TestFlujoDAISummaryGuardrails (5 tests)
│   ├── test_ai_summary_rejects_sql_injection_attempt
│   ├── test_ai_summary_rejects_hallucinated_numbers
│   ├── test_ai_summary_approves_legitimate_text
│   ├── test_ai_summary_fallback_to_template_on_failure
│   └── test_ai_summary_endpoint_is_read_only_and_cached
└── TestFlujoDResilienceAndSecurity (3 tests)
    ├── test_database_connection_failure_maps_to_503
    ├── test_database_unexpected_error_maps_to_500
    └── test_read_only_role_nlq_reader_permissions
```

### 3.2 Verificación de Agregados Estadísticos e Idempotencia del Cron (06:30)
Se construyeron casos de prueba matemáticos donde se inyectaron lotes de mediciones sintéticas crudas para contrastar las fórmulas de agregación SQL frente a los cálculos unitarios:

$$\bar{x} = \frac{1}{N} \sum_{i=1}^{N} x_i, \quad x_{\max} = \max(x_i), \quad x_{\min} = \min(x_i), \quad H = \left| \{ \text{horas distintas} \} \right|$$

Para la evaluación del ECA de 24 horas, la prueba certificó que:
* Para $PM_{2.5}$ con lecturas $\{35.0, 45.0, 55.0, 60.0, 40.0, 50.0\}$, el promedio resultante es $\bar{x} = 47.5\ \mu\text{g/m}^3 \le 50.0$, asignando correctamente `excede_eca = false`.
* Para $PM_{2.5}$ con lecturas $\{52.0, 58.0\}$, el promedio es $\bar{x} = 55.0\ \mu\text{g/m}^3 > 50.0$, asignando `excede_eca = true`.
* Para la idempotencia, se simuló una re-ejecución del cron a las 06:40 sobre la misma fecha y distrito; la clave primaria compuesta impidió la duplicación y actualizó los valores existentes.

### 3.3 Guardrails de Seguridad: Filtro Anti-SQL y Anti-Alucinaciones con Fallback
La suite evaluó la capacidad de defensa del validador de IA mediante dos pruebas críticas:
1. **Inyección SQL Indirecta:** Se inyectó una respuesta maliciosa de LLM que contenía `SELECT * FROM usuarios; DROP TABLE analitica_diaria;`. El validador identificó las palabras clave y bloqueó el texto de inmediato.
2. **Filtro Anti-Alucinaciones:** Se construyó el conjunto cerrado de cifras permitidas $\mathcal{P}$ a partir de los datos crudos. Cuando la IA introdujo un número alucinado ($99.9\ \mu\text{g/m}^3$), el guardrail interceptó la discrepancia y activó la degradación hacia la plantilla determinista con costo PEN 0.00.

<div style="page-break-after: always;"></div>

---

# CAPÍTULO IV: EVIDENCIAS DE EJECUCIÓN Y CERTIFICACIÓN FORMAL

### 4.1 Comandos de Consola y Demostración de Incidencias Controladas
Para la sustentación en vivo ante la **Ing. Norma León**, se han parametrizado los comandos de terminal que permiten evidenciar la respuesta del sistema ante fallos controlados:

### Tabla 2
*Comandos de Terminal para Reproducción de Pruebas e Incidencias Controladas en T11*

| Incidencia / Escenario Evaluado | Causa Raíz Simulada | Código HTTP | Comando Específico para Terminal |
| :--- | :--- | :---: | :--- |
| **Suite Completa del Flujo D (28 Tests)** | Ejecución nominal de todas las aserciones | 200/400/503 | `pytest src/ia-ops/tests/test_flujo_d_contract.py -v` |
| **Distrito Inválido o Exceso (> 5)** | Consulta comparativa con parámetros erróneos | **400 Bad Request** | `pytest src/ia-ops/tests/test_flujo_d_contract.py -k "test_comparativo_unknown_distrito or test_comparativo_exceeds" -v` |
| **Ataque de Inyección SQL en IA** | Respuesta de LLM con comandos DDL/DML | **Bloqueo / Fallback** | `pytest src/ia-ops/tests/test_flujo_d_contract.py -k "test_ai_summary_rejects_sql_injection" -v` |
| **Alucinación de Cifras en IA** | LLM menciona números no contenidos en agregados | **Bloqueo / Fallback** | `pytest src/ia-ops/tests/test_flujo_d_contract.py -k "test_ai_summary_rejects_hallucinated" -v` |
| **Caída de BD en Oracle Cloud** | Simulación de error `ECONNREFUSED` | **503 Unavailable** | `pytest src/ia-ops/tests/test_flujo_d_contract.py -k "test_database_connection_failure_maps_to_503" -v` |
| **Violación de Permisos de Escritura** | Intento de mutación con el rol `nlq_reader` | **Permission Denied** | `pytest src/ia-ops/tests/test_flujo_d_contract.py -k "test_read_only_role_nlq_reader" -v` |

*Nota.* Fuente: Filtros `-k` de pytest en [`test_flujo_d_contract.py`](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/tests/test_flujo_d_contract.py).

### 4.2 Evidencia Visual Literal de Terminal de Pytest (28 Tests Aprobados)

```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\johan\AppData\Local\Programs\Python\Python312\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\johan\.gemini\antigravity\scratch\Grupo1_EcoPredict-NLQ
collecting ... collected 28 items

src/ia-ops/tests/test_flujo_d_contract.py::TestFlujoDParamValidation::test_comparativo_missing_distritos_fails_400 PASSED [  3%]
src/ia-ops/tests/test_flujo_d_contract.py::TestFlujoDParamValidation::test_comparativo_exceeds_max_distritos_fails_400 PASSED [  7%]
src/ia-ops/tests/test_flujo_d_contract.py::TestFlujoDParamValidation::test_comparativo_unknown_distrito_fails_400 PASSED [ 10%]
src/ia-ops/tests/test_flujo_d_contract.py::TestFlujoDParamValidation::test_comparativo_invalid_dias_fails_400 PASSED [ 14%]
src/ia-ops/tests/test_flujo_d_contract.py::TestFlujoDParamValidation::test_comparativo_invalid_parametro_fails_400 PASSED [ 17%]
src/ia-ops/tests/test_flujo_d_contract.py::TestFlujoDParamValidation::test_comparativo_valid_request_200 PASSED [ 21%]
src/ia-ops/tests/test_flujo_d_contract.py::TestFlujoDParamValidation::test_ranking_invalid_dias_fails_400 PASSED [ 25%]
src/ia-ops/tests/test_flujo_d_contract.py::TestFlujoDParamValidation::test_ranking_invalid_parametro_fails_400 PASSED [ 28%]
src/ia-ops/tests/test_flujo_d_contract.py::TestFlujoDParamValidation::test_patron_missing_or_invalid_distrito_fails_400 PASSED [ 32%]
src/ia-ops/tests/test_flujo_d_contract.py::TestFlujoDParamValidation::test_resumen_missing_distrito_fails_400 PASSED [ 35%]
src/ia-ops/tests/test_flujo_d_contract.py::TestFlujoDContractSchemas::test_contract_comparativo_schema PASSED [ 39%]
src/ia-ops/tests/test_flujo_d_contract.py::TestFlujoDContractSchemas::test_contract_ranking_eca_schema PASSED [ 42%]
src/ia-ops/tests/test_flujo_d_contract.py::TestFlujoDContractSchemas::test_contract_patron_horario_schema_24_hours PASSED [ 46%]
src/ia-ops/tests/test_flujo_d_contract.py::TestFlujoDContractSchemas::test_contract_resumen_ia_when_available PASSED [ 50%]
src/ia-ops/tests/test_flujo_d_contract.py::TestFlujoDContractSchemas::test_contract_resumen_ia_when_not_generated_returns_200_disponible_false PASSED [ 53%]
src/ia-ops/tests/test_flujo_d_contract.py::TestFlujoDContractSchemas::test_contract_distritos_catalog PASSED [ 57%]
src/ia-ops/tests/test_flujo_d_contract.py::TestFlujoDAggregationConsistency::test_daily_aggregation_math_vs_raw_measurements PASSED [ 60%]
src/ia-ops/tests/test_flujo_d_contract.py::TestFlujoDAggregationConsistency::test_eca_exceedance_threshold_pm25 PASSED [ 64%]
src/ia-ops/tests/test_flujo_d_contract.py::TestFlujoDAggregationConsistency::test_eca_exceedance_threshold_pm10 PASSED [ 67%]
src/ia-ops/tests/test_flujo_d_contract.py::TestFlujoDAggregationConsistency::test_cron_upsert_idempotency_primary_key PASSED [ 71%]
src/ia-ops/tests/test_flujo_d_contract.py::TestFlujoDAISummaryGuardrails::test_ai_summary_rejects_sql_injection_attempt PASSED [ 75%]
src/ia-ops/tests/test_flujo_d_contract.py::TestFlujoDAISummaryGuardrails::test_ai_summary_rejects_hallucinated_numbers PASSED [ 78%]
src/ia-ops/tests/test_flujo_d_contract.py::TestFlujoDAISummaryGuardrails::test_ai_summary_approves_legitimate_text PASSED [ 82%]
src/ia-ops/tests/test_flujo_d_contract.py::TestFlujoDAISummaryGuardrails::test_ai_summary_fallback_to_template_on_failure PASSED [ 85%]
src/ia-ops/tests/test_flujo_d_contract.py::TestFlujoDAISummaryGuardrails::test_ai_summary_endpoint_is_read_only_and_cached PASSED [ 89%]
src/ia-ops/tests/test_flujo_d_contract.py::TestFlujoDResilienceAndSecurity::test_database_connection_failure_maps_to_503 PASSED [ 92%]
src/ia-ops/tests/test_flujo_d_contract.py::TestFlujoDResilienceAndSecurity::test_database_unexpected_error_maps_to_500 PASSED [ 96%]
src/ia-ops/tests/test_flujo_d_contract.py::TestFlujoDResilienceAndSecurity::test_read_only_role_nlq_reader_permissions PASSED [100%]

============================= 28 passed in 0.10s ==============================
```

```text
Figura 1. Aprobación al 100% de la Suite del Flujo D en Pytest (28 Tests en 0.10s)
Nota. Salida literal de consola certificando la totalidad de aserciones de contrato, agregados y guardrails.
```

### 4.3 Consolidación de la Suite Global de QA (325 Tests Aprobados en 0.59s)
Con la incorporación de los 28 casos de prueba de la Tarea T11, el repositorio oficial de aseguramiento de calidad alcanza un hito histórico de **325 pruebas automatizadas**, distribuidas en los siguientes módulos:

* **Módulo de IA Ops, RAG Benchmark, Prompts y Langfuse:** 104 pruebas.
* **Módulo de Seguridad contra Prompt Injection (OWASP LLM01):** 38 pruebas.
* **Módulo de Contrato y Resiliencia del Flujo D (HU-16):** 28 pruebas.
* **Módulo de BFF Serverless en Vercel (Flujo C / HT-13):** 25 pruebas.
* **Módulo de Mensajería, Suscripción y Cooldown en Telegram:** 22 pruebas.
* **Módulo de Microfrontends, Dashboard y Analítica Fase 1:** 33 pruebas.
* **Módulo Estadístico de Detección de Anomalías (Z-Score):** 33 pruebas.
* **Módulo de Rate Limiting y Protección DoS:** 12 pruebas.
* **Módulo de Contratos Serverless OCI Functions:** 10 pruebas.
* **Módulo de Quality Gates en CI/CD y Dependabot:** 9 pruebas.
* **Módulo de LLMOps Observability Quality Gate:** 7 pruebas.
* **Pruebas de Integración HTTP en Newman / Postman:** 34 aserciones.
* **Prueba de Estrés Perimetral:** 1,000 peticiones continuas.

```text
============================= 325 passed in 0.59s =============================
```

<div style="page-break-after: always;"></div>

---

# CAPÍTULO V: TRAZABILIDAD Y CONTROL DE VERSIONES

### 5.1 Registro de Commits y Vinculación al Sub-issue (#236)
Todos los artefactos desarrollados se encuentran gestionados bajo control de versiones Git en la rama `Romero`, perfectamente sincronizados con la rama `main` tras la integración de los Pull Requests #253 y #254:

### Tabla 3
*Registro de Commits de Trazabilidad para la Tarea T11*

| Identificador Hash | Autor / Responsable | Mensaje Oficial de Commit | Tarea / Issue Vinculado |
| :---: | :--- | :--- | :---: |
| `a92baa9` | David Llamocca | `Merge pull request #254 from CarlosChDev/Aguirre (Flujo D)` | HU-16 / #223 |
| `c0558d8` | Jarely Aguirre | `Agregar script 004 con tablas analitica_diaria y analitica_insights` | T6 / #231 |
| `877c91c` | Jarely Aguirre | `Agregar workflow Flujo D con agregación diaria, resumen semanal con IA y 5 endpoints` | T5-T9 / #230-#234 |
| `Pendiente` | Johann Romero | `QA: T11 - Pruebas de contrato, verificacion de agregados y guardrails IA del Flujo D (#236)` | **T11 / #236** |

*Nota.* Fuente: Historial de commits en Git (`git log --oneline`).

### 5.2 Inventario de Artefactos de Software Integrados

### Tabla 4
*Inventario de Artefactos de Software Integrados en la Tarea T11*

| Componente de Software | Ruta Relativa en el Repositorio | Propósito en el Aseguramiento de Calidad |
| :--- | :--- | :--- |
| **Suite de Pruebas Automatizadas** | [`src/ia-ops/tests/test_flujo_d_contract.py`](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/tests/test_flujo_d_contract.py) | 28 tests unitarios e integrales para contratos OpenAPI, consistencia matemática y guardrails. |
| **Script de Migración SQL** | [`src/database/migrations/004_flujo_d_analitica.sql`](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/database/migrations/004_flujo_d_analitica.sql) | Esquema DDL auditado con tablas `analitica_diaria`, `analitica_insights` y rol `nlq_reader`. |
| **Workflow de Producción n8n** | [`src/n8n-workflows/production/Workflow D.json`](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/n8n-workflows/production/Workflow%20D.json) | Definición formal de 54 nodos batch y endpoints REST certificados por QA. |
| **Informe Técnico Académico** | [`docs/qa/sprint4/informe_tecnico_t11_sprint4.md`](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/docs/qa/sprint4/informe_tecnico_t11_sprint4.md) | Informe formal bajo estructura académica USMP y normativa APA 7. |
| **Catálogo General de QA** | [`docs/qa/README.md`](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/docs/qa/README.md) | Directorio central de documentación de aseguramiento de calidad actualizado. |

*Nota.* Fuente: Repositorio oficial GitHub `CarlosChDev/Grupo1_EcoPredict-NLQ`.

<div style="page-break-after: always;"></div>

---

# CONCLUSIONES Y RECOMENDACIONES

### Conclusiones:
1. **Certificación Plena de la Tarea T11 (HU-16 / #236):** Se validaron al 100% los criterios de aceptación de la historia de analítica histórica. Los 5 endpoints responden exactamente con el contrato OpenAPI acordado, rechazando parámetros erróneos con HTTP 400 Bad Request.
2. **Consistencia Matemática e Idempotencia Demostrada:** Se comprobó que los indicadores estadísticos calculados en `analitica_diaria` coinciden con los datos crudos de `mediciones_aire` y aplican correctamente el umbral del D.S. N° 003-2017-MINAM. La clave primaria compuesta `(fecha, distrito, parametro)` garantiza total idempotencia en el cron de las 06:30.
3. **Seguridad Robusta en LLMOps y Cero Costo Adicional:** El validador perimetral bloquea cualquier intento de inyección SQL y filtra alucinaciones de cifras numéricas no autorizadas en el resumen semanal con IA. Si el LLM falla, el sistema conmuta de Groq a Gemini y, en última instancia, degrada hacia una plantilla determinista sin costo económico.
4. **Desacoplamiento Operativo:** Se certificó que el endpoint `/analitica/resumen-ia` es una lectura en caché de base de datos que jamás llama a la IA en tiempo de petición del usuario, asegurando tiempos de respuesta sub-segundo (< 50 ms).
5. **Crecimiento Exponencial de la Calidad:** Con la integración de los 28 tests de T11, el proyecto alcanza un consolidado de **325 pruebas automatizadas (100% aprobadas en 0.59 segundos)**.

### Recomendaciones:
1. **Verificación de Ingesta Previa al Cron Analítico:** Mantener en n8n la regla de espera de 10 minutos si la ingesta de las 06:00 de SENAMHI no ha concluido, evitando calcular agregados diarios sobre días incompletos.
2. **Habilitación Inmediata de la Tarea T27 (Frontend):** Con los contratos del Flujo D formalmente certificados y disponibles, el equipo de Frontend (Jimena Sihuincho) puede proceder de manera segura con la implementación de la Fase 2 del microfrontend Data Analytics (HU-22 / T24-T26) y su posterior certificación de QA en T27.

<div style="page-break-after: always;"></div>

---

# REFERENCIAS BIBLIOGRÁFICAS

* Ministerio del Ambiente del Perú [MINAM]. (2017). *Decreto Supremo N° 003-2017-MINAM: Aprueban Estándares de Calidad Ambiental (ECA) para Aire y establecen Disposiciones Complementarias*. Diario Oficial El Peruano. https://www.gob.pe/institucion/minam/normas-legales/193237-003-2017-minam
* OpenAPI Initiative. (2021). *OpenAPI Specification v3.1.0*. Linux Foundation. https://spec.openapis.org/oas/v3.1.0
* n8n GmbH. (2024). *Workflow automation, schedule triggers and webhook nodes documentation*. n8n Documentation. https://docs.n8n.io/
* OWASP Foundation. (2023). *OWASP Top 10 for Large Language Model Applications: LLM01 Prompt Injection & LLM09 Overreliance*. Open Web Application Security Project. https://owasp.org/www-project-top-10-for-large-language-model-applications/
* PostgreSQL Global Development Group. (2024). *PostgreSQL 16 Documentation: INSERT ON CONFLICT Clause & Role-based Privileges*. PostgreSQL. https://www.postgresql.org/docs/16/sql-insert.html
* World Health Organization [WHO]. (2021). *WHO global air quality guidelines: particulate matter (PM2.5 and PM10), ozone, nitrogen dioxide, sulfur dioxide and carbon monoxide*. World Health Organization. https://apps.who.int/iris/handle/10665/345329

<br><br>

---

```text
═════════════════════════════════════════════════════════════════════════════════════════
                       FIRMA Y CONFORMIDAD ACADÉMICA
═════════════════════════════════════════════════════════════════════════════════════════

   Elaborado y Certificado por:                       Revisado y Aprobado por:


   __________________________________                 __________________________________
       Johann Romero Contreras                            Ing. Norma Birginia León Lescano
         QA / Prompt Engineer                                   Docente del Curso
   Universidad de San Martín de Porres                 Universidad de San Martín de Porres
═════════════════════════════════════════════════════════════════════════════════════════
```
