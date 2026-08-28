# 🧪 EcoPredict & NLQ — Módulo de Aseguramiento de Calidad (QA)

Guía oficial de ejecución de pruebas automatizadas y evaluación de modelos de Inteligencia Artificial para el proyecto **EcoPredict & NLQ**.

---

## 📌 Control de Historias de Usuario y Tareas (Sprint 1)

* **HU Principal:** `HU 03-Automatización de pruebas de integración con Newman y Calidad de Prompts NLQ (#36)`
* **Sub-issues de QA:**
  * ✅ **T11 (#46):** Actualizar la colección Postman para los endpoints reales de los Flujos A y B.
  * ✅ **T12 (#47):** Incorporar casos positivos, negativos, de seguridad (X-API-Key, rate limiting) y validación de calidad de respuestas del LLM (control de alucinaciones y SQL generado).
  * 🔄 **T13 (#48):** Configurar variables de entorno para ejecutar las pruebas contra local y Oracle Cloud sin exponer credenciales.
  * ⏳ **T14 (#49):** Ejecutar Newman contra el entorno desplegado y validar los resultados de los Flujos A y B.
  * ⏳ **T15 (#50):** Registrar evidencias, resultados e incidencias y elaborar el informe técnico de calidad.

---

## 🗂️ Estructura del Módulo de QA

```text
src/ia-ops/
├── prompts/
│   ├── benchmark_eval_dataset.json   # 15 casos de referencia científica (OMS 2021 / MINAM)
│   ├── nlq_prompts.json              # 12 plantillas estructuradas de prompts
│   └── system_prompt.md              # Restricciones éticas y guardrails del modelo
└── tests/
    ├── test_llm_quality_benchmark.py # 28 tests de calidad de LLM, alucinaciones y Text-to-SQL
    ├── test_prompt_injection.py      # 36 tests de inyección (SQLi, DAN, Jailbreaks, XSS)
    ├── test_prompt_quality.py        # 27 tests estructurales de prompts JSON
    └── postman/
        ├── EcoPredict_Sprint1_Collection.json # Colección de 16 requests de API (Flujos A y B)
        └── eco_predict_nlq_environment.json   # Variables de entorno
```

---

## 🚀 Comandos de Ejecución

### 1. Pruebas Unitarias y de Seguridad en Código (pytest)
```bash
# Ejecutar los 91 tests automatizados
python -m pytest src/ia-ops/tests/ -v
```

### 2. Pruebas de API y Resiliencia en Consola (Newman CLI)
```bash
# Ejecutar las 28 aserciones de API contra el webhook n8n
newman run src/ia-ops/tests/postman/EcoPredict_Sprint1_Collection.json -e src/ia-ops/tests/postman/eco_predict_nlq_environment.json
```
