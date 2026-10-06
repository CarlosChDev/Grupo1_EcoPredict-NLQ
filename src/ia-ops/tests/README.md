# 🧪 EcoPredict & NLQ — Módulo de Aseguramiento de Calidad (QA)

Guía oficial de ejecución de pruebas automatizadas, calidad de prompts, detección de anomalías y evaluación de APIs para el proyecto **EcoPredict & NLQ**.

---

## 📌 Control de Historias de Usuario y Tareas (Sprint 2)

* **HU Principal:** `HU-16 - Calidad, Detección de Anomalías, Flujo C y Rate Limiting (#100)`
* **Sub-issues de QA:**
  * ✅ **T14 (#116):** Validación de Detección de Anomalías con Pytest (Z-Score y umbrales ECA MINAM/OMS).
  * ✅ **T15 (#117):** Validación del Flujo C (`GET /estaciones`) con Postman y Newman CLI.
  * ✅ **T16 (#118):** Pruebas de Rate Limiting por IP Real en Nginx (`X-Forwarded-For`, 10 req/min).
  * ✅ **T17 (#119):** Pruebas de Integración y Visualización del Dashboard (Índice INCA y Ranking).
  * ✅ **T18 (#120):** CI/CD Quality Gates e Informe Técnico Consolidado de Calidad del Sprint 2.

---

## 🗂️ Estructura del Módulo de QA

```text
src/ia-ops/
├── anomaly_detection/
│   ├── __init__.py
│   └── statistical_detector.py           # Motor matemático puro de Z-Score y ECA-Aire
├── prompts/
│   ├── benchmark_eval_dataset.json       # 15 casos de referencia científica (OMS 2021 / MINAM)
│   ├── nlq_prompts.json                  # 12 plantillas estructuradas de prompts
│   └── system_prompt.md                  # Restricciones éticas y guardrails del modelo
└── tests/
    ├── test_prompt_quality.py            # 74 tests de estructura y campos obligatorios de prompts
    ├── test_prompt_injection.py          # 17 tests de seguridad contra inyecciones y jailbreaks
    ├── test_statistical_anomaly_detection.py # 33 tests de Z-score y severidad ECA MINAM/OMS
    ├── test_rate_limiting.py             # 12 tests de Rate Limiting por IP Real e Nginx
    ├── test_dashboard_integration.py     # 22 tests de integración de Dashboard e Índice INCA
    └── postman/
        ├── EcoPredict_Sprint1_Collection.json          # Colección de 18 requests y 34 aserciones (Flujos A, B y C)
        ├── eco_predict_local.postman_environment.json  # Entorno Local (Docker)
        └── eco_predict_oracle_cloud.postman_environment.json # Entorno Oracle Cloud (144.22.203.51)
```

---

## 🚀 Comandos de Ejecución

### 1. Suite Completa de Pruebas Unitarias e Integración (Pytest)
```bash
# Ejecutar los 158 tests automatizados del repositorio
pytest src/ia-ops/tests/ -v
```

### 2. Pruebas Específicas por Módulo
```bash
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
```

---

## 📊 Métricas Consolidadas de Calidad (Sprint 2)

| Dimensión de Calidad | Métrica Obtenida | Criterio de Aceptación / SLA | Estado |
|---|:---:|:---:|:---:|
| **Tests en Pytest** | **158 tests** | $\ge 150$ | ✅ **100% Aprobados (0.42s)** |
| **Aserciones en Newman CLI** | **34 aserciones** | 34 | ✅ **100% Aprobadas (16.1s)** |
| **SLA Flujo C (`GET /estaciones`)** | **138 ms** | $< 500\text{ ms}$ | ⚡ **Margen +72.4%** |
| **Compilación Frontend** | **85 módulos** | 0 errores TypeScript | ✅ **100% Limpio (501ms)** |
| **Tasa de Aprobación Global** | **100% (192/192)** | 100% | 🚀 **Cero Regresiones** |

---

## ⚙️ Quality Gates en CI/CD (GitHub Actions)

Los flujos de trabajo en `.github/workflows/` ejecutan automáticamente las validaciones ante cada PR:
* `ai-testing-ci.yml`: Ejecuta `pytest src/ia-ops/tests -v` (158 tests).
* `newman-ci.yml`: Valida los contratos de API con Newman CLI.
* `frontend-ci.yml`: Valida el build de TypeScript y Vite.
* `dast.yml`: Análisis dinámico de seguridad OWASP ZAP.
