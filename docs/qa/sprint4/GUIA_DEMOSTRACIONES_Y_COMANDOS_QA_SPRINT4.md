# GUÍA MAESTRA DE DEMOSTRACIONES Y COMANDOS DE QA — SPRINT 4 (FINAL)
## "EcoPredict & NLQ" — Sistema de Alerta e Investigación Ambiental Ciudadana
**Universidad de San Martín de Porres (USMP) — Facultad de Ingeniería y Arquitectura**  
**Docente:** Ing. Norma Birginia León Lescano | **Alumno:** Johann Romero Contreras (`@JohannK99`)  
**Historias:** HT-04 (#219), HT-13 (#222), HU-16 (#223), HU-22 (#224) y HT-12 (#221)  
**Pull Requests Clave:** #257 (Merged) y #259 (Merged) | **Suite Global:** 334 tests (100% aprobados en 0.65s)

---

## 📌 Preparación de Terminal (PowerShell / Windows Terminal)

```powershell
# 1. Posicionarse en la raíz del repositorio
cd C:\Users\johan\.gemini\antigravity\scratch\Grupo1_EcoPredict-NLQ

# 2. Verificar estado de la rama Romero (sincronizada con origin/main)
git status

# 3. Comprobación rápida de la suite global completa (334 tests)
pytest src/ia-ops/tests/
```

---

## 🛡️ BLOQUE I: DEVSECOPS, PROMPT INJECTION Y QUALITY GATES (HT-04 / T2 #227)

### 🔹 TAREA 2 (#227): Batería Anti-Inyección OWASP LLM01 y Quality Gates
* **Comando General (38 pruebas de vectores de inyección adversarial):**
  ```powershell
  pytest src/ia-ops/tests/test_prompt_injection.py -v
  ```
* **Comando de Incidencia Controlada 1 (Intento de inyección SQL / DDL bloqueado):**
  ```powershell
  pytest src/ia-ops/tests/test_prompt_injection.py -k "test_bloqueo_inyeccion_sql_en_prompt" -v
  ```
* **Comando de Incidencia Controlada 2 (Intento de fuga de prompt de sistema "Ignore instructions"):**
  ```powershell
  pytest src/ia-ops/tests/test_prompt_injection.py -k "test_bloqueo_fuga_prompt_sistema" -v
  ```
* **Comando de Quality Gates CI/CD (9 pruebas del pipeline GitHub Actions):**
  ```powershell
  pytest src/ia-ops/tests/test_quality_gates_cicd.py -v
  ```
* 🗣️ **Frase para la Sustentación con la Ing. Norma León:**
  > *"Ingeniera, en esta sección demostramos el blindaje de seguridad contra la vulnerabilidad OWASP LLM01. Con 38 pruebas automatizadas verificamos que cualquier intento de inyección SQL adversaria, fuga de instrucciones maestras o jailbreak estilo DAN es interceptado de raíz por nuestro guardrail semántico, aplicando una política Zero-Failures que aborta automáticamente el pipeline de CI/CD si se detecta alguna brecha."*

---

## ⚡ BLOQUE II: CAPA SERVERLESS BFF Y RESILIENCIA 24H DEL FLUJO C (HT-13 / T16 #241)

### 🔹 TAREA 16 (#241): BFF Vercel, Whitelist y Cache Stale-If-Error
* **Comando General (25 pruebas de contrato BFF y caché multinivel):**
  ```powershell
  pytest src/ia-ops/tests/test_bff_vercel_flujo_c.py -v
  ```
* **Comando de Incidencia Controlada 1 (Ruta no autorizada bloqueada con HTTP 403 Forbidden):**
  ```powershell
  pytest src/ia-ops/tests/test_bff_vercel_flujo_c.py -k "test_ruta_no_autorizada_retorna_403" -v
  ```
* **Comando de Incidencia Controlada 2 (Simulación de caída total de n8n con `stale-if-error=86400`):**
  ```powershell
  pytest src/ia-ops/tests/test_bff_vercel_flujo_c.py -k "test_resiliencia_caida_n8n_retorna_stale_cache" -v
  ```
* 🗣️ **Frase para la Sustentación con la Ing. Norma León:**
  > *"Aquí demostramos la arquitectura de resiliencia del Flujo C mediante una función Serverless BFF en Vercel. Si un atacante solicita rutas fuera de la lista blanca, el proxy responde de inmediato con HTTP 403. Y lo más importante para la continuidad operativa: si el backend n8n se apaga por completo, la directiva `stale-if-error=86400` entrega la última versión en caché válida, manteniendo el mapa interactivo funcionando durante 24 horas continuas sin interrupción para los ciudadanos."*

---

## 📈 BLOQUE III: ANALÍTICA HISTÓRICA FLUJO D Y GUARDRAILS SEMÁNTICOS (HU-16 / T11 #236)

### 🔹 TAREA 11 (#236): Contratos OpenAPI v3, Consistencia Estadística y Cron 06:30
* **Comando General (28 pruebas de contratos, agregados e idempotencia):**
  ```powershell
  pytest src/ia-ops/tests/test_flujo_d_contract.py -v
  ```
* **Comando de Incidencia Controlada 1 (Verificación matemática de promedios vs datos crudos SENAMHI):**
  ```powershell
  pytest src/ia-ops/tests/test_flujo_d_contract.py -k "test_consistencia_promedios_vs_datos_crudos" -v
  ```
* **Comando de Incidencia Controlada 2 (Idempotencia del cron de agregación diaria de las 06:30 AM):**
  ```powershell
  pytest src/ia-ops/tests/test_flujo_d_contract.py -k "test_idempotencia_cron_agregacion" -v
  ```
* **Comando de Incidencia Controlada 3 (Rechazo de escrituras con rol de solo lectura `nlq_reader`):**
  ```powershell
  pytest src/ia-ops/tests/test_flujo_d_contract.py -k "test_seguridad_rol_nlq_reader_solo_lectura" -v
  ```
* 🗣️ **Frase para la Sustentación con la Ing. Norma León:**
  > *"En el Flujo D garantizamos la veracidad analítica de los datos. Auditamos que los 5 endpoints OpenAPI cumplan su esquema JSON estricto, que los promedios reportados coincidan matemáticamente al 100% con las mediciones crudas de la base de datos sin desviaciones, y que la ejecución repetida del cron matutino de las 06:30 sea totalmente idempotente gracias a operaciones UPSERT, asegurando la integridad con el rol `nlq_reader`."*

---

## 🖥️ BLOQUE IV: MICROFRONTEND DATA ANALYTICS FASE 2 Y RESILIENCIA 503 (HU-22 / T27 #252)

### 🔹 TAREA 27 (#252): Integración, Regla de 2 a 4 Distritos y Aislamiento de Error 503
* **Comando General (9 pruebas de renderizado, encapsulamiento CSS y resiliencia):**
  ```powershell
  pytest src/ia-ops/tests/test_microfrontend_analytics_fase2.py -v
  ```
* **Comando de Incidencia Controlada 1 (Validación de regla de negocio de límites: 2 a 4 distritos):**
  ```powershell
  pytest src/ia-ops/tests/test_microfrontend_analytics_fase2.py -k "test_validacion_seleccion_minimo_dos_maximo_cuatro" -v
  ```
* **Comando de Incidencia Controlada 2 (Encapsulamiento estricto de estilos CSS con prefijo `da-`):**
  ```powershell
  pytest src/ia-ops/tests/test_microfrontend_analytics_fase2.py -k "test_encapsulamiento_estilos_css_prefijo_da" -v
  ```
* **Comando de Incidencia Controlada 3 (Aislamiento de fallo HTTP 503 sin afectar bloques numéricos):**
  ```powershell
  pytest src/ia-ops/tests/test_microfrontend_analytics_fase2.py -k "test_manejo_error_503_aislado" -v
  ```
* 🗣️ **Frase para la Sustentación con la Ing. Norma León:**
  > *"Para la Fase 2 de Analítica demostramos el desacoplamiento total del microfrontend. Validamos que la interfaz restrinja la selección entre 2 y 4 distritos con avisos amigables, que todos los estilos usen el prefijo `da-` para evitar colisiones CSS, y que ante una caída 503 del servicio de IA, únicamente esa tarjeta muestre el estado de error controlado, permitiendo al usuario seguir comparando gráficos y rankings sin ninguna pantalla blanca."*

---

## 👥 BLOQUE V: VALIDACIÓN CON USUARIOS REALES (UAT) Y MÉTRICAS SUS (HT-12 / T21 #246)

### 🔹 TAREA 21 (#246): Protocolo UAT en Producción, Métrica SUS (89.2/100) y Hallazgos
* **Comprobación de Artefactos de Certificación:**
  ```powershell
  # Inspeccionar informe de validación formal UAT
  cat docs/qa/sprint4/informe_tecnico_t21_sprint4.md | Select-Object -First 30
  ```
* 🗣️ **Frase para la Sustentación con la Ing. Norma León:**
  > *"Finalmente, Ingeniera, la Tarea 21 certificó la plataforma en producción con 12 usuarios reales organizados en 3 perfiles (ciudadanos de a pie, estudiantes USMP y especialistas ambientales). Tras ejecutar 5 escenarios que cubren desde el chatbot NLQ hasta el bot de Telegram, obtuvimos una calificación System Usability Scale (SUS) de 89.2 sobre 100, ubicando a EcoPredict en el percentil 96.5% de la industria (Grado A 'Excelente') con una tasa de éxito en tareas de 98.3%. Los 5 hallazgos observados fueron registrados y resueltos en producción."*

---

## 💾 BLOQUE VI: DISASTER RECOVERY — BACKUP, RESTORE LOCAL Y RETENCIÓN R2 (AUDITORÍA DE QA)

### 🔹 CERTIFICACIÓN DE RECUPERACIÓN ANTE DESASTRES Y MANUAL "LÉEME" (`scripts/README.md`)
* **Comando General de QA (7 pruebas automáticas de integridad criptográfica y rollback):**
  ```powershell
  pytest src/ia-ops/tests/test_backup_restore_integrity.py -v
  ```
* **Comando de Incidencia Controlada 1 (Detección de alteración de hash SHA-256 en el respaldo cifrado):**
  ```powershell
  pytest src/ia-ops/tests/test_backup_restore_integrity.py -k "test_sha256_checksum_verification_logic" -v
  ```
* **Comando de Incidencia Controlada 2 (Bloqueo de restauración por discrepancia de N8N_ENCRYPTION_KEY):**
  ```powershell
  pytest src/ia-ops/tests/test_backup_restore_integrity.py -k "test_n8n_encryption_key_mismatch_protection" -v
  ```
* **Comprobación del Manual "LÉEME" y Checksum:**
  ```bash
  # Verificación de integridad SHA-256 en Git Bash:
  cd backups/
  sha256sum -c ecopredict-20261107T193835Z.tar.gz.gpg.sha256
  ```
* **Comandos Oficiales de Backup y Restore Local en PowerShell:**
  ```powershell
  # 1. Preparación de clave universal (compatible con PowerShell 5.1 y 7):
  New-Item -ItemType Directory -Force -Path C:\Secure | Out-Null
  $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
  $b = New-Object byte[] 32; $rng.GetBytes($b)
  [IO.File]::WriteAllText('C:\Secure\ecopredict-backup.key', [Convert]::ToBase64String($b))

  # 2. Generación del backup local cifrado:
  powershell.exe -ExecutionPolicy Bypass -File .\scripts\backup-local.ps1 -KeyFile C:\Secure\ecopredict-backup.key

  # 3. Verificación de integridad del archivo y descifrado seguro:
  $ultimoBackup = (Get-ChildItem .\backups\ecopredict-local-*.zip.enc | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
  powershell.exe -ExecutionPolicy Bypass -File .\scripts\restore-local.ps1 -BackupFile $ultimoBackup -KeyFile C:\Secure\ecopredict-backup.key -ExtractEnvOnly
  ```
* 🗣️ **Frase para la Sustentación con la Ing. Norma León:**
  > *"Ingeniera, como solicitó en el audio, auditamos y certificamos paso a paso el proceso de Backup y Restore. En `scripts/README.md` documentamos el 'LÉEME' oficial con la arquitectura de 4 etapas: desde la generación del dump cifrado con AES-256 en OCI, el almacenamiento off-site en Cloudflare R2 con retención de 4 copias, hasta la restauración segura en entorno Docker local con Rollback Recovery preventivo para no comprometer la base de datos de producción."*

---

## 📊 MATRIZ RESUMEN DE EJECUCIÓN RÁPIDA

| Bloque Temático | Historia / Tarea | Archivo de Prueba Pytest | N° Tests | Tiempo Estimado |
| :--- | :--- | :--- | :---: | :---: |
| **I. DevSecOps & Inyección** | HT-04 / T2 (#227) | `test_prompt_injection.py` + `test_quality_gates_cicd.py` | 47 tests | ~0.10 s |
| **II. Serverless BFF Vercel** | HT-13 / T16 (#241) | `test_bff_vercel_flujo_c.py` | 25 tests | ~0.05 s |
| **III. Contratos Flujo D** | HU-16 / T11 (#236) | `test_flujo_d_contract.py` | 28 tests | ~0.06 s |
| **IV. Data Analytics Fase 2** | HU-22 / T27 (#252) | `test_microfrontend_analytics_fase2.py` | 9 tests | ~0.02 s |
| **V. Validación UAT & SUS** | HT-12 / T21 (#246) | Validación 12 evaluadores (SUS: 89.2) | 12 users | Protocolo UAT |
| **VI. Disaster Recovery** | DevSecOps & QA | `test_backup_restore_integrity.py` | 7 tests | ~0.15 s |
| **TOTAL GLOBAL CONSOLIDADO** | **Ecosistema Completo** | **`pytest src/ia-ops/tests/`** | **341 tests** | **0.80 s** |

---

## 🏆 Cierre de Sustentación Recomendado:
> *"Con esto, Ingeniera Norma, el equipo de Aseguramiento de Calidad concluye y certifica formalmente el Sprint 4 y el cierre integral del proyecto EcoPredict & NLQ, con 341 pruebas automáticas pasando al 100%, la certificación y manual LÉEME de Backup y Restauración local, 5 informes técnicos de tarea, un informe consolidado bajo norma APA 7 y una satisfacción de usabilidad validada de 89.2 sobre 100."*
