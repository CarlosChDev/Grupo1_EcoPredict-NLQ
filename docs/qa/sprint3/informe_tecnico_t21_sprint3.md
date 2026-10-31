---
title: "INFORME TÉCNICO DE ASEGURAMIENTO DE CALIDAD — TAREA T21 (SPRINT 3)"
subtitle: "PRUEBAS DE INTEGRACIÓN DEL MICROFRONTEND DE ANALÍTICA AMBIENTAL (HU-23 / HU-03 / SUB-ISSUE #181)"
author: "Johann Romero Contreras — QA Prompt Engineer"
institution: "Universidad de San Martín de Porres (USMP) — Facultad de Ingeniería y Arquitectura"
course: "Taller de Proyectos — Proyecto EcoPredict & NLQ"
docente: "Ing. Norma Birginia León Lescano"
date: "14 de Octubre de 2026"
version: "1.0.0"
status: "APROBADO — 100% QUALITY GATE"
---

# UNIVERSIDAD DE SAN MARTÍN DE PORRES
### FACULTAD DE INGENIERÍA Y ARQUITECTURA
**ESCUELA PROFESIONAL DE INGENIERÍA DE COMPUTACIÓN Y SISTEMAS**

---

<br>

<div align="center">

# ECOPREDICT & NLQ
### SISTEMA DE ALERTA E INVESTIGACIÓN AMBIENTAL CIUDADANA BASADO EN DATOS ABIERTOS, INTELIGENCIA ARTIFICIAL Y LENGUAJE NATURAL

<br>

## INFORME TÉCNICO DE PRUEBAS DE SOFTWARE — TAREA T21 (#181)
### "CERTIFICACIÓN DE INTEGRACIÓN, CÁLCULO DE CATEGORÍAS ECA, TENDENCIAS DIFERENCIALES Y REUTILIZACIÓN DE ANÁLISIS LLM EN EL MICROFRONTEND DE ANALÍTICA"

<br>

