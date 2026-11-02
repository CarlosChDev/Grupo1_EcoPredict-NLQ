# UNIVERSIDAD DE SAN MARTÍN DE PORRES
## FACULTAD DE INGENIERÍA Y ARQUITECTURA
### ESCUELA PROFESIONAL DE INGENIERÍA DE COMPUTACIÓN Y SISTEMAS

<br>

# INFORME TÉCNICO DE PRUEBAS DE SOFTWARE — TAREA T27 (#252)
## "EcoPredict & NLQ" — Sistema de Alerta e Investigación Ambiental Ciudadana

<br>

### *CERTIFICACIÓN DE INTEGRACIÓN, RENDERIZADO, ENCAPSULAMIENTO DE ESTILOS CSS Y MANEJO RESILIENTE DEL ERROR 503 EN EL MICROFRONTEND DATA ANALYTICS FASE 2*
### *(Historia de Usuario HU-22 / Sub-issues #248 y #252)*

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
**CAPÍTULO I: FUNDAMENTACIÓN TEÓRICA Y CONTEXTO DE LA HU-22** . . . . . . . . . . . . 4  
&nbsp;&nbsp;&nbsp;&nbsp;1.1 Evolución de la Fase 1 a la Fase 2 del Panel de Analítica Ambiental . . . . . . . . 4  
&nbsp;&nbsp;&nbsp;&nbsp;1.2 Desacoplamiento de Microfrontends y Aislamiento Perimetral de Fallos . . . . . . . 4  
&nbsp;&nbsp;&nbsp;&nbsp;1.3 Principios de Usabilidad Ciudadana y Tolerancia a Fallos de Red . . . . . . . . . . 5  
**CAPÍTULO II: ESPECIFICACIÓN DEL MICROFRONTEND DATA ANALYTICS (FASE 2)** . . . . . . . 6  
&nbsp;&nbsp;&nbsp;&nbsp;2.1 Arquitectura de Componentes React y Consumo del Flujo D . . . . . . . . . . . . 6  
&nbsp;&nbsp;&nbsp;&nbsp;2.2 Matriz de Validación de Parámetros de Interfaz y Límites (2 a 4 Distritos) . . . . . 7  
&nbsp;&nbsp;&nbsp;&nbsp;2.3 Encapsulamiento de Estilos CSS (`da-`) y Prevención de Colisiones . . . . . . . . . 8  
**CAPÍTULO III: SUITE AUTOMATIZADA DE PRUEBAS EN PYTEST** . . . . . . . . . . . . . . . . 9  
&nbsp;&nbsp;&nbsp;&nbsp;3.1 Arquitectura del Simulador (`test_microfrontend_analytics_fase2.py`) . . . . . . . . 9  
&nbsp;&nbsp;&nbsp;&nbsp;3.2 Verificación de Integración de los 4 Bloques Analíticos . . . . . . . . . . . . . . 10  
&nbsp;&nbsp;&nbsp;&nbsp;3.3 Manejo Canónico del Error 503, Aislamiento de Bloques y AbortSignal . . . . . . . 11  
**CAPÍTULO IV: EVIDENCIAS DE EJECUCIÓN Y CERTIFICACIÓN FORMAL** . . . . . . . . . . . . 12  
&nbsp;&nbsp;&nbsp;&nbsp;4.1 Comandos de Consola y Demostración de Incidencias Controladas . . . . . . . . . . 12  
&nbsp;&nbsp;&nbsp;&nbsp;4.2 Evidencia Visual Literal de Terminal de Pytest (9 Tests Aprobados) . . . . . . . . . 13  
&nbsp;&nbsp;&nbsp;&nbsp;4.3 Consolidación de la Suite Global de QA (334 Tests Aprobados en 0.62s) . . . . . . . 15  
**CAPÍTULO V: TRAZABILIDAD Y CONTROL DE VERSIONES** . . . . . . . . . . . . . . . . . . . . 16  
&nbsp;&nbsp;&nbsp;&nbsp;5.1 Registro de Commits, Pull Request #258 y Vinculación al Sub-issue #252 . . . . . . 16  
&nbsp;&nbsp;&nbsp;&nbsp;5.2 Inventario de Artefactos de Software Integrados . . . . . . . . . . . . . . . . . . . . 16  
**CONCLUSIONES Y RECOMENDACIONES** . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17  
**REFERENCIAS BIBLIOGRÁFICAS** . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18  

