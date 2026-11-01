# GUÍA MAESTRA DE DEMOSTRACIONES Y COMANDOS DE QA — SPRINT 3
## "EcoPredict & NLQ" — Sistema de Alerta e Investigación Ambiental Ciudadana
**Universidad de San Martín de Porres (USMP) — Facultad de Ingeniería y Arquitectura**  
**Docente:** Ing. Norma Birginia León Lescano | **Alumno:** Johann Romero Contreras (`@JohannK99`)  
**Historias Técnicas:** HT-10 (#152) y HT-09 (#151) | **PRs:** #200 (Merged) y #207 (Merged)  

---

## 📌 Preparación de Terminal (PowerShell / Bash)

```powershell
# 1. Posicionarse en la raíz del proyecto
cd C:\Users\johan\.gemini\antigravity\scratch\Grupo1_EcoPredict-NLQ

# 2. Verificar estado de la rama
git status
```

---

## 🧠 BLOQUE I: IA OPS, BENCHMARK RAG Y OBSERVABILIDAD (HT-10 / PR #200)

### 🔹 TAREA 23 (#183): Benchmark Anti-Alucinaciones RAG
* **Comando General (32 pruebas del benchmark con y sin contexto):**
  ```powershell
  pytest src/ia-ops/tests/test_rag_benchmark_quality.py -v
  ```
* **Comando de Incidencia Controlada (Ataques de SQL Injection y Prompt Override bloqueados):**
  ```powershell
  pytest src/ia-ops/tests/test_rag_benchmark_quality.py -k "test_resistencia_inyeccion" -v
  ```
* 🗣️ **Frase para la Sustentación:**
  > *"Aquí demuestro cómo el RAG con `pgvector` neutraliza al 100% las inyecciones SQL adversarias (`DROP TABLE`, `OR 1=1`) y cómo modismos peruanos como 'La Rica Vicky' o 'aire pesado' resuelven con exactitud matemática la estación oficial y la norma ECA sin alucinar."*

---

### 🔹 TAREA 24 (#184): Métricas de Producción y Evaluador LLM-as-a-Judge
* **Comando General (11 pruebas de evaluación algorítmica determinista):**
  ```powershell
  pytest src/ia-ops/tests/test_llm_judge_metrics.py -v
  ```
* **Comando de Incidencia Controlada (Detección de alucinación numérica fuera de tolerancia):**
  ```powershell
  pytest src/ia-ops/tests/test_llm_judge_metrics.py -k "test_deteccion_alucinacion_numerica_fuera_de_tolerancia" -v
  ```
* 🗣️ **Frase para la Sustentación:**
  > *"Aquí corre nuestro juez determinista en Python. Si el LLM emite una concentración de PM2.5 con más de un 10% de desviación del dato real de la base de datos, el evaluador la marca de inmediato como alucinación. Nuestra tasa de alucinación global se calibró en 10.0%, dentro del límite del 15%."*

---

### 🔹 TAREA 25 (#185): Telemetría y Costos con Langfuse
* **Comando General (12 pruebas de esquemas OpenAPI v2 y catálogo de tokens):**
  ```powershell
  pytest src/ia-ops/tests/test_langfuse_observability.py -v
  ```
* **Comando de Incidencia Controlada (Validación de límites SLA y fallback por timeout de Groq):**
  ```powershell
  pytest src/ia-ops/tests/test_langfuse_observability.py -k "test_alerta_violacion_sla_latencia" -v
  ```
* 🗣️ **Frase para la Sustentación:**
  > *"Este comando valida que si la llamada a Groq supera los 2 segundos, Langfuse genera automáticamente la alerta de violación de SLA y audita la conmutación al modelo de respaldo Gemini Flash, registrando el costo exacto por token sin discrepancias (\$0.00035 USD en Groq vs \$0.00008 USD en Gemini)."*

---

## 📱 BLOQUE II: MENSAJERÍA CIUDADANA Y ANTI-SPAM (HT-09 / PR #207)

### 🔹 TAREA 18 (#178): Notificación y Suscripción en Telegram
* **Comando General (14 pruebas de ciclo de vida del bot y comandos):**
  ```powershell
  pytest src/ia-ops/tests/test_telegram_subscription.py -v
  ```
* **Comando de Incidencia Controlada (Ciudadano intenta suscribirse a estación inexistente o sin número):**
  ```powershell
  pytest src/ia-ops/tests/test_telegram_subscription.py -k "test_comando_suscribir_estacion_inexistente or test_comando_suscribir_sin_numero" -v
  ```
* 🗣️ **Frase para la Sustentación:**
  > *"Aquí vemos las pruebas negativas del bot `@ecopredict_lima_bot`. Si un usuario escribe `/suscribir 99` o `/suscribir` sin argumentos, el bot no se rompe: captura el error y le muestra de forma guiada el listado oficial de estaciones activas."*

---

### 🔹 TAREA 19 (#179): Cooldown Anti-Spam de 24 Horas en Telegram
* **Comando General (8 pruebas del algoritmo de cooldown temporal):**
  ```powershell
  pytest src/ia-ops/tests/test_telegram_cooldown.py -v
  ```
* **Comando de Incidencia Controlada (Intento de enviar alerta duplicada antes de 24h es bloqueado):**
  ```powershell
  pytest src/ia-ops/tests/test_telegram_cooldown.py -k "test_segunda_alerta_mismo_parametro_bloqueada_dentro_de_24h" -v
  ```
* 🗣️ **Frase para la Sustentación:**
  > *"Este es el núcleo anti-spam. Si la estación de San Juan de Lurigancho sigue con exceso de PM2.5 dos horas después, el sistema bloquea el reenvío. Pero si ocurre una anomalía de un contaminante distinto como PM10, el sistema sí lo despacha, aislando por parámetro y suscriptor."*

---

## ☁️ BLOQUE III: SERVERLESS EN OCI Y MICROFRONTENDS (HT-09 / PR #207)

### 🔹 TAREA 20 (#180): Contratos y SLA de OCI Functions Serverless
* **Comando General (10 pruebas de contratos HTTP y JSON Schema):**
  ```powershell
  pytest src/ia-ops/tests/test_oci_functions_contract.py -v
  ```
* **Comando de Incidencias Controladas (Demuestra los códigos 400, 401, 422, 500 y 504):**
  ```powershell
  pytest src/ia-ops/tests/test_oci_functions_contract.py -k "test_error" -v
  ```
* 🗣️ **Frase para la Sustentación:**
  > *"Aquí demuestro la matriz de errores RESTful en la nube de Oracle: HTTP 400 por rango inválido, 401 si no hay token, 422 si las fechas están invertidas, 500 si la base de datos se desconecta temporalmente sin filtrar credenciales, y 504 si se excede el SLA de 10 segundos."*

---

### 🔹 TAREA 21 (#181): Microfrontend de Analítica `<mfe-analytics>`
* **Comando General (11 pruebas de Custom Elements, Shadow DOM y Chart.js):**
  ```powershell
  pytest src/ia-ops/tests/test_microfrontend_analytics.py -v
  ```
* **Comando de Incidencia Controlada (Simulación de caída de red 503 y renderizado de fallback amigable):**
  ```powershell
  pytest src/ia-ops/tests/test_microfrontend_analytics.py -k "test_manejo_de_errores_red_renderiza_fallback_amigable" -v
  ```
* 🗣️ **Frase para la Sustentación:**
  > *"Si la API externa falla con un error 503, el microfrontend destruye los skeletons de carga y renderiza un contenedor accesible con un botón de reintento (`btn-retry`), evitando que la pantalla del usuario se quede en blanco o congelada."*

---

## 🛡️ BLOQUE IV: DEVSECOPS Y PRUEBAS DE ESTRÉS (HT-09 / PR #207)

### 🔹 TAREA 22 (#182): Quality Gates en CI/CD
* **Comando General (8 pruebas auditando los workflows de GitHub Actions):**
  ```powershell
  pytest src/ia-ops/tests/test_quality_gates_cicd.py -v
  ```
* 🗣️ **Frase para la Sustentación:**
  > *"Esta suite audita automáticamente los flujos de GitHub Actions (`ai-testing-ci`, `newman-ci`, `frontend-ci`, `sast-codeql`, `dast-owasp`, `n8n-validate` y `cd`), garantizando que ningún Pull Request pase a producción sin que todas las pruebas estén en verde."*

---

### 🔹 PRUEBA DE CARGA Y ESTRÉS (1,000 Peticiones en Oracle Cloud)
* **Comando para ejecutar la prueba de estrés de Rate Limiting:**
  ```powershell
  powershell -ExecutionPolicy Bypass -File src/ia-ops/tests/postman/run_stress_test_1000.ps1
  ```
* 🗣️ **Frase para la Sustentación:**
  > *"Ejecutamos 1,000 solicitudes continuas contra la IP de Oracle Cloud (`144.22.203.51`). Demostramos que a partir de la petición 11 el gateway bloquea deterministamente con HTTP 429 Too Many Requests, mientras que IPs distintas mantienen sus contadores aislados sin falsos bloqueos."*

---

## 🏆 DEMOSTRACIÓN FINAL: LA SUITE COMPLETA CONSOLIDADA

```powershell
pytest src/ia-ops/tests/ -v
```

⏱️ **Tiempo de ejecución:** ~0.50 - 0.64 segundos  
📊 **Resultado:** **264 passed (100% de éxito)**

> **Frase de cierre:** *"Ingeniera Norma, como puede comprobar en pantalla, las 264 pruebas automatizadas cubren desde la matemática del RAG hasta la seguridad de la infraestructura en la nube, certificando el cumplimiento del 100% de los criterios de aceptación del Sprint 3."*