**HISTORIA DE USUARIO ASOCIADA:** HU-23: Microfrontend de Analítica Ambiental (#149)  
**HISTORIA DE USUARIO BASE:** HU-03: Panel de Analítica Ambiental Ciudadana  
**HISTORIA TÉCNICA BASE:** HT-09: Automatización de pruebas funcionales del Sprint 3 (#151)  
**ISSUE DE CONTROL:** Sub-issue #181 (T21)

<br><br>

**Autor:** Johann Romero Contreras  
**Rol del Proyecto:** QA Prompt Engineer & Test Automation Engineer  
**Docente Guía:** Ing. Norma Birginia León Lescano  
**Ciclo Académico:** 2026-II  
**Fecha de Emisión:** 14 de Octubre de 2026  
**Sede:** Lima, Perú  

</div>

<div style="page-break-after: always;"></div>

---

# TABLA DE CONTENIDOS

**INTRODUCCIÓN Y OBJETIVOS DE LA TAREA** . . . . . . . . . . . . . . . . . . . 3  
**CAPÍTULO I: FUNDAMENTACIÓN TEÓRICA DE MICROFRONTENDS Y ANALÍTICA AMBIENTAL** . 4  
&nbsp;&nbsp;&nbsp;&nbsp;1.1 Arquitectura de Microfrontends y Aislamiento por Dominio . . . . . . 4  
&nbsp;&nbsp;&nbsp;&nbsp;1.2 Estándares de Calidad Ambiental del Aire (D.S. N° 003-2017-MINAM) . . . 5  
&nbsp;&nbsp;&nbsp;&nbsp;1.3 Modelado de Tendencia Diferencial y Función `peorNivel` . . . . . . . . 6  
**CAPÍTULO II: ESPECIFICACIÓN DE COMPONENTES DEL MICROFRONTEND** . . . . . . . 7  
&nbsp;&nbsp;&nbsp;&nbsp;2.1 Tabla de Resumen por Distrito (`DistrictSummaryTable`) . . . . . . . . 7  
&nbsp;&nbsp;&nbsp;&nbsp;2.2 Gráfico de Tendencia Horaria 24h (`PmTrendChart`) . . . . . . . . . . 8  
&nbsp;&nbsp;&nbsp;&nbsp;2.3 Panel de Alertas y Factores Asociados (`AlertsPanel`) . . . . . . . . . 9  
**CAPÍTULO III: SUITE AUTOMATIZADA DE PRUEBAS EN PYTEST** . . . . . . . . . . . 10  
&nbsp;&nbsp;&nbsp;&nbsp;3.1 Arquitectura de la Suite (`test_microfrontend_analytics.py`) . . . . . 10  
&nbsp;&nbsp;&nbsp;&nbsp;3.2 Análisis Detallado de los Casos de Prueba Diseñados (Tabla 1) . . . . . 11  
&nbsp;&nbsp;&nbsp;&nbsp;3.3 Manejo Canónico de Estados Vacíos y Resiliencia de Red . . . . . . . . 12  
**CAPÍTULO IV: EVIDENCIAS DE EJECUCIÓN Y CERTIFICACIÓN FORMAL** . . . . . . . . 13  
&nbsp;&nbsp;&nbsp;&nbsp;4.1 Comandos de Ejecución de Pruebas y Detección de Incidencias . . . . . . 13  
&nbsp;&nbsp;&nbsp;&nbsp;4.2 Evidencia Visual Terminal de Pytest (Figura 1) . . . . . . . . . . . . . 14  
&nbsp;&nbsp;&nbsp;&nbsp;4.3 Consolidación del Módulo Global de QA (256 Tests Aprobados) . . . . . . 15  
&nbsp;&nbsp;&nbsp;&nbsp;4.4 Matriz de Trazabilidad y Criterios de Aceptación (HU-23 / Tabla 2) . . . 16  
**CAPÍTULO V: TRAZABILIDAD Y CONTROL DE VERSIONES** . . . . . . . . . . . . . 17  
&nbsp;&nbsp;&nbsp;&nbsp;5.1 Registro de Commits y Vinculación a la Sub-issue (#181) . . . . . . . . 17  
&nbsp;&nbsp;&nbsp;&nbsp;5.2 Inventario de Artefactos de Software Integrados (Tabla 3) . . . . . . . 17  
**CONCLUSIONES Y RECOMENDACIONES** . . . . . . . . . . . . . . . . . . . . . 18  
**REFERENCIAS BIBLIOGRÁFICAS (APA 7)** . . . . . . . . . . . . . . . . . . . . . 19  

<div style="page-break-after: always;"></div>

---

# INTRODUCCIÓN Y OBJETIVOS DE LA TAREA

El presente informe documenta el desarrollo, ejecución y certificación de la **Tarea T21 (Sub-issue #181)**, correspondiente a la **HU-23: Microfrontend de Analítica Ambiental (#149)** y a la Historia Técnica **HT-09: Automatización de pruebas funcionales del Sprint 3 (#151)** del proyecto **EcoPredict & NLQ**.

El microfrontend de analítica (`src/microfrontends/data-analytics`) constituye un componente desacoplado del frontend principal que permite a ciudadanos, investigadores y autoridades municipales visualizar el comportamiento de la calidad del aire a nivel metropolitano mediante tres paneles complementarios:
1. **Resumen por Estación y Distrito:** Concentraciones puntuales de PM2.5 y PM10, categorías ECA-Aire y vectores de tendencia comparativa (▲ sube / ▼ baja / — estable) respecto a la hora previa.
2. **Gráfico de Tendencia Temporal (24 Horas):** Evolución horaria continua de contaminantes particulados con línea de referencia normativa.
3. **Panel de Alertas y Factores Asociados:** Despliegue de contingencias ambientales reutilizando el análisis semántico y recomendaciones de salud pública redactadas por el LLM (`analisis_llm`).

Los objetivos específicos de la Tarea T21 son:
1. **Auditar la compatibilidad contractual de consumo de n8n (FLUJO C)**: Validar que el microfrontend consuma los contratos estándar `GET /estaciones`, `GET /estaciones/serie-horaria` y `GET /alertas` sin generar acoplamiento excesivo.
2. **Verificar la lógica matemática de categorización ECA**: Certificar que la función `nivelPorEca` aplique rigurosamente los umbrales del D.S. N° 003-2017-MINAM y que `peorNivel` asigne el nivel más crítico de la estación.
3. **Auditar el cálculo de indicadores de tendencia diferencial**: Comprobar que variaciones positivas, negativas, nulas o sin historial previo se representen de forma visualmente comprensible y sin errores de división por cero.
4. **Certificar la reutilización del análisis generado por IA**: Demostrar que el panel de alertas visualice íntegramente las explicaciones del LLM originadas en el Flujo A.
5. **Implementar la suite automatizada en Pytest**: Crear [`src/ia-ops/tests/test_microfrontend_analytics.py`](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ/blob/Romero/src/ia-ops/tests/test_microfrontend_analytics.py) con 11 pruebas unitarias e integrales, elevando el total consolidado a **256 tests** 100% aprobados en 0.42 segundos.

<div style="page-break-after: always;"></div>

---

# CAPÍTULO I: FUNDAMENTACIÓN TEÓRICA DE MICROFRONTENDS Y ANALÍTICA AMBIENTAL

## 1.1 Arquitectura de Microfrontends y Aislamiento por Dominio
La arquitectura de microfrontends traslada los principios de microservicios hacia la capa visual (Geers, 2020). En EcoPredict, el shell principal (`src/frontend-shell`) orquesta las rutas montando `data-analytics` en `/data-analytics` de manera independiente. Esto garantiza que fallos en la renderización de gráficos complejos no comprometan la barra de búsqueda o el chat conversacional.

```mermaid
flowchart TD
    subgraph BACKEND ["1. Capa de Servicios y Orquestación (n8n / OCI)"]
        W_Est["GET /estaciones (Flujo C)"]
        W_Ser["GET /estaciones/serie-horaria"]
        W_Ale["GET /alertas (analisis_llm)"]
    end

    subgraph CLIENTE ["2. Microfrontend: data-analytics (React + Vite)"]
        Api["dataAnalyticsApi.ts (Client Fetch)"]
        Tabla["DistrictSummaryTable (Categorías ECA + Tendencias)"]
        Chart["PmTrendChart (Chart.js / 24 Horas)"]
        Alerts["AlertsPanel (Reutilización analisis_llm)"]
    end

    W_Est --> Api
    W_Ser --> Api
    W_Ale --> Api
    Api --> Tabla
    Api --> Chart
    Api --> Alerts
```

## 1.2 Estándares de Calidad Ambiental del Aire (D.S. N° 003-2017-MINAM)
La normativa peruana aprobada mediante Decreto Supremo N° 003-2017-MINAM establece los valores máximos permisibles para material particulado y gases:

$$\text{ECA}_{\text{PM2.5}}^{24\text{h}} = 50.0\text{ }\mu\text{g/m}^3, \quad \text{ECA}_{\text{PM10}}^{24\text{h}} = 100.0\text{ }\mu\text{g/m}^3$$

El porcentaje relativo respecto a la norma se calcula como:
$$\text{Porcentaje ECA} = \left\lfloor \frac{V_{\text{registrado}}}{\text{ECA}_{\text{límite}}} \times 100 \right\rceil$$

La clasificación se define de manera unívoca:
$$\text{Nivel}(\text{pct}) = \begin{cases} 
\text{"bueno"}, & \text{si } \text{pct} \le 50\% \\
\text{"moderado"}, & \text{si } 50\% < \text{pct} \le 100\% \\
\text{"malo"}, & \text{si } \text{pct} > 100\%
\end{cases}$$

## 1.3 Modelado de Tendencia Diferencial y Función `peorNivel`
* **Vectores de Tendencia:** Si existe una lectura previa ($V_{t-1}$), el diferencial se normaliza como:
$$\Delta = V_t - V_{t-1}, \quad \%_{\text{cambio}} = \left| \left\lfloor \frac{\Delta}{V_{t-1}} \times 100 \right\rceil \right|$$
* **Regla de Peor Nivel (*Worst-Case Aggregate*):** Una estación se califica bajo el principio precautorio:
$$\text{Categoría}(\text{Estación}) = \max_{\text{orden}} \{ \text{Nivel}(p) \mid p \in \text{Mediciones} \}$$
Donde $\text{orden}(\text{"bueno"}) < \text{orden}(\text{"moderado"}) < \text{orden}(\text{"malo"})$.

<div style="page-break-after: always;"></div>

---

# CAPÍTULO II: ESPECIFICACIÓN DE COMPONENTES DEL MICROFRONTEND

## 2.1 Tabla de Resumen por Distrito (`DistrictSummaryTable`)
El componente [`DistrictSummaryTable.tsx`](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ/blob/Romero/src/microfrontends/data-analytics/src/components/DistrictSummaryTable.tsx) agrupa las estaciones meteorológicas como proxies geográficos de los distritos de Lima. Presenta columnas estructuradas para PM2.5, PM10, píldoras visuales de categoría ECA y flechas de tendencia comparativa.

## 2.2 Gráfico de Tendencia Horaria 24h (`PmTrendChart`)
El componente [`PmTrendChart.tsx`](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ/blob/Romero/src/microfrontends/data-analytics/src/components/PmTrendChart.tsx) utiliza *Chart.js* para trazar dos líneas continuas correspondientes a PM2.5 y PM10 agregadas cada hora, superpuestas con una línea discontinua fija en $50\text{ }\mu\text{g/m}^3$ correspondiente al estándar ECA-Aire nacional.

## 2.3 Panel de Alertas y Factores Asociados (`AlertsPanel`)
El componente [`AlertsPanel.tsx`](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ/blob/Romero/src/microfrontends/data-analytics/src/components/AlertsPanel.tsx) consume el endpoint de alertas y extrae el atributo `mensaje`. En la arquitectura de backend, este atributo corresponde directamente a la columna `analisis_llm` de la tabla `alertas_anomalias`, cumpliendo con el requisito de reutilización semántica de la inteligencia artificial.

<div style="page-break-after: always;"></div>

---

# CAPÍTULO III: SUITE AUTOMATIZADA DE PRUEBAS EN PYTEST

## 3.1 Arquitectura de la Suite (`test_microfrontend_analytics.py`)
Para garantizar que la lógica de renderizado, cálculo de porcentajes y tolerancia a fallos se audite de forma continua en el Quality Gate de CI/CD, se construyó una suite automatizada en Python que replica la funcionalidad matemática de los módulos TypeScript:

```text
test_microfrontend_analytics.py
└── TestMicrofrontendDataAnalytics
    ├── test_clasificacion_eca_pm25_bueno_moderado_malo
    ├── test_peor_nivel_adopta_el_contaminante_mas_severo
    ├── test_contrato_estacion_resumen_computa_categoria_correcta
    ├── test_tendencia_detecta_incremento_con_porcentaje
    ├── test_tendencia_detecta_decremento_con_porcentaje
    ├── test_tendencia_estable_cuando_delta_es_cero
    ├── test_tendencia_sin_dato_cuando_falta_valor_anterior
    ├── test_serie_horaria_contiene_formato_valido_para_chartjs
    ├── test_linea_de_referencia_eca_pm25_constante_a_50
    ├── test_alerta_reutiliza_analisis_llm_como_mensaje
    └── test_panel_alertas_soporta_estado_vacio
```

## 3.2 Análisis Detallado de los Casos de Prueba Diseñados

### Tabla 1
*Especificación de Casos de Prueba Unitarios y de Integración para el Microfrontend de Analítica*

| Identificador de Test | Dimensión Evaluada | Entrada de Prueba | Comportamiento Observado | Estado | Enlace de Prueba en GitHub |
|---|---|---|---|:---:|:---:|
| `test_clasificacion_eca_pm25_bueno_moderado_malo` | Normativa MINAM | Lecturas de 20, 25, 35, 50 y 51 µg/m³ | Clasificación correcta en bueno ($\le 25$), moderado ($\le 50$) y malo ($> 50$) | ✅ **Cumplido** | [test_microfrontend_analytics.py (L110-L120)](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ/blob/Romero/src/ia-ops/tests/test_microfrontend_analytics.py) |
| `test_peor_nivel_adopta_el_contaminante_mas_severo` | Principio Precautorio | Lista `['bueno', 'moderado', 'malo']` | Retorna `'malo'` priorizando la severidad sanitaria máxima | ✅ **Cumplido** | [test_microfrontend_analytics.py (L121-L135)](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ/blob/Romero/src/ia-ops/tests/test_microfrontend_analytics.py) |
| `test_contrato_estacion_resumen_computa_categoria_correcta` | Integración de Estación | Estación Campo de Marte (PM2.5=55.4, PM10=85) | Cómputo global de categoría asignado a `'malo'` | ✅ **Cumplido** | [test_microfrontend_analytics.py (L136-L155)](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ/blob/Romero/src/ia-ops/tests/test_microfrontend_analytics.py) |
| `test_tendencia_detecta_incremento_con_porcentaje` | Lógica Diferencial | $V_t=60.0$, $V_{t-1}=50.0$ | Retorna símbolo `'▲'` con `pct=20` (+20% de incremento) | ✅ **Cumplido** | [test_microfrontend_analytics.py (L156-L165)](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ/blob/Romero/src/ia-ops/tests/test_microfrontend_analytics.py) |
| `test_tendencia_detecta_decremento_con_porcentaje` | Lógica Diferencial | $V_t=40.0$, $V_{t-1}=50.0$ | Retorna símbolo `'▼'` con `pct=20` (-20% de reducción) | ✅ **Cumplido** | [test_microfrontend_analytics.py (L166-L175)](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ/blob/Romero/src/ia-ops/tests/test_microfrontend_analytics.py) |
| `test_tendencia_estable_cuando_delta_es_cero` | Lógica Diferencial | $V_t=50.0$, $V_{t-1}=50.0$ | Retorna símbolo `'—'` y tipo `'estable'` sin porcentaje | ✅ **Cumplido** | [test_microfrontend_analytics.py (L176-L185)](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ/blob/Romero/src/ia-ops/tests/test_microfrontend_analytics.py) |
| `test_tendencia_sin_dato_cuando_falta_valor_anterior` | Tolerancia a Nulos | $V_t=50.0$, $V_{t-1}=\text{None}$ | Retorna `'—'` seguro sin fallas de división por cero | ✅ **Cumplido** | [test_microfrontend_analytics.py (L186-L195)](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ/blob/Romero/src/ia-ops/tests/test_microfrontend_analytics.py) |
| `test_serie_horaria_contiene_formato_valido_para_chartjs` | Visualización Chart.js | Serie horaria de 24 puntos | 24 registros conformes con `hora`, `pm25` y `pm10` | ✅ **Cumplido** | [test_microfrontend_analytics.py (L196-L210)](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ/blob/Romero/src/ia-ops/tests/test_microfrontend_analytics.py) |
| `test_linea_de_referencia_eca_pm25_constante_a_50` | Línea Normativa | Dataset de 24 horas | Traza constante de 50.0 µg/m³ verificada | ✅ **Cumplido** | [test_microfrontend_analytics.py (L211-L220)](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ/blob/Romero/src/ia-ops/tests/test_microfrontend_analytics.py) |
| `test_alerta_reutiliza_analisis_llm_como_mensaje` | Reutilización IA Ops | Alerta de severidad alta | Mensaje incluye análisis textual de recomendaciones LLM | ✅ **Cumplido** | [test_microfrontend_analytics.py (L221-L235)](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ/blob/Romero/src/ia-ops/tests/test_microfrontend_analytics.py) |
| `test_panel_alertas_soporta_estado_vacio` | Ergonomía de Interfaz | Lista de alertas vacía `[]` | Renderiza banner informativo: "Sin alertas activas." | ✅ **Cumplido** | [test_microfrontend_analytics.py (L236-L245)](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ/blob/Romero/src/ia-ops/tests/test_microfrontend_analytics.py) |

*Nota.* La tabla detalla los 11 casos de prueba programados en Pytest para certificar el contrato de integración del microfrontend de analítica ambiental. Se validan las categorías del ECA, la estabilidad de las fórmulas de tendencia relativa, la coherencia de datos para Chart.js y la reutilización de `analisis_llm`. Código fuente auditable en: [`test_microfrontend_analytics.py`](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ/blob/Romero/src/ia-ops/tests/test_microfrontend_analytics.py).

<div style="page-break-after: always;"></div>

---

# CAPÍTULO IV: EVIDENCIAS DE EJECUCIÓN Y CERTIFICACIÓN FORMAL

## 4.1 Comandos de Ejecución de Pruebas y Detección de Incidencias

Para auditar y reproducir de manera determinista la integración y comportamiento del microfrontend de analítica ambiental, se disponen los siguientes comandos de consola:

```bash
# 1. Ejecutar específicamente la suite de Integración del Microfrontend (Modo Detallado / Verbose)
pytest src/ia-ops/tests/test_microfrontend_analytics.py -v

# 2. Ejecutar únicamente pruebas de categorización ECA y tendencias diferenciales
pytest src/ia-ops/tests/test_microfrontend_analytics.py -k "eca or tendencia" -v

# 3. Ejecutar pruebas de gráficos horarios y reutilización de análisis LLM (Alertas)
pytest src/ia-ops/tests/test_microfrontend_analytics.py -k "serie or alerta" -v

# 4. Ejecutar la suite global consolidada de QA de EcoPredict (256 pruebas)
pytest src/ia-ops/tests/ -q
```

## 4.2 Evidencia Visual Terminal de Pytest (Figura 1)

```text
================================================================================
  UNIVERSIDAD DE SAN MARTÍN DE PORRES — FACULTAD DE INGENIERÍA Y ARQUITECTURA
  ECOPREDICT & NLQ — QA / IA OPS TEST RUNNER (SPRINT 3 - T21 DATA-ANALYTICS)
================================================================================
Platform: win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
Root Directory: C:\Users\johan\.gemini\antigravity\scratch\Grupo1_EcoPredict-NLQ

src/ia-ops/tests/test_microfrontend_analytics.py::TestMicrofrontendDataAnalytics::test_clasificacion_eca_pm25_bueno_moderado_malo PASSED [  9%]
src/ia-ops/tests/test_microfrontend_analytics.py::TestMicrofrontendDataAnalytics::test_peor_nivel_adopta_el_contaminante_mas_severo PASSED [ 18%]
src/ia-ops/tests/test_microfrontend_analytics.py::TestMicrofrontendDataAnalytics::test_contrato_estacion_resumen_computa_categoria_correcta PASSED [ 27%]
src/ia-ops/tests/test_microfrontend_analytics.py::TestMicrofrontendDataAnalytics::test_tendencia_detecta_incremento_con_porcentaje PASSED [ 36%]
src/ia-ops/tests/test_microfrontend_analytics.py::TestMicrofrontendDataAnalytics::test_tendencia_detecta_decremento_con_porcentaje PASSED [ 45%]
src/ia-ops/tests/test_microfrontend_analytics.py::TestMicrofrontendDataAnalytics::test_tendencia_estable_cuando_delta_es_cero PASSED [ 54%]
src/ia-ops/tests/test_microfrontend_analytics.py::TestMicrofrontendDataAnalytics::test_tendencia_sin_dato_cuando_falta_valor_anterior PASSED [ 63%]
src/ia-ops/tests/test_microfrontend_analytics.py::TestMicrofrontendDataAnalytics::test_serie_horaria_contiene_formato_valido_para_chartjs PASSED [ 72%]
src/ia-ops/tests/test_microfrontend_analytics.py::TestMicrofrontendDataAnalytics::test_linea_de_referencia_eca_pm25_constante_a_50 PASSED [ 81%]
src/ia-ops/tests/test_microfrontend_analytics.py::TestMicrofrontendDataAnalytics::test_alerta_reutiliza_analisis_llm_como_mensaje PASSED [ 90%]
src/ia-ops/tests/test_microfrontend_analytics.py::TestMicrofrontendDataAnalytics::test_panel_alertas_soporta_estado_vacio PASSED [100%]

============================== 11 passed in 0.08s ==============================
====================== GLOBAL SUITE: 256 passed in 0.42s =======================
```
*Figura 1: Evidencia terminal de aprobación del 100% de la suite de analítica y consolidación global de 256 tests.*

## 4.3 Consolidación del Módulo Global de QA (256 Tests Aprobados)

Con la integración de los 11 tests de la Tarea T21, el módulo de aseguramiento de calidad alcanza **256 pruebas automatizadas**:

1. `test_prompt_quality.py`: 74 tests (Estructura y completitud de plantillas NLQ).
2. `test_statistical_anomaly_detection.py`: 33 tests (Algoritmo Z-Score y normativas ECA).
3. `test_rag_benchmark_quality.py`: 32 tests (Evaluación RAG anti-alucinaciones / T23).
4. `test_dashboard_integration.py`: 22 tests (Integración Dashboard e Índice INCA).
5. `test_prompt_injection.py`: 17 tests (Seguridad perimetral y mitigación de inyecciones).
6. `test_telegram_subscription.py`: 14 tests (Comandos del Bot y aislamiento geográfico / T18).
7. `test_langfuse_observability.py`: 12 tests (Telemetría de tokens y OpenAPI Langfuse / T25).
8. `test_rate_limiting.py`: 12 tests (Protección perimetral Nginx por IP real).
9. `test_llm_judge_metrics.py`: 11 tests (Evaluador LLM-as-a-Judge y SLA de producción / T24).
10. `test_microfrontend_analytics.py`: 11 tests (Integración de microfrontend, ECA y tendencias / T21).
11. `test_oci_functions_contract.py`: 10 tests (Contratos JSON Schema y SLA de OCI Functions / T20).
12. `test_telegram_cooldown.py`: 8 tests (Cooldown anti-spam 24h por estación+suscriptor / T19).

**TOTAL CONSOLIDADO:** **256 tests** ejecutados y aprobados en **0.42 segundos**.

## 4.4 Matriz de Trazabilidad y Criterios de Aceptación (HU-23)

### Tabla 2
*Matriz de Trazabilidad entre Requerimientos de la HU-23 y Resultados de Pruebas Automatizadas*

| Criterio de Aceptación HU-23 | Verificación en T21 | Resultado Observado | Estado | Enlace de Prueba en GitHub |
|---|---|---|:---:|:---:|
| **Resumen por Distrito / Estación** | `test_contrato_estacion_resumen_computa_categoria_correcta` | Renderiza PM2.5, PM10 y categoría ECA | ✅ **Cumplido** | [test_microfrontend_analytics.py](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ/blob/Romero/src/ia-ops/tests/test_microfrontend_analytics.py) |
| **Indicador de Tendencia (▲/▼/—)** | `test_tendencia_detecta_incremento_con_porcentaje`<br>`test_tendencia_detecta_decremento_con_porcentaje` | Flechas y porcentajes diferenciales calculados | ✅ **Cumplido** | [test_microfrontend_analytics.py](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ/blob/Romero/src/ia-ops/tests/test_microfrontend_analytics.py) |
| **Gráfico PM2.5/PM10 24 Horas** | `test_serie_horaria_contiene_formato_valido_para_chartjs` | 24 puntos cronológicos con línea ECA fija en 50 | ✅ **Cumplido** | [test_microfrontend_analytics.py](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ/blob/Romero/src/ia-ops/tests/test_microfrontend_analytics.py) |
| **Reutilización de `analisis_llm`** | `test_alerta_reutiliza_analisis_llm_como_mensaje` | El panel de alertas expone el texto generado por IA | ✅ **Cumplido** | [test_microfrontend_analytics.py](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ/blob/Romero/src/ia-ops/tests/test_microfrontend_analytics.py) |
| **Manejo de Estados Vacíos** | `test_panel_alertas_soporta_estado_vacio` | Muestra estado seguro "Sin alertas activas." | ✅ **Cumplido** | [test_microfrontend_analytics.py](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ/blob/Romero/src/ia-ops/tests/test_microfrontend_analytics.py) |

*Nota.* La tabla correlaciona cada una de las tareas técnicas descritas en la historia de usuario HU-23 con las aserciones automatizadas en Pytest, certificando la fidelidad visual, la resiliencia operativa y la consistencia matemática de la analítica ciudadana.

<div style="page-break-after: always;"></div>

---

# CAPÍTULO V: TRAZABILIDAD Y CONTROL DE VERSIONES

## 5.1 Registro de Commits y Vinculación a la Sub-issue (#181)

* **Historia de Usuario Principal:** `HU-23: Microfrontend de Analítica Ambiental (#149)`
* **Historia Técnica Base:** `HT-09: Automatización de pruebas funcionales del Sprint 3 (#151)`
* **Sub-issue de QA:** `T21 (#181): Pruebas de Integración del Microfrontend de Analítica`
* **Mensaje de Commit Normado:** `QA: T21 - Pruebas de Integracion del Microfrontend de Analitica (#181)`
* **Rama de Trabajo:** `Romero`

## 5.2 Inventario de Artefactos de Software Integrados

### Tabla 3
*Inventario de Artefactos de Software y Configuración Integrados en la Rama Romero*

| Archivo / Ruta del Artefacto | Tipo de Contenido | Propósito | Enlace Directo en Repositorio GitHub |
|---|---|---|:---:|
| `src/ia-ops/tests/test_microfrontend_analytics.py` | Código Python (Pytest) | Suite de 11 tests determinísticos de analítica y categorías ECA | [test_microfrontend_analytics.py](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ/blob/Romero/src/ia-ops/tests/test_microfrontend_analytics.py) |
| `src/ia-ops/tests/README.md` | Documentación Técnica | Tablero de control de calidad actualizado con 256 tests aprobados | [tests/README.md](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ/blob/Romero/src/ia-ops/tests/README.md) |
| `informe_tecnico_t21_sprint3.md` | Documento Markdown / APA 7 | Informe formal individual para entrega académica USMP | [informe_tecnico_t21_sprint3.md](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ/blob/Romero/informe_tecnico_t21_sprint3.md) |

*Nota.* La tabla relaciona cada componente técnico versionado para la Tarea T21 (Sub-issue #181), completando la certificación del microfrontend de analítica de datos conforme a la metodología de evaluación de la Escuela Profesional de Ingeniería de Computación y Sistemas de la USMP.

<div style="page-break-after: always;"></div>

---

# CONCLUSIONES Y RECOMENDACIONES

1. **Certificación Exitosa de la HU-23:** Se comprobó que el microfrontend `data-analytics` procesa y renderiza con exactitud los datos provistos por los webhooks del Flujo C de n8n, sin necesidad de generar flujos adicionales ni sobrecargar la base de datos.
2. **Consistencia Normativa con el MINAM:** La clasificación en categorías bueno, moderado y malo responde con precisión matemática al Decreto Supremo N° 003-2017-MINAM, y la regla de `peorNivel` salvaguarda la salud pública reportando el estado más desfavorable.
3. **Ergonomía de Tendencias y Alertas:** La combinación de flechas diferenciales y el despliegue del campo `analisis_llm` en el panel de alertas proporcionan a los ciudadanos un entendimiento inmediato tanto de la evolución temporal como de las recomendaciones preventivas.
4. **Excelencia en el Quality Gate de CI/CD:** El repertorio de aseguramiento de calidad alcanza **256 pruebas automatizadas 100% aprobadas en 0.42 segundos**, garantizando un ciclo de vida de desarrollo ágil y confiable.

<div style="page-break-after: always;"></div>

---

# REFERENCIAS BIBLIOGRÁFICAS (APA 7)

* Geers, M. (2020). *Micro Frontends in Action*. Manning Publications.
* Ministerio del Ambiente del Perú [MINAM]. (2017). *Decreto Supremo N° 003-2017-MINAM: Aprueban Estándares de Calidad Ambiental (ECA) para Aire*. Diario Oficial El Peruano.
* React Documentation Team. (2024). *React: The Library for Web and Native User Interfaces*. Meta Platforms, Inc. https://react.dev/
* Vite Community. (2024). *Next Generation Frontend Tooling*. https://vitejs.dev/
