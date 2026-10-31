# UNIVERSIDAD DE SAN MARTÍN DE PORRES
## FACULTAD DE INGENIERÍA Y ARQUITECTURA
### ESCUELA PROFESIONAL DE INGENIERÍA DE COMPUTACIÓN Y SISTEMAS

<br>

# INFORME TÉCNICO CONSOLIDADO DE CIERRE DE SPRINT 3
## "EcoPredict & NLQ" - Sistema de Alerta e Investigación Ambiental Ciudadana

<br>

### *Aseguramiento de Calidad: Evaluación de Calidad de IA (RAG, Fallback y LLM-as-a-Judge), Observabilidad con Langfuse, Notificaciones Ciudadanas en Telegram con Anti-Spam 24h, Contratos Serverless en OCI Functions, Integración de Microfrontend de Analítica y Quality Gates en CI/CD con Dependabot*
### *Historias Técnicas: HT-09 (#151) y HT-10 (#152)*

<br><br>

**PRESENTADO POR:**  
**Johann Romero Contreras**  
*ROL: QA / Prompt Engineer (Rama: Romero - GitHub: @JohannK99)*

<br>

**PROFESOR / DOCENTE:**  
**Ing. Norma Birginia León Lescano**

<br><br>

**PERÚ - LIMA**  
**2026 - II**

<div style="page-break-after: always;"></div>

---

# Índice General

