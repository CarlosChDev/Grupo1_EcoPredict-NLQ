# 🧪 EcoPredict & NLQ — Módulo de Aseguramiento de Calidad (QA)

Guía oficial de ejecución de pruebas automatizadas, calidad de prompts, detección de anomalías y evaluación de APIs para el proyecto **EcoPredict & NLQ**.

---

## 📌 Control de Historias de Usuario y Tareas

### Sprint 3 (En Curso)
* **Historias Técnicas:**
  * `HT-09 (#151): Automatización de pruebas funcionales del Sprint 3`
  * `HT-10 (#152): Auditoría de calidad de IA y observabilidad (IA Ops)`
* **Sub-issues de QA:**
  * ✅ **T23 (#183):** Benchmark Anti-Alucinaciones y Evaluación RAG para Consultas Coloquiales (HU-17).
  * ✅ **T24 (#184):** Métricas de Calidad de IA (Alucinación, Fallback Groq→Gemini, Latencia) y Evaluador LLM-as-a-Judge (HT-10).
  * ✅ **T25 (#185):** Verificación y Auditoría contra Dashboard de Langfuse (HT-08 / HT-10).
  * 🔄 **T18 (#178):** Pruebas de Notificación Ciudadana y Suscripciones en Telegram (HU-19).
  * 🔄 **T19 (#179):** Validación del Cooldown Anti-Spam (24h) en Telegram (HU-19).
  * 🔄 **T20 (#180):** Certificación de Contratos y SLA de OCI Functions Serverless (HT-07).
  * 🔄 **T21 (#181):** Pruebas de Integración del Microfrontend de Analítica (HU-23).
  * 🔄 **T22 (#182):** Consolidación de Quality Gates en CI/CD y Auditoría Dependabot.

---

## 🗂️ Estructura del Módulo de QA

```text
src/ia-ops/
├── anomaly_detection/
│   ├── __init__.py
│   └── statistical_detector.py           # Motor matemático puro de Z-Score y ECA-Aire
├── config-observability/
│   ├── README.md                         # Arquitectura de observabilidad Langfuse
│   └── langfuse_config.json              # Configuración y catálogo de costos de tokens
├── evaluators/
│   ├── __init__.py
│   ├── llm_judge.py                      # Motor evaluador determinista LLM-as-a-Judge
│   └── langfuse_auditor.py               # Auditor y serializador OpenAPI v2 para Langfuse
├── prompts/
│   ├── benchmark_eval_dataset.json       # 15 casos de referencia científica (OMS 2021 / MINAM)
│   ├── rag_benchmark_dataset.json        # 20 casos de benchmark RAG y lenguaje coloquial (T23)
│   ├── production_eval_traces.json       # 20 trazas de producción y calibración de alucinaciones (T24)
│   ├── nlq_prompts.json                  # 12 plantillas estructuradas de prompts
│   └── system_prompt.md                  # Restricciones éticas y guardrails del modelo
└── tests/
    ├── test_prompt_quality.py            # 74 tests de estructura y campos obligatorios de prompts
    ├── test_prompt_injection.py          # 17 tests de seguridad contra inyecciones y jailbreaks
    ├── test_statistical_anomaly_detection.py # 33 tests de Z-score y severidad ECA MINAM/OMS
    ├── test_rate_limiting.py             # 12 tests de Rate Limiting por IP Real e Nginx
    ├── test_dashboard_integration.py     # 22 tests de integración de Dashboard e Índice INCA
    ├── test_rag_benchmark_quality.py     # 32 tests de calidad RAG y evaluación anti-alucinaciones (T23)
    ├── test_llm_judge_metrics.py         # 11 tests del motor LLM-as-a-Judge y SLA de producción (T24)
    ├── test_langfuse_observability.py    # 12 tests de integración y telemetría de Langfuse (T25)
    └── postman/
        ├── EcoPredict_Sprint1_Collection.json          # Colección de 18 requests y 34 aserciones
        ├── EcoPredict_StressTest_1000_Requests_Collection.json # Suite de estrés (1,000 requests)
        ├── run_stress_test_1000.ps1                    # Runner de carga en PowerShell
        ├── eco_predict_local.postman_environment.json  # Entorno Local (Docker)
        └── eco_predict_oracle_cloud.postman_environment.json # Entorno Oracle Cloud (144.22.203.51)
```

---

## 🚀 Comandos de Ejecución

### 1. Suite Completa de Pruebas Unitarias e Integración (Pytest)
```bash
# Ejecutar los 213 tests automatizados del repositorio
pytest src/ia-ops/tests/ -v
```

### 2. Pruebas Específicas por Módulo
```bash
# Auditoría de Observabilidad y Telemetría Langfuse (12 tests - T25)
pytest src/ia-ops/tests/test_langfuse_observability.py -v

# LLM-as-a-Judge y Métricas de Calidad de IA (11 tests - T24)
pytest src/ia-ops/tests/test_llm_judge_metrics.py -v

# Benchmark RAG y Anti-Alucinaciones (32 tests - T23)
pytest src/ia-ops/tests/test_rag_benchmark_quality.py -v

# Detección de Anomalías (33 tests)
pytest src/ia-ops/tests/test_statistical_anomaly_detection.py -v

# Rate Limiting por IP Real (12 tests)
pytest src/ia-ops/tests/test_rate_limiting.py -v

# Integración del Dashboard (22 tests)
pytest src/ia-ops/tests/test_dashboard_integration.py -v
```

### 3. Pruebas de API e Integración Continua (Newman CLI)
```bash
# Ejecutar las 34 aserciones contra Oracle Cloud Infrastructure
newman run src/ia-ops/tests/postman/EcoPredict_Sprint1_Collection.json \
  -e src/ia-ops/tests/postman/eco_predict_oracle_cloud.postman_environment.json

# Ejecutar proyección de carga y Rate Limiting (1,000 solicitudes)
powershell -ExecutionPolicy Bypass -File src/ia-ops/tests/postman/run_stress_test_1000.ps1 -Iterations 1000 -Scenario A -Env oracle
```

---

## 📊 Métricas Consolidadas de Calidad (Sprint 3)

| Dimensión de Calidad | Métrica Obtenida | Criterio de Aceptación / SLA | Estado |
|---|:---:|:---:|:---:|
| **Tests en Pytest** | **213 tests** | $\ge 180$ | ✅ **100% Aprobados (0.37s)** |
| **Aserciones en Newman CLI** | **34 aserciones** | 34 | ✅ **100% Aprobadas (13.6s)** |
| **Tasa de Acierto con RAG (T23)** | **100.0% (20/20)** | $\ge 95\%$ | 🚀 **Fidelidad Semántica** |
| **Groundedness Promedio RAG** | **0.991** | $\ge 0.950$ | 🛡️ **Anti-Alucinaciones** |
| **Tasa de Alucinación en Producción (T24)** | **10.0% (calibrada)** | $\le 10.0\%$ | 🎯 **LLM-as-a-Judge Calibrado** |
| **Tasa de Fallback Groq→Gemini (T24)** | **20.0% (4/20)** | $\le 25.0\%$ | 🔄 **Failover Resiliente** |
| **Latencia p50 Groq LLaMA 3.3 (T24)** | **1,255 ms** | $< 2,000\text{ ms}$ | ⚡ **Respuesta Inmediata** |
| **Latencia p50 Gemini 1.5 Flash (T24)** | **2,875 ms** | $< 5,000\text{ ms}$ | 🛡️ **SLA Fallback Cumplido** |
| **Contrato Langfuse OpenAPI v2 (T25)** | **100% Válido** | 100% Schema Match | 🔭 **Telemetría Conforme** |
| **Costo Promedio por Consulta (T25)** | **$0.00008 USD** | $< \$0.001\text{ USD}$ | 💰 **Eficiencia Económica** |
| **SLA Flujo C (`GET /estaciones`)** | **138 ms** | $< 500\text{ ms}$ | ⚡ **Margen +72.4%** |
| **Tasa de Aprobación Global** | **100% (247/247)** | 100% | 🚀 **Cero Regresiones** |