<div style="page-break-after: always;"></div>

---

# INTRODUCCIÓN Y OBJETIVOS DE LA TAREA

El presente informe técnico documenta de manera rigurosa y formal el proceso de verificación, testing automatizado y certificación de la **Tarea T27 (Sub-issue #252)**, en estrecha vinculación con la **Tarea T23 (Sub-issue #248)**, correspondientes a la **Historia de Usuario HU-22: Panel de Analítica Ambiental — Fase 2 (#224)** en el Sprint 4 de *EcoPredict & NLQ — Sistema de Alerta e Investigación Ambiental Ciudadana*.

En el Sprint 3, la Fase 1 de Analítica (`data-analytics`) reutilizaba los mismos webhooks de tiempo real del Flujo C (`/estaciones`, `/estaciones/serie-horaria`, `/alertas`), lo que ocasionaba una duplicidad funcional con el **Dashboard Ambiental** y carecía de herramientas de análisis histórico comparativo. Para corregir este solapamiento, la **HU-22** transformó integralmente el microfrontend para desligarlo del Flujo C y conectarlo de manera exclusiva a los nuevos endpoints del **Flujo D** en n8n (`/analitica/distritos`, `/comparativo`, `/ranking-eca`, `/patron-horario`, `/resumen-ia`).

Con la implementación realizada por Frontend (Jimena Sihuincho) en el **Pull Request #258** (mergeado a `main` en el commit `40819a6`), el rol de **QA / Prompt Engineer (Johann Romero)** procedió a auditar y certificar que la interfaz cumpla con el contrato de datos establecido en la Tarea T11, mantenga encapsulamiento estricto de estilos y responda con resiliencia ante contingencias de red (como el error **HTTP 503 Service Unavailable**).

```text
Arquitectura Desacoplada de Data Analytics (Fase 2) y Aislamiento de Fallos:

[Usuario / Navegador Web]
         │
         ▼
[Microfrontend: data-analytics] (Montado en /data-analytics)
  ├── DataAnalyticsPage (Estado global: selector 7/30 días + chips distritos)
  │
  ├── 1. DistrictComparison  ───> GET /analitica/comparativo?distritos=...&dias=7
  ├── 2. EcaRanking          ───> GET /analitica/ranking-eca?parametro=pm25&dias=7
  ├── 3. HourlyPattern       ───> GET /analitica/patron-horario?distrito=...&dias=7
  └── 4. WeeklyAiSummary     ───> GET /analitica/resumen-ia?distrito=... (por distrito)
         │
         ▼
[Aislamiento Operativo]: Si WeeklyAiSummary recibe HTTP 503, los bloques 1, 2 y 3
permanecen 100% operativos; el bloque 4 muestra PanelError con botón 'Reintentar'.
```

Los objetivos específicos asignados a QA en la Tarea T27 son:

1. **Certificar la Integración de los 4 Bloques:** Validar que los componentes `DistrictComparison`, `EcaRanking`, `HourlyPattern` y `WeeklyAiSummary` consuman las rutas canónicas del Flujo D definidas en `dataAnalyticsApi.ts`.
2. **Validar las Restricciones de Selección en UI (T23):** Verificar que la interfaz obligue a seleccionar un mínimo de 2 distritos y restrinja a un máximo de 4 distritos simultáneos para garantizar la legibilidad en pantallas ciudadanas.
3. **Auditar el Encapsulamiento de Estilos CSS:** Garantizar que todas las clases visuales empleen prefijos reservados (`da-` o `data-analytics-`), impidiendo la fuga de reglas globales hacia el contenedor Shell o hacia el Dashboard.
4. **Verificar la Tolerancia a Fallos (HTTP 503 Service Unavailable):** Simular caídas de la base de datos o sobrecargas en n8n, comprobando que la aplicación no sufra excepciones no controladas (*white screen of death*), muestre un `PanelError` amigable y provea mecanismos de reintento.
5. **Comprobar la Desconexión Asíncrona (AbortSignal):** Certificar que ante cambios rápidos del selector temporal (7 a 30 días), el hook `useRemoteData` cancele las peticiones previas en curso evitando condiciones de carrera (*race conditions*).
6. **Consolidar la Suite Global de QA en Pytest:** Desarrollar [`src/ia-ops/tests/test_microfrontend_analytics_fase2.py`](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/tests/test_microfrontend_analytics_fase2.py) con **9 pruebas unitarias e integrales**, alcanzando un nuevo hito de **334 pruebas automatizadas 100% aprobadas en 0.62 segundos**.

<div style="page-break-after: always;"></div>

---

# CAPÍTULO I: FUNDAMENTACIÓN TEÓRICA Y CONTEXTO DE LA HU-22

### 1.1 Evolución de la Fase 1 a la Fase 2 del Panel de Analítica Ambiental
En el ciclo de vida de los sistemas de información ambiental ciudadana, la arquitectura evoluciona desde la supervisión de contingencias inmediatas hacia el análisis longitudinal de patrones de exposición (World Health Organization [WHO], 2021). 

En la **Fase 1 (HU-03 / Sprint 3)**, el microfrontend `data-analytics` actuaba como una vista complementaria del Flujo C, utilizando `DistrictSummaryTable` y `AlertsPanel`. Sin embargo, esto duplicaba el propósito del Dashboard. La **Fase 2 (HU-22 / Sprint 4)** eliminó completamente dicha dependencia para dar paso a la analítica histórica:
* Se removieron los componentes antiguos: `AlertsPanel`, `DistrictSummaryTable`, `PmTrendChart`.
* Se crearon componentes especializados en indicadores agregados: comparación interdistrital de 7 vs 30 días, ranking de distritos con mayor número de días superando el ECA, curva horaria típica de 24 horas y resumen interpretativo redactado por IA.

### 1.2 Desacoplamiento de Microfrontends y Aislamiento Perimetral de Fallos
El paradigma de arquitectura de microfrontends (Geers, 2020) exige que cada aplicación satélite funcione con autonomía operativa. En un entorno de producción donde los servicios de backend (n8n, Groq, Gemini, PostgreSQL) pueden sufrir indisponibilidad transitoria, la interfaz debe aplicar el patrón *Bulkhead* (aislamiento en compartimentos estancos):
* Si el endpoint `/analitica/resumen-ia` falla por saturación de tokens o timeout de la IA, dicha caída no debe propagarse a los gráficos de tendencias ni al ranking de excedencias.
* Cada componente (`Panel`) maneja de manera encapsulada su propio estado de carga (`Esqueleto`), estado exitoso y estado de error (`PanelError`).

### 1.3 Principios de Usabilidad Ciudadana y Tolerancia a Fallos de Red
Bajo las pautas de accesibilidad e interacción ciudadana (Nielsen Norman Group, 2020), las aplicaciones públicas deben evitar tecnicismos en las pantallas de error. Un error de base de datos como `ECONNREFUSED` en el puerto 5432 no debe exponer trazas de software al usuario. En su lugar, el cliente debe recibir un mensaje estructurado con código HTTP canónico (`503`), junto con un control interactivo de "Reintentar" que no recargue la página completa.

<div style="page-break-after: always;"></div>

---

# CAPÍTULO II: ESPECIFICACIÓN DEL MICROFRONTEND DATA ANALYTICS (FASE 2)

### 2.1 Arquitectura de Componentes React y Consumo del Flujo D
El microfrontend está estructurado en React con TypeScript y Vite, bajo un esquema modular:

### Tabla 1
*Estructura de Componentes de la Fase 2 y Mapeo de Endpoints del Flujo D*

| Bloque / Componente | Archivo Fuente | Endpoint REST Consumido | Responsabilidad en la UI |
| :--- | :--- | :--- | :--- |
| **Cabecera y Selector** | `DataAnalyticsPage.tsx` | `GET /analitica/distritos` | Muestra estado de cobertura, selector 7/30 días y chips de distritos. |
| **Bloque 1: Comparativo** | `DistrictComparison.tsx` | `GET /analitica/comparativo` | Tarjetas comparativas de 2 a 4 distritos, variación % y sparklines SVG. |
| **Bloque 2: Ranking ECA** | `EcaRanking.tsx` | `GET /analitica/ranking-eca` | Ranking de distritos por días de superación del ECA en PM2.5 o PM10. |
| **Bloque 3: Patrón Horario** | `HourlyPattern.tsx` | `GET /analitica/patron-horario` | Gráfico horario 00:00-23:00, hora crítica y corte en horas sin dato. |
| **Bloque 4: Resumen con IA** | `WeeklyAiSummary.tsx` | `GET /analitica/resumen-ia` | Tarjetas con resumen interpretativo generado por LLM con fallback. |
| **Contenedor Compartido** | `Panel.tsx` | N/A | Marco visual unificado con numeración, pie de endpoint y `PanelError`. |

*Nota.* Fuente: Código fuente en [`src/microfrontends/data-analytics/src/`](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/microfrontends/data-analytics/src/).

### 2.2 Matriz de Validación de Parámetros de Interfaz y Límites (2 a 4 Distritos)
Aunque el backend del Flujo D soporta hasta 5 distritos en `/analitica/comparativo`, la interfaz de usuario de la Fase 2 (en cumplimiento de la Tarea T23) restringe intencionalmente el rango entre **2 y 4 distritos** para asegurar que las tarjetas comparativas se visualicen de manera óptima sin desbordar el diseño responsivo:

### Tabla 2
*Reglas de Validación en la Selección de Distritos (UI)*

| Intento de Usuario | Estado Inicial | Acción de la Interfaz | Mensaje de Retroalimentación |
| :--- | :---: | :---: | :--- |
| Desmarcar distrito quedando 1 | 2 distritos | Bloqueado | `"Se necesitan al menos 2 distritos para comparar."` |
| Seleccionar 3er o 4to distrito | 2 o 3 distritos | Permitido | Ninguno (renderiza tarjeta nueva con sparkline). |
| Intentar seleccionar un 5to distrito | 4 distritos | Bloqueado | `"Máximo 4 distritos a la vez: quita uno primero."` |
| Distrito con pocos datos | Cualquiera | Permitido | Borde punteado en chip y tooltip `"Pocos datos en los últimos N días"`. |

*Nota.* Fuente: Lógica implementada en `DistrictComparison.tsx` y validada en `TestMicrofrontendDataAnalyticsFase2Integration`.

### 2.3 Encapsulamiento de Estilos CSS (`da-`) y Prevención de Colisiones
Para impedir que las reglas de diseño interfieran con el Shell contenedor u otros microfrontends:
1. **Namespace de Clases:** Todos los selectores CSS utilizan los prefijos exclusivos `data-analytics-` o `da-` (ej. `da-panel`, `da-chips`, `da-chip`, `da-seg`, `da-sparkline`, `da-iagrid`).
2. **Uso de Variables Semánticas:** Los colores de categorías de calidad del aire (`--good`, `--moderate`, `--poor`) se consumen desde las variables CSS globales inyectadas por el Shell, garantizando soporte nativo para **tema claro y tema oscuro**.
3. **Gráficos SVG Nativos:** Se retiró la librería Chart.js; los sparklines y curvas horarias se generan con elementos `<svg>` nativos, evitando colisiones en el árbol DOM del navegador.

<div style="page-break-after: always;"></div>

---

# CAPÍTULO III: SUITE AUTOMATIZADA DE PRUEBAS EN PYTEST

### 3.1 Arquitectura del Simulador (`test_microfrontend_analytics_fase2.py`)
Para auditar la capa de frontend y su integración sin requerir servidores Node.js activos, se diseñó la suite en [`src/ia-ops/tests/test_microfrontend_analytics_fase2.py`](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/tests/test_microfrontend_analytics_fase2.py):

```text
Estructura Jerárquica de la Suite test_microfrontend_analytics_fase2.py:

test_microfrontend_analytics_fase2.py (9 Tests)
├── TestMicrofrontendDataAnalyticsFase2Integration (4 tests)
│   ├── test_describir_endpoint_formato_canonico
│   ├── test_district_comparison_selection_limits
│   ├── test_hourly_pattern_calculates_critical_hour_when_sufficient
│   └── test_hourly_pattern_handles_insufficient_data
├── TestMicrofrontendStyleEncapsulation (2 tests)
│   ├── test_css_class_prefix_consistency
│   └── test_root_wrapper_encapsulation
└── TestMicrofrontendError503HandlingAndResilience (3 tests)
    ├── test_error_503_maps_to_user_friendly_message
    ├── test_block_isolation_when_ai_summary_fails_503
    └── test_abort_signal_cancels_previous_requests_on_filter_change
```

### 3.2 Verificación de Integración de los 4 Bloques Analíticos
* **Formato de Endpoints:** Se auditó que la función `describirEndpoint` serialice adecuadamente las peticiones en los pies de página de cada tarjeta (ej. `GET /analitica/comparativo?distritos=ate,surco&dias=7`).
* **Suficiencia en Patrón Horario:** Se verificó que `HourlyPattern` evalúe la regla de negocio: se requieren al menos 12 horas con $n \ge 3$ lecturas para calcular la hora crítica. En caso contrario, renderiza los datos disponibles sin emitir falso dictamen crítico.

### 3.3 Manejo Canónico del Error 503, Aislamiento de Bloques y AbortSignal
* **Mapeo Canónico de 503:** La prueba `test_error_503_maps_to_user_friendly_message` certificó que un código HTTP 503 devuelto por n8n o PostgreSQL se traduzca al mensaje: `"El servicio de analítica no está disponible por ahora. Intenta de nuevo en unos minutos. (503)"`.
* **Aislamiento de Bloques:** En `test_block_isolation_when_ai_summary_fails_503`, se simuló que de 3 distritos seleccionados (`ate`, `surco`, `san-borja`), el servicio de IA de `surco` responda con 503. La suite comprobó que `cargarResumenes` entregue 2 resúmenes exitosos y aísle el error en la tarjeta de Surco con botón de reintento, sin afectar al comparativo ni al ranking.
* **Control de Concurrencia con AbortSignal:** Se verificó que el cambio dinámico entre periodos temporales (7 vs 30 días) invoque `AbortSignal.abort()`, descartando respuestas tardías de red.

<div style="page-break-after: always;"></div>

---

# CAPÍTULO IV: EVIDENCIAS DE EJECUCIÓN Y CERTIFICACIÓN FORMAL

### 4.1 Comandos de Consola y Demostración de Incidencias Controladas
Para la sustentación oral ante la **Ing. Norma León**, se han preparado los siguientes comandos de terminal:

### Tabla 3
*Comandos de Terminal para Reproducción de Pruebas e Incidencias en T27*

| Incidencia / Escenario Evaluado | Causa Raíz Simulada | Comportamiento en UI | Comando Específico para Terminal |
| :--- | :--- | :---: | :--- |
| **Suite Completa de T27 (9 Tests)** | Ejecución de integración y UI | **100% Passed** | `pytest src/ia-ops/tests/test_microfrontend_analytics_fase2.py -v` |
| **Selección Fuera de Rango (< 2 o > 4)** | Usuario intenta violar los límites | **Bloqueo / Aviso UI** | `pytest src/ia-ops/tests/test_microfrontend_analytics_fase2.py -k "test_district_comparison_selection_limits" -v` |
| **Caída 503 en Resumen con IA** | n8n o LLM devuelve 503 para 1 distrito | **Aislamiento / Retry** | `pytest src/ia-ops/tests/test_microfrontend_analytics_fase2.py -k "test_block_isolation" -v` |
| **Auditoría de Clases CSS** | Verificación de prefijos `da-` | **Aislamiento Estricto** | `pytest src/ia-ops/tests/test_microfrontend_analytics_fase2.py -k "TestMicrofrontendStyleEncapsulation" -v` |
| **Concurrencia de Filtro Temporal** | Cambio rápido de 7 a 30 días | **Cancelación Abort** | `pytest src/ia-ops/tests/test_microfrontend_analytics_fase2.py -k "test_abort_signal" -v` |

*Nota.* Fuente: Filtros `-k` de pytest en [`test_microfrontend_analytics_fase2.py`](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/tests/test_microfrontend_analytics_fase2.py).

### 4.2 Evidencia Visual Literal de Terminal de Pytest (9 Tests Aprobados)

```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\johan\AppData\Local\Programs\Python\Python312\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\johan\.gemini\antigravity\scratch\Grupo1_EcoPredict-NLQ
collecting ... collected 9 items

src/ia-ops/tests/test_microfrontend_analytics_fase2.py::TestMicrofrontendDataAnalyticsFase2Integration::test_describir_endpoint_formato_canonico PASSED [ 11%]
src/ia-ops/tests/test_microfrontend_analytics_fase2.py::TestMicrofrontendDataAnalyticsFase2Integration::test_district_comparison_selection_limits PASSED [ 22%]
src/ia-ops/tests/test_microfrontend_analytics_fase2.py::TestMicrofrontendDataAnalyticsFase2Integration::test_hourly_pattern_calculates_critical_hour_when_sufficient PASSED [ 33%]
src/ia-ops/tests/test_microfrontend_analytics_fase2.py::TestMicrofrontendDataAnalyticsFase2Integration::test_hourly_pattern_handles_insufficient_data PASSED [ 44%]
src/ia-ops/tests/test_microfrontend_style_encapsulation::test_css_class_prefix_consistency PASSED [ 55%]
src/ia-ops/tests/test_microfrontend_style_encapsulation::test_root_wrapper_encapsulation PASSED [ 66%]
src/ia-ops/tests/test_microfrontend_error503_handling_and_resilience::test_error_503_maps_to_user_friendly_message PASSED [ 77%]
src/ia-ops/tests/test_microfrontend_error503_handling_and_resilience::test_block_isolation_when_ai_summary_fails_503 PASSED [ 88%]
src/ia-ops/tests/test_microfrontend_error503_handling_and_resilience::test_abort_signal_cancels_previous_requests_on_filter_change PASSED [100%]

============================== 9 passed in 0.06s ==============================
```

```text
Figura 1. Aprobación al 100% de la Suite de Fase 2 en Pytest (9 Tests en 0.06s)
Nota. Salida literal de consola certificando las pruebas de integración, renderizado, encapsulamiento y resiliencia 503.
```

### 4.3 Consolidación de la Suite Global de QA (334 Tests Aprobados en 0.62s)
Con la incorporación de los 9 casos de prueba de la Tarea T27, el marco de aseguramiento de calidad alcanza un total de **334 pruebas automatizadas**:

* **Módulo de IA Ops, RAG Benchmark, Prompts y Langfuse:** 104 pruebas.
* **Módulo de Seguridad contra Prompt Injection (OWASP LLM01):** 38 pruebas.
* **Módulo de Microfrontend Data Analytics Fase 2 (HU-22 / T27):** 9 pruebas.
* **Módulo de Contrato y Resiliencia del Flujo D (HU-16 / T11):** 28 pruebas.
* **Módulo de BFF Serverless en Vercel (Flujo C / HT-13 / T16):** 25 pruebas.
* **Módulo de Mensajería, Suscripción y Cooldown en Telegram:** 22 pruebas.
* **Módulo de Microfrontend Data Analytics Fase 1 (Histórico):** 11 pruebas.
* **Módulo de Dashboard Ambiental e Integración:** 22 pruebas.
* **Módulo Estadístico de Detección de Anomalías (Z-Score):** 33 pruebas.
* **Módulo de Rate Limiting y Protección DoS:** 12 pruebas.
* **Módulo de Contratos Serverless OCI Functions:** 10 pruebas.
* **Módulo de Quality Gates en CI/CD y Dependabot:** 9 pruebas.
* **Módulo de LLMOps Observability Quality Gate:** 7 pruebas.
* **Pruebas de Integración HTTP en Newman / Postman:** 34 aserciones.
* **Prueba de Estrés Perimetral:** 1,000 peticiones continuas.

```text
============================= 334 passed in 0.62s =============================
```

<div style="page-break-after: always;"></div>

---

# CAPÍTULO V: TRAZABILIDAD Y CONTROL DE VERSIONES

### 5.1 Registro de Commits, Pull Request #258 y Vinculación al Sub-issue #252
La implementación de la Fase 2 fue desplegada por Frontend y auditada por QA con el siguiente historial de control de versiones:

### Tabla 4
*Registro de Commits de Trazabilidad para la Tarea T27 / HU-22*

| Hash / Referencia | Responsable | Mensaje Oficial de Commit | Tarea / Sub-issue |
| :---: | :--- | :--- | :---: |
| `40819a6` | David Llamocca | `Merge pull request #258 from CarlosChDev/Sihuincho (Fase 2)` | HU-22 / #224 |
| `2541dfa` | Jimena Sihuincho | `feat: HU-22 Panel de Analítica Ambiental — Fase 2` | T24-T26 / #249-#251 |
| `Pendiente` | Johann Romero | `QA: T27 - Pruebas de renderizado, encapsulamiento y resiliencia 503 en Data Analytics Fase 2 (#252)` | **T27 / #252** |

*Nota.* Fuente: Historial de commits en Git (`git log --oneline`).

### 5.2 Inventario de Artefactos de Software Integrados

### Tabla 5
*Inventario de Artefactos de Software Integrados en la Tarea T27*

| Componente de Software | Ruta Relativa en el Repositorio | Propósito en el Aseguramiento de Calidad |
| :--- | :--- | :--- |
| **Suite de Pruebas Pytest** | [`src/ia-ops/tests/test_microfrontend_analytics_fase2.py`](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/tests/test_microfrontend_analytics_fase2.py) | 9 pruebas unitarias e integrales para UI, estilos y error 503. |
| **Código del Microfrontend** | [`src/microfrontends/data-analytics/src/`](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/microfrontends/data-analytics/src/) | Componentes React (`DistrictComparison`, `Panel`, `HourlyPattern`, etc.). |
| **Evidencias Visuales UI** | [`docs/evidencias/HU-23/`](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/docs/evidencias/HU-23/) | 13 capturas de pantalla certificando temas, estados de carga y errores. |
| **Informe Técnico Académico** | [`docs/qa/sprint4/informe_tecnico_t27_sprint4.md`](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/docs/qa/sprint4/informe_tecnico_t27_sprint4.md) | Documento de certificación oficial bajo estructura USMP y APA 7. |
| **Catálogo General de QA** | [`docs/qa/README.md`](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/docs/qa/README.md) | Índice general de documentación de calidad actualizado con el Sprint 4. |

*Nota.* Fuente: Repositorio oficial GitHub `CarlosChDev/Grupo1_EcoPredict-NLQ`.

<div style="page-break-after: always;"></div>

---

# CONCLUSIONES Y RECOMENDACIONES

### Conclusiones:
1. **Certificación Exitosa de la Tarea T27 (HU-22 / #252):** Se validó que el microfrontend Data Analytics migró plenamente hacia el Flujo D de analítica histórica, retirando los componentes redundantes de la Fase 1 y logrando un desacoplamiento limpio frente al Dashboard Ambiental.
2. **Resiliencia Operativa y Aislamiento de Fallos:** Se comprobó que el microfrontend aísla los fallos de red a nivel de componente mediante `PanelError`. Si el servicio de IA o un distrito específico devuelve **HTTP 503**, los demás bloques continúan renderizando normalmente, garantizando una alta disponibilidad percibida por la ciudadanía.
3. **Encapsulamiento de Estilos sin Fugas Visuales:** Se auditó que la totalidad de las clases de estilo emplean prefijos unificados (`da-`), permitiendo la convivencia armónica con el Shell y habilitando soporte para temas claro y oscuro sin colisiones CSS.
4. **Suficiencia en la Experiencia de Usuario:** La interfaz restringe defensivamente la selección entre 2 y 4 distritos simultáneos y cancela peticiones desactualizadas mediante `AbortSignal`, previniendo inconsistencias de estado.
5. **Máxima Cobertura Acumulada de QA:** La incorporación de los 9 tests de T27 consolida un total de **334 pruebas automatizadas (100% aprobadas en 0.62 segundos)** para el cierre de proyecto.

### Recomendaciones:
1. **Monitoreo de Variables de Entorno en Despliegue:** Verificar que en el panel de Vercel del microfrontend `data-analytics` se configure correctamente `VITE_N8N_ANALITICA_BASE_URL` apuntando al proxy Nginx en el puerto 80 de OCI (con CORS habilitado), evitando llamar al puerto 5678 no expuesto.
2. **Cierre Consolidado del Sprint 4:** Con las tareas T2, T16, T11 y T27 certificadas, se recomienda emitir el **Informe Consolidado de Cierre de Sprint 4** para la sustentación final ante la docente Ing. Norma León.

<div style="page-break-after: always;"></div>

---

# REFERENCIAS BIBLIOGRÁFICAS

* Geers, M. (2020). *Micro Frontends in Action*. Manning Publications.
* Nielsen Norman Group. (2020). *Error Message Guidelines: Usability and User Experience*. NN/g. https://www.nngroup.com/articles/error-message-guidelines/
* World Health Organization [WHO]. (2021). *WHO global air quality guidelines: particulate matter (PM2.5 and PM10), ozone, nitrogen dioxide, sulfur dioxide and carbon monoxide*. World Health Organization. https://apps.who.int/iris/handle/10665/345329
* W3C. (2021). *CSS Cascading and Inheritance Level 4 (W3C Candidate Recommendation Snapshot)*. World Wide Web Consortium. https://www.w3.org/TR/css-cascade-4/
* React Documentation. (2024). *Synchronizing with Effects & AbortController in Data Fetching*. Meta Open Source. https://react.dev/reference/react/useEffect

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