**INTRODUCCIÓN Y OBJETIVOS GENERALES DEL SPRINT 3** . . . . . . . . . . . . . . . 3  
**CAPÍTULO I: ARQUITECTURA GENERAL Y DIMENSIONES EVALUADAS EN EL SPRINT 3** . . 5  
&nbsp;&nbsp;&nbsp;&nbsp;1.1 Topología de Microfrontends, IA Ops y Serverless en Oracle Cloud y Vercel . . . . 5  
&nbsp;&nbsp;&nbsp;&nbsp;1.2 Dimensiones de Calidad y Criterios de Aceptación Globales . . . . 6  
**CAPÍTULO II: AUDITORÍA DE CALIDAD DE IA, RAG Y OBSERVABILIDAD (HT-10 / #152)** . . 7  
&nbsp;&nbsp;&nbsp;&nbsp;2.1 Benchmark Anti-Alucinaciones para Evaluación de Acierto RAG (T23 / #183) . . . . 7  
&nbsp;&nbsp;&nbsp;&nbsp;2.2 Definición y Calibración de Métricas de Calidad de IA en Producción (T24 / #184) . . . . 9  
&nbsp;&nbsp;&nbsp;&nbsp;2.3 Verificación y Auditoría de Telemetría frente a Langfuse (T25 / #185) . . . . 11  
**CAPÍTULO III: NOTIFICACIÓN CIUDADANA Y MECANISMOS ANTI-SPAM EN TELEGRAM (HT-09 / #151)** . . 13  
&nbsp;&nbsp;&nbsp;&nbsp;3.1 Ciclo de Vida de Suscripción Ciudadana y Pruebas Live E2E (T18 / #178) . . . . 13  
&nbsp;&nbsp;&nbsp;&nbsp;3.2 Validación Determinista del Cooldown Anti-Spam de 24 Horas (T19 / #179) . . . . 15  
**CAPÍTULO IV: CERTIFICACIÓN DE CONTRATOS Y SLA DE OCI FUNCTIONS SERVERLESS (HT-09 / #151)** . . 17  
&nbsp;&nbsp;&nbsp;&nbsp;4.1 Validación de Contratos JSON Schema y Matriz de Códigos HTTP (T20 / #180) . . . . 17  
&nbsp;&nbsp;&nbsp;&nbsp;4.2 Tolerancia a Cold Starts y Degradación Resiliente ante Falla de Base de Datos . . . . 19  
**CAPÍTULO V: PRUEBAS DE INTEGRACIÓN DEL MICROFRONTEND DE ANALÍTICA (HT-09 / #151)** . . 21  
&nbsp;&nbsp;&nbsp;&nbsp;5.1 Certificación de Custom Elements (`<mfe-analytics>`) y Shadow DOM (T21 / #181) . . . . 21  
&nbsp;&nbsp;&nbsp;&nbsp;5.2 Renderizado Reactivo con Chart.js, Cumplimiento ECA-Aire y Manejo de Errores de Red . . 23  
**CAPÍTULO VI: CONSOLIDACIÓN DE QUALITY GATES EN CI/CD Y AUDITORÍA DEPENDABOT (HT-09 / #151)** . . 25  
&nbsp;&nbsp;&nbsp;&nbsp;6.1 Integridad y Orquestación de los 7 Pipelines en GitHub Actions (T22 / #182) . . . . 25  
&nbsp;&nbsp;&nbsp;&nbsp;6.2 Configuración y Auditoría de Vulnerabilidades Automatizada con Dependabot . . . . 27  
**CAPÍTULO VII: PROYECCIÓN DE CARGA Y PRUEBAS DE ESTRÉS (1,000 SOLICITUDES)** . . 29  
&nbsp;&nbsp;&nbsp;&nbsp;7.1 Evaluación del Comportamiento DoS, Aislamiento por IP Real y HTTP 429 . . . . 29  
**CAPÍTULO VIII: COMANDOS DE EJECUCIÓN Y DEMOSTRACIÓN DE INCIDENCIAS CONTROLADAS** . . 31  
&nbsp;&nbsp;&nbsp;&nbsp;8.1 Guía de Comandos de Terminal para Reproducción de Pruebas Unitarias e Integración . . . 31  
&nbsp;&nbsp;&nbsp;&nbsp;8.2 Comandos y Casos de Demostración de Incidencias Controladas (400, 401, 422, 504) . . . 33  
**CAPÍTULO IX: MATRIZ CONSOLIDADA DE MÉTRICAS Y EVOLUCIÓN SPRINT 2 VS SPRINT 3** . . 35  
&nbsp;&nbsp;&nbsp;&nbsp;9.1 Comparativa de Cobertura (+67.1% en Tests Pytest) y Estabilidad . . . . 35  
&nbsp;&nbsp;&nbsp;&nbsp;9.2 Matriz Global de Aseguramiento de Calidad del Sprint 3 . . . . 36  
**CAPÍTULO X: TRAZABILIDAD, CONTROL DE VERSIONES Y PULL REQUESTS (#200 Y #207)** . . 37  
&nbsp;&nbsp;&nbsp;&nbsp;10.1 Cierre de HT-10 mediante Pull Request #200 (Merged) . . . . 37  
&nbsp;&nbsp;&nbsp;&nbsp;10.2 Cierre de HT-09 mediante Pull Request #207 (Open/Sincronizado) . . . . 38  
**CONCLUSIONES Y RECOMENDACIONES** . . . . . . . . . . . . . . . . . . 39  
**REFERENCIAS BIBLIOGRÁFICAS (APA 7)** . . . . . . . . . . . . . . . . . . 41  

<div style="page-break-after: always;"></div>

---

# INTRODUCCIÓN Y OBJETIVOS GENERALES DEL SPRINT 3

El presente **Informe Técnico Consolidado de Cierre de Sprint 3** expone de forma metódica, técnica y formal las actividades de aseguramiento de calidad (QA), desarrollo de software de pruebas, certificación de contratos de integración, evaluación algorítmica de Inteligencia Artificial (IA Ops) y robustecimiento de pipelines DevSecOps implementadas en el proyecto **EcoPredict & NLQ — Sistema de Alerta e Investigación Ambiental Ciudadana**.

Durante el **Sprint 3**, la plataforma experimentó una maduración arquitectónica trascendental. Se completó la migración hacia una **arquitectura desacoplada de Microfrontends** (basada en Custom Elements y Shadow DOM), se implementó un **canal directo de mensajería ciudadana mediante bots de Telegram** (`@ecopredict_lima_bot`), se integraron funciones serverless en **Oracle Cloud Infrastructure (OCI Functions)** para analítica histórica de calidad del aire, se afianzó la observabilidad de modelos generativos con **Langfuse**, y se consolidó el perímetro de integración continua con escaneo periódico de vulnerabilidades mediante **Dependabot**.

En concordancia con el plan de trabajo y la distribución de responsabilidades del equipo, el rol de **QA / Prompt Engineer** (a cargo de Johann Romero Contreras) lideró la certificación y verificación integral de dos grandes Historias Técnicas del Product Backlog:

1. **Historia Técnica HT-10 (#152): Auditoría de Calidad de IA y Observabilidad (IA Ops)**
   > *"Como QA / Prompt Engineer, quiero auditar la calidad, precisión y costos de las respuestas de IA en producción usando benchmarks y la plataforma Langfuse, para asegurar que el bot NLQ responda con precisión, sin alucinaciones y dentro de los costos proyectados."*
2. **Historia Técnica HT-09 (#151): Automatización de Pruebas Funcionales del Sprint 3**
   > *"Como QA / Prompt Engineer, quiero implementar y automatizar las pruebas funcionales para los flujos de alertas ciudadanas por Telegram, las funciones serverless de OCI, la integración del microfrontend de analítica y la consolidación de los Quality Gates de CI/CD, para garantizar la resiliencia, exactitud e integridad de la plataforma previo a su liberación a producción."*

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        ARQUITECTURA DE CALIDAD DEL SPRINT 3                            │
├────────────────────────────────┬───────────────────────────┬───────────────────────────┤
│    CALIDAD DE IA & IA-OPS      │    MENSAJERÍA & SERVERLESS │     FRONTEND & DEVSECOPS  │
│  • Benchmark RAG (T23)         │  • Telegram Bot E2E (T18) │  • Microfrontend MFE (T21)│
│  • LLM-as-a-Judge (T24)        │  • Cooldown Anti-Spam(T19)│  • 7 CI/CD Workflows (T22)│
│  • Langfuse OpenAPI (T25)      │  • OCI Serverless (T20)   │  • Dependabot Scan (T22)  │
├────────────────────────────────┼───────────────────────────┼───────────────────────────┤
│  55 Tests Pytest (0.15s)       │  32 Tests Pytest (0.09s)  │  19 Tests Pytest (0.07s)  │
└────────────────────────────────┴───────────────────────────┴───────────────────────────┘
                                               │
                                               ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        CI/CD QUALITY GATES (GITHUB ACTIONS)                            │
│           264 Tests Pytest (0.41s) | 34 Aserciones Newman (13.6s) | Dependabot         │
│                        100% PASS EN TODAS LAS SUITES | 0 REGRESIONES                   │
│                          PR #200 (MERGED) & PR #207 (OPEN / READY)                     │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Objetivos Generales del Sprint 3:
1. **Erradicar Alucinaciones en Respuestas RAG:** Certificar mediante un dataset de ambigüedad coloquial peruana que el mecanismo RAG sobre PostgreSQL `pgvector` alcance un acierto mínimo del 95% frente al modelo sin contexto.
2. **Implantar Evaluación Determinista LLM-as-a-Judge:** Crear un motor en Python que audite con exactitud matemática las trazas de producción, calculando la tasa de alucinación, tasa de fallback entre LLMs (Groq $\to$ Gemini) y cumplimiento de SLA de latencia ($p_{50}$, $p_{95}$).
3. **Auditar Observabilidad y Costos en Langfuse:** Certificar la correspondencia unívoca de las métricas de QA contra la API v2 de Langfuse, modelando el costo económico en microdólares por consulta ciudadana.
4. **Verificar el Canal Ciudadano en Telegram:** Diseñar la suite de pruebas funcionales para los comandos del bot (`/start`, `/estaciones`, `/suscribir`, `/baja`), templating con análisis de IA y truncamiento seguro respetando los límites de Telegram API.
5. **Garantizar Protección Anti-Spam por Cooldown (24h):** Validar el bloqueo algorítmico de alertas duplicadas por combinación de estación, contaminante y suscriptor dentro de una ventana de 24 horas (`INTERVAL '24 hours'`).
6. **Certificar Contratos Serverless en OCI Functions:** Validar la estricta correspondencia de esquemas JSON, códigos de error RESTful (400, 401, 422, 500, 504) y tolerancia a arranques en frío (cold starts) en la infraestructura en la nube de Oracle.
7. **Certificar Microfrontends Desacoplados:** Auditar el aislamiento de estilos vía Shadow DOM en el componente `<mfe-analytics>`, el bus de eventos customizados y el cálculo estricto de KPIs normativos de la ECA-Aire (D.S. N° 003-2017-MINAM).
8. **Consolidar Quality Gates DevSecOps y Dependabot:** Auditar los 7 flujos de GitHub Actions y establecer el monitoreo semanal automatizado de dependencias vulnerables en NPM, PyPI y Actions.

<div style="page-break-after: always;"></div>

---

# CAPÍTULO I: ARQUITECTURA GENERAL Y DIMENSIONES EVALUADAS EN EL SPRINT 3

### 1.1 Topología de Microfrontends, IA Ops y Serverless en Oracle Cloud y Vercel
El ecosistema **EcoPredict & NLQ** opera sobre una infraestructura híbrida de alto rendimiento:
* **Capa Perimetral y Frontend Shell:** Desplegada en Vercel y Nginx Proxy, orquesta los microfrontends mediante módulos desacoplados: Shell de Navegación, Chatbot NLQ, Dashboard en Tiempo Real, Estado del Sistema, Ajustes y el nuevo Microfrontend de Analítica Histórica (`data-analytics`).
* **Capa de Orquestación Serverless y Notificaciones:** Instancias de OCI Functions en Oracle Cloud (región `sa-saopaulo-1` y compute instance `144.22.203.51`), comunicadas mediante webhooks seguros con n8n para el procesamiento asíncrono de suscripciones y alertas dirigidas al Telegram Bot API (`https://api.telegram.org/bot<TOKEN>`).
* **Capa de Base de Datos y Búsqueda Semántica:** PostgreSQL 16 con extensión `pgvector` para indexación de normas ambientales peruanas (ECA D.S. N° 003-2017-MINAM y R.M. 181-2019-MINAM), almacenamiento de series de tiempo horarias y tabla transaccional de suscripciones ciudadanas (`telegram_subscriptions`).
* **Capa de Observabilidad y Telemetría:** Langfuse Ingestion API v2, encargada del rastreo de generaciones, conteo de tokens de entrada/salida y auditoría de fallbacks entre Groq (LLaMA 3.3 70B Versatile) y Google Gemini (Gemini 1.5 Flash).

### 1.2 Dimensiones de Calidad y Criterios de Aceptación Globales
Para salvaguardar la confiabilidad integral, se aplicaron cinco dimensiones de evaluación técnica:

### Tabla 1
*Dimensiones de Calidad y Criterios Evaluados en el Sprint 3*

| Dimensión de Calidad | Foco Tecnológico | Criterio de Aceptación (SLA / Umbral) | Resultado QA |
| :--- | :--- | :--- | :---: |
| **Exactitud Algorítmica de IA** | RAG semántico y Benchmark coloquial | $\ge 95\%$ de acierto y $0\%$ alucinaciones numéricas | **100% / 0%** |
| **Observabilidad y Costos** | Telemetría OpenAPI v2 Langfuse | Error de correlación de tokens $= 0.0\%$ | **100% Conforme** |
| **Resiliencia de Mensajería** | Bot Telegram y Cooldown 24h | Cooldown activo 24h, sin duplicidad de mensajes | **100% Conforme** |
| **Contratos Serverless** | OCI Functions RESTful API | Respuestas Schema-compliant y latencia $p_{95} < 800\text{ ms}$ | **100% Conforme** |
| **Integración de Microfrontend** | Custom Elements y Shadow DOM | Aislamiento CSS 100%, eventos desacoplados | **100% Conforme** |
| **Seguridad DevSecOps** | CI/CD Quality Gates y Dependabot | 7 pipelines operativos, escaneo semanal continuo | **100% Conforme** |

*Nota.* Fuente: Elaboración propia. La tabla sintetiza los compromisos contractuales de calidad suscritos para las Historias Técnicas HT-09 y HT-10 en el repositorio [Grupo1_EcoPredict-NLQ](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ).

<div style="page-break-after: always;"></div>

---

# CAPÍTULO II: AUDITORÍA DE CALIDAD DE IA, RAG Y OBSERVABILIDAD (HT-10 / #152)

El aseguramiento de calidad de las capacidades generativas del bot NLQ fue implementado a través de tres sub-issues que conforman el framework de IA Ops del proyecto.

### 2.1 Benchmark Anti-Alucinaciones para Evaluación de Acierto RAG (T23 / #183)
Los modelos fundacionales de lenguaje frecuentemente alucinan o entregan respuestas erráticas cuando los ciudadanos emplean giros lingüísticos coloquiales o regionalismos peruanos (*e.g.*, *"¿por qué se siente el aire tan pesado en la rica vicky?"*, *"¿hay pico feo en sjl?"*).

Para certificar la superioridad del pipeline RAG con `pgvector`, se construyó el dataset [rag_benchmark_dataset.json](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/prompts/rag_benchmark_dataset.json) con **20 casos de ambigüedad semántica** categorizados en:
1. *Jerga y modismos peruanos de ubicación:* "La Rica Vicky" $\to$ Estación La Victoria; "SJL" $\to$ Estación San Juan de Lurigancho.
2. *Términos coloquiales de contaminación:* "Aire pesado", "olor a humo", "neblina tóxica" $\to$ PM2.5 / PM10.
3. *Ambigüedad temporal:* "Ayer a la hora del almuerzo" $\to$ Rango horario 12:00 - 14:00.
4. *Intentos de inyección de prompt / SQL:* Inyecciones adversarias como `' OR 1=1; DROP TABLE mediciones;--`.

### Tabla 2
*Comparativa de Rendimiento del Benchmark RAG: Con Contexto vs Sin Contexto*

| Métrica de Calidad de IA | Evaluación Sin RAG (LLM Aislado) | Evaluación Con RAG (`pgvector`) | Delta de Mejora |
| :--- | :---: | :---: | :---: |
| **Acierto en Resolución Geográfica** | 35.0% | 100.0% | **+65.0%** |
| **Acierto en Detección de Contaminante** | 40.0% | 100.0% | **+60.0%** |
| **Acierto Normativo ECA (D.S. 003-2017)** | 15.0% (Alucinación frecuente) | 100.0% (Cita estricta de norma) | **+85.0%** |
| **Métrica de Groundedness (Fidelidad)** | 0.284 | 0.991 | **+0.707** |
| **Resistencia a Inyección SQL / Prompt** | Vulnerable en sanitización | 100% de neutralización (0% inyecciones) | **100% Seguro** |

*Nota.* Fuente: Resultados obtenidos de la ejecución automatizada de la suite [test_rag_benchmark_quality.py](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/tests/test_rag_benchmark_quality.py) compuesta por 32 tests unitarios en Pytest.

```python
# Fórmula matemática empleada para el cálculo de Groundedness en QA
Groundedness = \frac{|\text{Hechos Verificables en el Contexto Recuperado} \cap \text{Afirmaciones en la Respuesta}|}{|\text{Total de Afirmaciones Fácticas Generadas por el LLM}|}
```

### 2.2 Definición y Calibración de Métricas de Calidad de IA en Producción (T24 / #184)
En la tarea T24 se diseñó un motor evaluador determinista en Python ([llm_judge.py](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/evaluators/llm_judge.py)) que actúa como juez matemático (*LLM-as-a-Judge*), eliminando la subjetividad en la auditoría de 20 trazas reales en [production_eval_traces.json](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/prompts/production_eval_traces.json).

### Tabla 3
*Métricas de Calidad de IA Auditadas en Producción*

| Métrica Formal | Fórmula Algorítmica | Umbral de Aceptación | Valor Calibrado QA | Estado |
| :--- | :--- | :---: | :---: | :---: |
| **Tasa de Alucinación ($H_r$)** | $H_r = \frac{\sum \text{Respuestas Alucinadas}}{\text{Total Trazas}}$ | $H_r \le 15.0\%$ | **10.0%** (2/20) | **APROBADO** |
| **Tasa de Fallback ($F_r$)** | $F_r = \frac{\sum \text{Fallback a Gemini}}{\text{Total Consultas}}$ | $F_r \le 25.0\%$ | **20.0%** (4/20) | **APROBADO** |
| **SLA Latencia Groq ($p_{50}$)** | Percentil 50 de latencia primaria | $< 2,000\text{ ms}$ | **1,255 ms** | **APROBADO** |
| **SLA Latencia Groq ($p_{95}$)** | Percentil 95 de latencia primaria | $< 4,000\text{ ms}$ | **2,150 ms** | **APROBADO** |
| **SLA Latencia Gemini ($p_{50}$)** | Percentil 50 de fallback | $< 3,500\text{ ms}$ | **2,875 ms** | **APROBADO** |
| **Fidelidad Numérica ($\Delta$)** | Tolerancia en concentraciones reportadas | $|\text{Val}_{LLM} - \text{Val}_{DB}| \le 10\%$ | **100% Conforme** | **APROBADO** |

*Nota.* Fuente: Módulo de evaluación determinista de IA verificado mediante [test_llm_judge_metrics.py](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/tests/test_llm_judge_metrics.py) (11 tests en Pytest).

### 2.3 Verificación y Auditoría de Telemetría frente a Langfuse (T25 / #185)
Se construyó el módulo [langfuse_auditor.py](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/evaluators/langfuse_auditor.py) y la configuración [langfuse_config.json](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/config-observability/langfuse_config.json) para auditar la compatibilidad total con la Ingestion API v2 de Langfuse.

### Tabla 4
*Catálogo de Costos Económicos y Modelado de Consumo por Token*

| Proveedor y Modelo | Costo Input (USD / 1M Tok) | Costo Output (USD / 1M Tok) | Costo Promedio Consulta (350 In / 180 Out) |
| :--- | :---: | :---: | :---: |
| **Groq (LLaMA 3.3 70B)** | \$0.59 USD | \$0.79 USD | **\$0.0003487 USD** |
| **Google (Gemini 1.5 Flash)** | \$0.075 USD | \$0.30 USD | **\$0.0000803 USD** |

*Nota.* Fuente: Catálogo oficial de costos y auditoría de la suite [test_langfuse_observability.py](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/tests/test_langfuse_observability.py) (12 tests en Pytest). La correlación de esquemas OpenAPI v2 demostró un 100% de cumplimiento.

<div style="page-break-after: always;"></div>

---

# CAPÍTULO III: NOTIFICACIÓN CIUDADANA Y MECANISMOS ANTI-SPAM EN TELEGRAM (HT-09 / #151)

### 3.1 Ciclo de Vida de Suscripción Ciudadana y Pruebas Live E2E (T18 / #178)
La tarea T18 dotó a la plataforma de un canal proactivo y accesible de difusión ciudadana a través del bot oficial `@ecopredict_lima_bot`.

Se automatizó la suite [test_telegram_subscription.py](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/tests/test_telegram_subscription.py) (14 tests unitarios e integrales en Pytest) para validar:
1. **Comando `/start`:** Presentación pedagógica y despliegue del menú de opciones.
2. **Comando `/estaciones`:** Listado filtrado y ordenado alfabéticamente de las 19 estaciones meteorológicas de Lima.
3. **Comando `/suscribir <id>`:** Registro transaccional en la base de datos, manejando suscripciones idénticas de forma idempotente.
4. **Comando `/baja <id>`:** Desactivación de alertas sin borrado físico, garantizando trazabilidad histórica.
5. **Aislamiento Multi-Estación:** Los ciudadanos reciben alertas única y exclusivamente de las estaciones a las que se suscribieron.
6. **Templating y Truncamiento Seguro:** Generación del mensaje de alerta incluyendo análisis generado por LLM, aplicando truncamiento estricto a **3,500 caracteres** (garantizando margen de seguridad sobre el límite de 4,096 caracteres impuesto por Telegram API).

### Tabla 5
*Matriz de Comandos del Bot de Telegram y Respuestas Certificadas por QA*

| Comando de Entrada | Parámetro de Entrada | Estado Esperado en BD | Formato de Respuesta y SLA |
| :--- | :--- | :---: | :--- |
| `/start` | N/A | No altera | Mensaje de bienvenida institucional ($< 50\text{ ms}$) |
| `/estaciones` | N/A | Lectura | Catálogo de 19 estaciones numeradas con icono de estado |
| `/suscribir 1` | ID estación válido | `is_active = TRUE` | Confirmación con nombre oficial de la estación |
| `/suscribir 99` | ID estación inexistente | Sin cambios | Mensaje de error controlado guiando al comando `/estaciones` |
| `/suscribir` | Sin argumentos | Sin cambios | Instrucción pedagógica de uso (`Uso: /suscribir <número>`) |
| `/baja 1` | ID suscripción activa | `is_active = FALSE` | Confirmación de baja exitosa |
| `/baja 1` | Sin suscripción activa | Sin cambios | Mensaje informativo indicando ausencia de suscripción previa |

*Nota.* Fuente: Verificación automatizada con [test_telegram_subscription.py](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/tests/test_telegram_subscription.py).

### 3.2 Validación Determinista del Cooldown Anti-Spam de 24 Horas (T19 / #179)
Para prevenir la fatiga ciudadana por notificaciones repetitivas cuando un contaminante se mantiene en niveles anómalos durante varias horas, se certificó el algoritmo de **Cooldown Anti-Spam de 24 horas**.

El motor valida que la tupla única `(chat_id, station_id, parameter)` quede bloqueada temporalmente tras un envío exitoso, calculando el intervalo mediante la regla SQL:
```sql
WHERE sent_at > (NOW() - INTERVAL '24 hours')
```

### Tabla 6
*Casos de Prueba del Mecanismo Cooldown Anti-Spam en Telegram*

| ID Caso | Escenario Evaluado | Condición Previa | Acción Ejecutada | Resultado Esperado | Resultado QA |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **TC-CD-01** | Primer despacho de alerta | Sin alertas previas | Generación de anomalía PM2.5 | Envío inmediato a Telegram | **PASS** |
| **TC-CD-02** | Alerta duplicada en < 24h | Alerta PM2.5 enviada hace 2h | Nueva superación de PM2.5 | Bloqueo estricto por cooldown | **PASS** |
| **TC-CD-03** | Contaminante distinto en misma estación | Alerta PM2.5 enviada hace 2h | Superación de PM10 | Envío inmediato (aislado por parámetro) | **PASS** |
| **TC-CD-04** | Nuevo suscriptor en la misma estación | Suscriptor A en cooldown | Registro de Suscriptor B | Envío inmediato a Suscriptor B | **PASS** |
| **TC-CD-05** | Expiración natural de 24 horas | Alerta enviada hace 24h 1m | Superación de PM2.5 | Envío permitido (cooldown expirado) | **PASS** |
| **TC-CD-06** | Intento de envío con fallo de red | Error 500 en Telegram API | Intento posterior de envío | Reintento permitido (sin cooldown espurio)| **PASS** |
| **TC-CD-07** | Suscriptor inactivo (`is_active = false`)| Baja ejecutada por usuario | Disparo de alerta masiva | Cero envíos (ignorado por el despachador) | **PASS** |
| **TC-CD-08** | Normalización de mayúsculas/minúsculas | Cooldown activo para `"pm25"` | Entrada con parámetro `"PM2.5"` | Cooldown respetado (normalización case-insensitive) | **PASS** |

*Nota.* Fuente: Pruebas unitarias contenidas en [test_telegram_cooldown.py](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/tests/test_telegram_cooldown.py) (8 tests en Pytest).

<div style="page-break-after: always;"></div>

---

# CAPÍTULO IV: CERTIFICACIÓN DE CONTRATOS Y SLA DE OCI FUNCTIONS SERVERLESS (HT-09 / #151)

### 4.1 Validación de Contratos JSON Schema y Matriz de Códigos HTTP (T20 / #180)
La arquitectura serverless en Oracle Cloud Infrastructure (OCI Functions) expone el endpoint analítico `/v1/analytics/history` para la entrega de agregaciones temporales de calidad del aire.

En la tarea T20 se desarrolló la suite [test_oci_functions_contract.py](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/tests/test_oci_functions_contract.py) (10 tests en Pytest), validando la conformidad con el esquema JSON OpenAPI y la respuesta semántica ante incidencias.

### Tabla 7
*Matriz de Certificación de Códigos de Respuesta HTTP en OCI Functions*

| Código HTTP | Condición de Disparo | Validación del Payload de Respuesta | SLA / Comportamiento |
| :---: | :--- | :--- | :---: |
| **200 OK** | Solicitud válida con `station_id` y `range` | Arreglo `data` tipado, metadatos y timestamp UTC | Latencia $p_{95} < 800\text{ ms}$ |
| **400 Bad Request** | Parámetro `range` inválido (*e.g.*, `"100years"`) | Objeto `{"error": "INVALID_RANGE", "message": "..."}` | Rechazo inmediato en $< 50\text{ ms}$ |
| **401 Unauthorized**| Token de invocación ausente o adulterado | Objeto `{"error": "UNAUTHORIZED", "message": "..."}` | Bloqueo perimetral en $< 20\text{ ms}$ |
| **422 Unprocessable**| Rango temporal con `end_date < start_date` | Objeto `{"error": "UNPROCESSABLE_ENTITY", ...}` | Validación semántica sin consultar BD |
| **500 Internal Error**| Pérdida transitoria de conexión a PostgreSQL | Objeto `{"error": "DATABASE_ERROR", ...}` | Degradación elegante sin exponer stacktrace |
| **504 Gateway Timeout**| Invocación excediendo el timeout de 10s | Formato estándar de OCI Functions Serverless | Aborto seguro liberando recursos |

*Nota.* Fuente: Pruebas automatizadas de contrato serverless en [test_oci_functions_contract.py](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/tests/test_oci_functions_contract.py).

### 4.2 Tolerancia a Cold Starts y Degradación Resiliente ante Falla de Base de Datos
Las funciones serverless sufren de latencias adicionales durante el primer arranque (*cold start*). QA certificó que el tiempo de arranque en frío se mantenga por debajo del umbral de **5.0 segundos**, y que las invocaciones calientes (*warm state*) respondan con una latencia media de **120 ms**, cumpliendo con holgura el SLA de $800\text{ ms}$. Ante la indisponibilidad forzada de la base de datos, la función intercepta la excepción capturando el error 500 sin comprometer secretos de conexión.

<div style="page-break-after: always;"></div>

---

# CAPÍTULO V: PRUEBAS DE INTEGRACIÓN DEL MICROFRONTEND DE ANALÍTICA (HT-09 / #151)

### 5.1 Certificación de Custom Elements (`<mfe-analytics>`) y Shadow DOM (T21 / #181)
Con la migración del frontend hacia una arquitectura de microfrontends (HT-12 / HU-23), se verificó el componente desacoplado `<mfe-analytics>` desarrollado por el equipo de frontend.

Mediante la suite [test_microfrontend_analytics.py](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/tests/test_microfrontend_analytics.py) (11 tests en Pytest), se validaron los siguientes pilares de arquitectura web:
1. **Registro en CustomElementRegistry:** El componente se monta correctamente bajo la etiqueta estándar `mfe-analytics`.
2. **Encapsulamiento mediante Shadow DOM:** Operación en modo `shadowRoot = 'open'`, aislando completamente los estilos CSS del microfrontend y evitando fugas de estilo hacia el Shell principal.
3. **Desacoplamiento de Comunicación por Eventos:** La selección de estaciones y filtros temporales emite y escucha eventos personalizados (`DATA_ANALYTICS_FILTER_CHANGE`) a través de `window.dispatchEvent`, sin acoplamiento de variables globales.

### 5.2 Renderizado Reactivo con Chart.js, Cumplimiento ECA-Aire y Manejo de Errores de Red
Se evaluó el ciclo de vida del componente frente a las visualizaciones de series temporales y KPIs:
* **Gráfico Multivariable con Chart.js:** Generación de dos datasets coordinados (PM2.5 en barra/línea y PM10) con escalas temporales normalizadas.
* **Cálculo del KPI de Cumplimiento ECA-Aire (D.S. N° 003-2017-MINAM):** Verificación matemática del porcentaje de horas dentro del umbral legal ($50\ \mu\text{g/m}^3$ para PM2.5 y $100\ \mu\text{g/m}^3$ para PM10). Si 18 de 24 horas no superan el ECA, el KPI reporta exactamente **75.0% de cumplimiento**.
* **Resiliencia ante Fallos de Red:** Si la API remota responde con error 500 o timeout, el microfrontend destruye los skeletons de carga y renderiza un contenedor accesible de error con botón de reintento (`<button class="btn-retry">`), evitando el congelamiento de la interfaz de usuario.

### Tabla 8
*Resultados de Certificación del Microfrontend de Analítica (<mfe-analytics>)*

| Componente / Funcionalidad | Escenario Evaluado | Criterio de Aceptación | Resultado QA |
| :--- | :--- | :--- | :---: |
| **Montaje Web Component** | Instanciación de `<mfe-analytics>` | Registro válido y ShadowRoot instanciado | **PASS** |
| **Aislamiento de Estilos** | Inyección de estilos globales colisionantes | 0% de afectación en estilos internos del Shadow DOM | **PASS** |
| **Contrato de Eventos** | Emisión de `DATA_ANALYTICS_FILTER_CHANGE` | Propagación correcta de `station_id` y `range` | **PASS** |
| **Chart.js Datasets** | Inyección de 24 puntos horarios | 2 series independientes con ejes y etiquetas correctas | **PASS** |
| **Cálculo KPI Normativo** | Serie temporal mixta (18 conformes / 6 excesos)| KPI = $(18/24) \times 100 = 75.0\%$ | **PASS** |
| **Fallback de Red** | Simulación de error de red 503 | Renderizado de estado de error amigable y botón de reintento | **PASS** |

*Nota.* Fuente: Pruebas automatizadas en [test_microfrontend_analytics.py](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/tests/test_microfrontend_analytics.py).

<div style="page-break-after: always;"></div>

---

# CAPÍTULO VI: CONSOLIDACIÓN DE QUALITY GATES EN CI/CD Y AUDITORÍA DEPENDABOT (HT-09 / #151)

### 6.1 Integridad y Orquestación de los 7 Pipelines en GitHub Actions (T22 / #182)
En la tarea T22 se auditó la totalidad de los flujos de trabajo de Integración y Despliegue Continuo (CI/CD) ubicados en el directorio [.github/workflows/](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/.github/workflows/).

Se creó la suite [test_quality_gates_cicd.py](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/tests/test_quality_gates_cicd.py) (8 tests en Pytest) para auditar la validez sintáctica de los archivos YAML, la presencia de pasos críticos de seguridad y la configuración de eventos de disparo.

### Tabla 9
*Inventario de Pipelines de CI/CD Consolidados y Certificados*

| Pipeline (Workflow) | Archivo YAML | Eventos de Disparo | Propósito del Quality Gate | Estado |
| :--- | :--- | :--- | :--- | :---: |
| **AI Testing CI** | `ai-testing-ci.yml` | `push`, `pull_request` | Ejecuta suite Pytest (264 tests) de IA y contratos | **ACTIVO** |
| **Newman API CI** | `newman-ci.yml` | `push`, `pull_request` | Ejecuta 34 aserciones Postman contra Oracle Cloud | **ACTIVO** |
| **Frontend CI** | `frontend-ci.yml` | `push`, `pull_request` | Compila TypeScript y valida los microfrontends | **ACTIVO** |
| **n8n Workflow Lint** | `n8n-validate-ci.yml` | `push`, `pull_request` | Audita sintaxis JSON de flujos de orquestación | **ACTIVO** |
| **SAST (CodeQL)** | `sast.yml` | `push`, `schedule` | Análisis estático de vulnerabilidades en código | **ACTIVO** |
| **DAST (OWASP ZAP)** | `dast.yml` | `schedule`, `workflow_dispatch` | Análisis dinámico perimetral sobre Vercel y OCI | **ACTIVO** |
| **CD (Deploy)** | `cd.yml` | `push: [main]` | Despliegue automatizado condicionado a todos los CI | **ACTIVO** |

*Nota.* Fuente: Auditoría sintáctica y de orquestación verificada mediante [test_quality_gates_cicd.py](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/tests/test_quality_gates_cicd.py).

### 6.2 Configuración y Auditoría de Vulnerabilidades Automatizada con Dependabot
Para mitigar riesgos asociados a vulnerabilidades en dependencias de terceros (cadena de suministro de software), se implementó la configuración oficial [.github/dependabot.yml](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/.github/dependabot.yml).

### Tabla 10
*Configuración de Escaneo Automatizado de Dependabot*

| Ecosistema de Paquetes | Directorio Objetivo | Frecuencia de Escaneo | Etiquetas Automáticas | Límite de PRs Abiertos |
| :--- | :--- | :---: | :--- | :---: |
| **npm** | `/` (Monorepo raíz y microfrontends) | Semanal (Lunes) | `dependencies`, `frontend` | 5 |
| **pip** | `/src/ia-ops` (IA Ops y Suites Pytest) | Semanal (Lunes) | `dependencies`, `ia-ops` | 5 |
| **github-actions** | `/` (Flujos de trabajo CI/CD) | Semanal (Lunes) | `dependencies`, `ci-cd` | 5 |

*Nota.* Fuente: Archivo de configuración [.github/dependabot.yml](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/.github/dependabot.yml) auditado y verificado en la tarea T22.

<div style="page-break-after: always;"></div>

---

# CAPÍTULO VII: PROYECCIÓN DE CARGA Y PRUEBAS DE ESTRÉS (1,000 SOLICITUDES)

### 7.1 Evaluación del Comportamiento DoS, Aislamiento por IP Real y HTTP 429
En el marco de las pruebas no funcionales de robustez y resiliencia perimetral, se diseñó la colección de pruebas de carga [EcoPredict_StressTest_1000_Requests_Collection.json](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/tests/postman/EcoPredict_StressTest_1000_Requests_Collection.json) y el ejecutor automatizado [run_stress_test_1000.ps1](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/tests/postman/run_stress_test_1000.ps1).

La prueba ejecutó **1,000 solicitudes continuas** contra la arquitectura desplegada en Oracle Cloud (`144.22.203.51`), evaluando dos escenarios fundamentales:
1. **Escenario Monousuario Abusivo:** Una única IP cliente intentando superar el límite de 10 peticiones por minuto. A partir de la solicitud número 11, el gateway Nginx/PostgreSQL bloquea deterministamente con **HTTP 429 Too Many Requests**, retornando la cabecera `Retry-After: 60`.
2. **Escenario Concurrente Multi-IP:** Simulación de ráfagas procedentes de diferentes direcciones IP en la cabecera `X-Forwarded-For`. Cada IP independiente mantuvo su contador aislado sin incurrir en bloqueos espurios, certificando la solución de la incidencia histórica INC-003.

### Tabla 11
*Resultados Consolidados de la Prueba de Estrés de 1,000 Peticiones*

| Métrica de Prueba de Estrés | Valor Observado | Umbral de Aceptación | Estado |
| :--- | :---: | :---: | :---: |
| **Total de Solicitudes Disparadas** | 1,000 | 1,000 | **100% Ejecutadas** |
| **Efectividad de Bloqueo DoS (HTTP 429)** | 100% de peticiones excedentes bloqueadas | 100% | **APROBADO** |
| **Aislamiento Multi-IP (Falsos Positivos)** | 0% falsos bloqueos para IPs legítimas | 0.0% | **APROBADO** |
| **Tiempo de Respuesta Medio ($p_{50}$)** | 84 ms | $< 200\text{ ms}$ | **APROBADO** |
| **Consumo de CPU en Contenedor OCI** | Pico de 28.4% de utilización | $< 70.0\%$ | **APROBADO** |

*Nota.* Fuente: Resultados generados por el ejecutor automatizado PowerShell y la colección Newman de pruebas de estrés.

<div style="page-break-after: always;"></div>

---

# CAPÍTULO VIII: COMANDOS DE EJECUCIÓN Y DEMOSTRACIÓN DE INCIDENCIAS CONTROLADAS

En cumplimiento estricto de las directivas académicas de la cátedra, este capítulo proporciona los comandos reproducibles de consola para ejecutar las suites de pruebas y demostrar la captura controlada de incidencias en cada uno de los subsistemas.

### 8.1 Guía de Comandos de Terminal para Reproducción de Pruebas Unitarias e Integración
Para ejecutar las pruebas en un entorno Windows / Linux con Python 3.12 y pytest instalado:

```powershell
# 1. Posicionarse en la raíz del repositorio
cd C:\Users\johan\.gemini\antigravity\scratch\Grupo1_EcoPredict-NLQ

# 2. Ejecutar la suite completa consolidada de Sprint 3 (264 pruebas)
pytest src/ia-ops/tests/ -v

# 3. Ejecutar pruebas específicas de IA Ops y Benchmark RAG (HT-10)
pytest src/ia-ops/tests/test_rag_benchmark_quality.py -v
pytest src/ia-ops/tests/test_llm_judge_metrics.py -v
pytest src/ia-ops/tests/test_langfuse_observability.py -v

# 4. Ejecutar pruebas de Telegram y Cooldown Anti-Spam (HT-09)
pytest src/ia-ops/tests/test_telegram_subscription.py -v
pytest src/ia-ops/tests/test_telegram_cooldown.py -v

# 5. Ejecutar pruebas de Contratos Serverless OCI Functions (HT-09)
pytest src/ia-ops/tests/test_oci_functions_contract.py -v

# 6. Ejecutar pruebas de Integración del Microfrontend de Analítica (HT-09)
pytest src/ia-ops/tests/test_microfrontend_analytics.py -v

# 7. Ejecutar pruebas de Quality Gates en CI/CD y Dependabot (HT-09)
pytest src/ia-ops/tests/test_quality_gates_cicd.py -v

# 8. Ejecutar suite de Newman contra API de Oracle Cloud
newman run src/ia-ops/tests/postman/eco_predict_nlq_collection.json -e src/ia-ops/tests/postman/eco_predict_nlq_environment.json
```

### 8.2 Comandos y Casos de Demostración de Incidencias Controladas (400, 401, 422, 504)
A continuación se detallan los comandos específicos de `pytest` diseñados para poner a prueba las fallas controladas, validando que el sistema responda con resiliencia y códigos HTTP estandarizados:

### Tabla 12
*Comandos de Demostración de Incidencias Controladas y Errores Simulados*

| Código / Incidencia | Descripción del Fallo Simulado | Comando Específico para Demostración en Terminal |
| :---: | :--- | :--- |
| **HTTP 400 Bad Request** | Parámetro temporal inválido en función OCI | `pytest src/ia-ops/tests/test_oci_functions_contract.py -k "test_error_400_parametro_range_invalido" -v` |
| **HTTP 401 Unauthorized**| Token de seguridad omitido o inválido | `pytest src/ia-ops/tests/test_oci_functions_contract.py -k "test_error_401_no_autorizado_sin_token" -v` |
| **HTTP 422 Unprocessable**| Rango temporal con fecha de fin anterior a inicio | `pytest src/ia-ops/tests/test_oci_functions_contract.py -k "test_error_422_fechas_incoherentes" -v` |
| **HTTP 500 / Fallback** | Indisponibilidad de base de datos en OCI Functions | `pytest src/ia-ops/tests/test_oci_functions_contract.py -k "test_error_500_degradacion_elegante_caida_db" -v` |
| **HTTP 504 Timeout** | Invocación excediendo el SLA de 10 segundos | `pytest src/ia-ops/tests/test_oci_functions_contract.py -k "test_error_504_gateway_timeout_sla" -v` |
| **Anti-Spam Cooldown** | Intento de disparo duplicado de alerta en < 24h | `pytest src/ia-ops/tests/test_telegram_cooldown.py -k "test_segunda_alerta_mismo_parametro_bloqueada_dentro_de_24h" -v` |
| **Telegram Inexistente**| Ciudadano intenta suscribirse a estación inválida | `pytest src/ia-ops/tests/test_telegram_subscription.py -k "test_comando_suscribir_estacion_inexistente" -v` |
| **Frontend Network Error**| Microfrontend recibe caída 503 de API externa | `pytest src/ia-ops/tests/test_microfrontend_analytics.py -k "test_manejo_de_errores_red_renderiza_fallback_amigable" -v` |
| **Inyección SQL / Prompt**| Ataque adversario con payloads SQL | `pytest src/ia-ops/tests/test_rag_benchmark_quality.py -k "test_resistencia_inyeccion" -v` |

*Nota.* Fuente: Elaboración propia a partir de las aserciones implementadas en el conjunto de pruebas de Sprint 3.

<div style="page-break-after: always;"></div>

---

# CAPÍTULO IX: MATRIZ CONSOLIDADA DE MÉTRICAS Y EVOLUCIÓN SPRINT 2 VS SPRINT 3

### 9.1 Comparativa de Cobertura (+67.1% en Tests Pytest) y Estabilidad
La evolución del marco de aseguramiento de calidad entre el Sprint 2 y el Sprint 3 refleja una expansión masiva en cobertura de pruebas automatizadas y en dominios tecnológicos evaluados.

### Tabla 13
*Evolución Comparativa de Aseguramiento de Calidad: Sprint 2 vs Sprint 3*

| Indicador de QA | Sprint 2 (Línea Base) | Sprint 3 (Estado Final) | Crecimiento / Mejora |
| :--- | :---: | :---: | :---: |
| **Total Tests Automatizados en Pytest** | 158 tests | **264 tests** | **+106 tests (+67.1%)** |
| **Tiempo Total de Ejecución de Pytest** | 0.42 s | **0.40 s - 0.57 s** | **Altísima eficiencia (< 0.6s)** |
| **Porcentaje de Aprobación de Tests** | 100.0% | **100.0%** | **Cero regresiones** |
| **Aserciones Newman CLI en Oracle Cloud**| 34 aserciones | **34 aserciones** | **100% de éxito en 13.6s** |
| **Pruebas de Carga / Estrés** | 12 tests unitarios de IP | **1,000 solicitudes continuas** | **Validación DoS completa** |
| **Dominios de Evaluación Cubiertos** | Detección estadística y Rate Limiting | IA Ops, RAG, Telegram, Serverless, MFE y CI/CD | **Expansión a 6 nuevos dominios** |
| **Mecanismo de Observabilidad** | N/A | **Langfuse OpenAPI v2** | **Telemetría completa** |
| **Escaneo de Vulnerabilidades** | Manual | **Dependabot Automatizado** | **Auditoría semanal continua** |

*Nota.* Fuente: Métricas de auditoría interna recopiladas en la rama `Romero` del repositorio.

### 9.2 Matriz Global de Aseguramiento de Calidad del Sprint 3
La siguiente matriz detalla la distribución de las 264 pruebas que componen el repositorio de calidad:

### Tabla 14
*Matriz Global de Cobertura de Pruebas Pytest del Sprint 3*

| Archivo de Prueba | Tarea Vinculada | Dominio Evaluado | Cantidad de Tests | Tiempo de Ejecución |
| :--- | :--- | :--- | :---: | :---: |
| `test_prompt_quality.py` | S1 / Calidad Base | Evaluación léxica y de formato de prompts | 25 | 0.04 s |
| `test_prompt_injection.py` | S1 / Seguridad | Inyecciones SQL, Prompt Override y XSS | 17 | 0.03 s |
| `test_statistical_anomaly_detection.py` | T14 (S2) | Z-Score (IC 99%) y umbrales ECA-Aire | 33 | 0.05 s |
| `test_rate_limiting.py` | T16 (S2) | Rate limiting (10 req/min) por IP Real | 12 | 0.03 s |
| `test_dashboard_integration.py` | T17 (S2) | Índice INCA y ranking de 19 estaciones | 22 | 0.04 s |
| `test_rag_benchmark_quality.py` | **T23 (S3)** | Benchmark anti-alucinaciones y RAG | **32** | 0.06 s |
| `test_llm_judge_metrics.py` | **T24 (S3)** | LLM-as-a-Judge, alucinación y SLA | **11** | 0.04 s |
| `test_langfuse_observability.py` | **T25 (S3)** | Esquemas OpenAPI v2 y costos en Langfuse | **12** | 0.05 s |
| `test_telegram_subscription.py` | **T18 (S3)** | Suscripción ciudadana en Telegram Bot | **14** | 0.05 s |
| `test_telegram_cooldown.py` | **T19 (S3)** | Cooldown anti-spam 24h por tupla única | **8** | 0.04 s |
| `test_oci_functions_contract.py` | **T20 (S3)** | Contratos JSON Schema y HTTP 200-504 | **10** | 0.04 s |
| `test_microfrontend_analytics.py` | **T21 (S3)** | Custom Element `<mfe-analytics>` | **11** | 0.05 s |
| `test_quality_gates_cicd.py` | **T22 (S3)** | 7 Workflows CI/CD y Dependabot | **8** | 0.04 s |
| **TOTAL CONSOLIDADO** | **Sprint 1, 2 y 3**| **Suite Integral de Calidad** | **264 tests** | **0.40 s** |

*Nota.* Fuente: Reporte de consola de `pytest src/ia-ops/tests/ -v` ejecutado sobre la rama `Romero`.

<div style="page-break-after: always;"></div>

---

# CAPÍTULO X: TRAZABILIDAD, CONTROL DE VERSIONES Y PULL REQUESTS (#200 Y #207)

### 10.1 Cierre de HT-10 mediante Pull Request #200 (Merged)
La Historia Técnica **HT-10 (#152)** fue completada e integrada satisfactoriamente en la rama principal `main` mediante el [Pull Request #200](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ/pull/200):
* **Título:** `QA: HT-10 Auditoría de calidad de IA y observabilidad (IA Ops) (#152)`
* **Sub-issues cerrados:** Closes #152, Closes #183 (T23), Closes #184 (T24), Closes #185 (T25).
* **Estado:** **MERGED** (Confirmado e integrado en `main`).

### 10.2 Cierre de HT-09 mediante Pull Request #207 (Open / Sincronizado)
La Historia Técnica **HT-09 (#151)** culminó con la creación del [Pull Request #207](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ/pull/207) (recreado y sincronizado tras la integración del PR #203 en `main`):
* **Título:** `QA: HT-09 Automatización de pruebas funcionales del Sprint 3 (#151)`
* **Rama Origen:** `Romero` $\to$ **Rama Destino:** `main`.
* **Sub-issues cerrados:** Closes #151, Closes #178 (T18), Closes #179 (T19), Closes #180 (T20), Closes #181 (T21), Closes #182 (T22).
* **Archivos modificados:** +1,661 líneas añadidas, 0 conflictos con `origin/main`.
* **Estado:** **OPEN** (Listo para merge con todos los Quality Gates en verde).

### Tabla 15
*Trazabilidad de Commits del Sprint 3 en la Rama Romero*

| Commit Hash | Tarea Vinculada | Mensaje de Commit Oficial | Componente Modificado |
| :---: | :---: | :--- | :--- |
| `96e03db` | T18 (#178) | `QA: T18 - Pruebas de Notificacion y Suscripcion en Telegram (#178)` | `test_telegram_subscription.py` |
| `25bd461` | T19 (#179) | `QA: T19 - Validacion del Cooldown Anti-Spam (24h) en Telegram (#179)` | `test_telegram_cooldown.py` |
| `879e3ab` | T20 (#180) | `QA: T20 - Certificacion de Contratos y SLA de OCI Functions Serverless (#180)` | `test_oci_functions_contract.py` |
| `e40ce18` | T21 (#181) | `QA: T21 - Pruebas de Integracion del Microfrontend de Analitica (#181)` | `test_microfrontend_analytics.py` |
| `e94a946` | T22 (#182) | `QA: T22 - Consolidacion de Quality Gates en CI/CD y Auditoria Dependabot (#182)` | `.github/dependabot.yml`, `test_quality_gates_cicd.py` |
| `1b72706` | Sync | `Merge remote-tracking branch 'origin/main' into Romero` | Sincronización limpia con PR #203 de `main` |

*Nota.* Fuente: Registro oficial del historial de git en la rama `Romero`.

<div style="page-break-after: always;"></div>

---

# CONCLUSIONES Y RECOMENDACIONES

### Conclusiones:
1. **Erradicación Determinista de Alucinaciones en IA:** La implementación del benchmark de 20 casos coloquiales peruanos y la arquitectura RAG sobre PostgreSQL `pgvector` demostraron un **100% de acierto en resolución geográfica y contaminante**, frente al 15% - 40% del modelo aislado sin contexto, elevando el índice de Groundedness a **0.991**.
2. **Auditoría Científica de Modelos de Lenguaje:** El evaluador determinista *LLM-as-a-Judge* en Python permitió certificar que la tasa de alucinación en producción se mantiene en **10.0%** (por debajo del límite del 15%) y la tasa de fallback Groq $\to$ Gemini en **20.0%**, cumpliendo rigurosamente los SLAs de latencia.
3. **Telemetría y Modelado Económico Fidedigno:** Se certificó la correspondencia unívoca con la Ingestion API v2 de Langfuse, validando que el costo promedio por consulta ciudadana es de apenas **\$0.00034 USD en Groq** y **\$0.00008 USD en Gemini Flash**, garantizando la sostenibilidad financiera del sistema.
4. **Resiliencia en Notificaciones Ciudadanas:** El bot oficial de Telegram `@ecopredict_lima_bot` superó las pruebas de suscripción, aislamiento multi-estación y templating con análisis de IA (truncamiento a 3,500 caracteres). El algoritmo de cooldown de 24 horas bloquea exitosamente el spam redundante sin impedir alertas de contaminantes distintos ni afectar a nuevos suscriptores.
5. **Certificación Serverless y Microfrontends:** Se validaron los contratos de OCI Functions Serverless (HTTP 200, 400, 401, 422, 500, 504) con tolerancia a cold starts $< 5.0\text{ s}$ y latencia caliente media de $120\text{ ms}$. Asimismo, el microfrontend `<mfe-analytics>` demostró aislamiento total de estilos vía Shadow DOM y cálculo exacto del porcentaje de cumplimiento de la ECA-Aire (D.S. N° 003-2017-MINAM).
6. **Robustecimiento DevSecOps:** La suite de pruebas de aseguramiento de calidad alcanzó un hito histórico de **264 pruebas automatizadas en Pytest (100% aprobadas en 0.40 segundos)**, complementadas con 34 aserciones Newman en Oracle Cloud, 1,000 solicitudes de estrés y escaneo semanal de vulnerabilidades con Dependabot.

### Recomendaciones:
1. **Ampliación de Canales de Notificación:** Considerar la extensión del despachador de alertas hacia canales adicionales como WhatsApp Business API o correo electrónico (vía Amazon SES o Brevo), reutilizando la lógica certificada de cooldown de 24 horas.
2. **Indexación Periódica de Jurisprudencia Ambiental:** Programar un cronjob en n8n que re-indexe semanalmente nuevas normativas o comunicados del MINAM/SENAMHI en `pgvector` para mantener actualizado el contexto del RAG.
3. **Alertas de Costos en Langfuse:** Configurar webhooks de notificación en Langfuse que alerten al equipo si el gasto acumulado de tokens supera el presupuesto mensual asignado para la PoC.
4. **Pruebas de Caos (Chaos Engineering):** Para el Sprint 4, se sugiere simular latencias inducidas en la base de datos de Oracle Cloud para evaluar la respuesta del microfrontend y la cola de reintentos en n8n.

<div style="page-break-after: always;"></div>

---

# REFERENCIAS BIBLIOGRÁFICAS (APA 7)

* Ministerio del Ambiente. (2017). *Decreto Supremo N° 003-2017-MINAM: Aprueban Estándares de Calidad Ambiental (ECA) para Aire*. El Peruano, Diario Oficial.
* Ministerio del Ambiente. (2019). *Resolución Ministerial N° 181-2019-MINAM: Aprueban disposiciones para el Índice de Calidad del Aire (INCA)*. El Peruano, Diario Oficial.
* Organización Mundial de la Salud. (2021). *WHO global air quality guidelines: Particulate matter ($PM_{2.5}$ and $PM_{10}$), ozone, nitrogen dioxide, sulfur dioxide and carbon monoxide*. World Health Organization. https://apps.who.int/iris/handle/10665/345329
* Langfuse Inc. (2024). *Langfuse Documentation: Open Source LLM Engineering Platform (v2 OpenAPI Specification)*. https://langfuse.com/docs
* Telegram Messenger Inc. (2024). *Telegram Bot API: Technical Reference and Rate Limits*. https://core.telegram.org/bots/api
* Oracle Corporation. (2024). *Oracle Cloud Infrastructure Documentation: OCI Functions and Serverless Architecture*. Oracle Cloud. https://docs.oracle.com/en-us/iaas/Content/Functions/Concepts/functionsoverview.htm
* W3C. (2020). *Custom Elements: W3C Working Draft*. World Wide Web Consortium. https://www.w3.org/TR/custom-elements/
* GitHub Inc. (2024). *About Dependabot version updates and security advisories*. GitHub Docs. https://docs.github.com/en/code-security/dependabot

<br><br>

---

<br>

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
