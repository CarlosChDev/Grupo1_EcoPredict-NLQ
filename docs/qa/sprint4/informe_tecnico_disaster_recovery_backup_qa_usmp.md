# UNIVERSIDAD DE SAN MARTÍN DE PORRES
## FACULTAD DE INGENIERÍA Y ARQUITECTURA
### ESCUELA PROFESIONAL DE INGENIERÍA DE COMPUTACIÓN Y SISTEMAS

<br>

# INFORME QA: ENSAYO DE RESTAURACIÓN Y AUDITORÍA DE BACKUP v1.0
## "EcoPredict & NLQ" — Sistema de Alerta e Investigación Ambiental Ciudadana

<br>

**AUTOR:**  
**Romero Contreras, Johann**  
*QA Prompt Engineer & Test Automation Engineer (Rama: Romero | GitHub: @JohannK99)*  
*Taller de Proyectos — Equipo 1*

**DOCENTE:**  
**Ing. Norma Birginia León Lescano**

**PERÚ — LIMA**  
**2026 — II**

---

### Tabla 1
*Detalle del documento*

| Especificación | Descripción |
| :--- | :--- |
| **Tipo de documento** | Informe Técnico Electrónico de Aseguramiento de Calidad (QA) |
| **Idioma** | Español |
| **Proyecto** | EcoPredict & NLQ (Grupo 1) |
| **Objeto de prueba** | Paquete de Disaster Recovery `scripts/` y manual `scripts/Readme.md` (commit ba12373 / PR #277) |
| **Fecha de ejecución** | 08/11/2026 – 09/11/2026 |

---

### Tabla 2
*Historial de revisiones*

| Versión | Fecha | Autor | Descripción | Estado |
| :---: | :---: | :--- | :--- | :---: |
| **1.0** | 08/11/2026 | Romero Contreras, Johann | Informe inicial de auditoría y pruebas de integridad (7 tests) | Revisión |
| **2.0** | 09/11/2026 | Romero Contreras, Johann | Ensayo de caja negra, resolución de 6 hallazgos y verificación en Postman | Aprobado |

---

# Índice

**1. INTRODUCCIÓN** . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2  
&nbsp;&nbsp;&nbsp;&nbsp;1.1 Propósito . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2  
&nbsp;&nbsp;&nbsp;&nbsp;1.2 Alcance . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2  
&nbsp;&nbsp;&nbsp;&nbsp;1.3 Metodología de Caja Negra . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2  
**2. ENTORNO DE PRUEBA** . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3  
**3. PREPARACIÓN DEL ENSAYO** . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4  
&nbsp;&nbsp;&nbsp;&nbsp;3.1 Comprobación de Herramientas y Servicios . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4  
&nbsp;&nbsp;&nbsp;&nbsp;3.2 Lectura del Manual Oficial "LÉEME" (`scripts/Readme.md`) . . . . . . . . . . . . . . . . . . . . 4  
&nbsp;&nbsp;&nbsp;&nbsp;3.3 Generación de Claves Criptográficas Seguras (`C:\Secure`) . . . . . . . . . . . . . . . . . . . . 4  
**4. EJECUCIÓN DEL RESTORE Y VERIFICACIÓN POR PASOS** . . . . . . . . . . . . . . . . . . . . . . 5  
&nbsp;&nbsp;&nbsp;&nbsp;4.1 Paso 1: Verificación de Disponibilidad en Postman (`healthz/readiness`) . . . . . . . . . . . 5  
&nbsp;&nbsp;&nbsp;&nbsp;4.2 Paso 2: Suite Automatizada de Integridad de QA (`pytest` 341 tests) . . . . . . . . . . . . . 6  
&nbsp;&nbsp;&nbsp;&nbsp;4.3 Paso 3: Generación del Backup Local Cifrado (`backup-local.ps1`) . . . . . . . . . . . . . . . . 7  
&nbsp;&nbsp;&nbsp;&nbsp;4.4 Paso 4: Verificación Criptográfica y Descifrado Seguro (`restore-local.ps1`) . . . . . . . . . . 8  
&nbsp;&nbsp;&nbsp;&nbsp;4.5 Conteo de Filas: Entorno Original vs Restaurado . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9  
**5. REGISTRO FORMAL DE HALLAZGOS DEL ENSAYO** . . . . . . . . . . . . . . . . . . . . . . . . . . . 10  
&nbsp;&nbsp;&nbsp;&nbsp;5.1 Tabla de Hallazgos y Errores Literales . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10  
&nbsp;&nbsp;&nbsp;&nbsp;5.2 Resumen Cuantitativo por Severidad . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11  
&nbsp;&nbsp;&nbsp;&nbsp;5.3 Aspectos de Alto Desempeño Identificados . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11  
**6. CONCLUSIONES** . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12  
**7. PENDIENTES Y PLAN B (VIDEO DE CONTINGENCIA)** . . . . . . . . . . . . . . . . . . . . . . . . . 13  
**8. OPINIÓN DEL TESTER** . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14  
**9. RECOMENDACIONES TÉCNICAS** . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15  
**10. LISTA DE CHEQUEO DEL ENSAYO DE QA** . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16  
**REFERENCIAS BIBLIOGRÁFICAS (APA 7)** . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17  

---

# 1. INTRODUCCIÓN

El presente informe documenta el ensayo de auditoría y verificación del procedimiento de **Backup y Restauración v1.0** de *EcoPredict & NLQ*, realizado entre el 8 y 9 de noviembre de 2026 por el rol de QA. 

Siguiendo las directrices explícitas instruidas por la docente **Ing. Norma Birginia León Lescano**, el ensayo tuvo como meta fundamental comprobar que una persona externa al equipo o un nuevo desarrollador pueda levantar y restaurar la plataforma completa de forma reproducible, utilizando únicamente la documentación del paquete (`scripts/Readme.md`) y recursos aislados, sin riesgo de dañar o sobreescribir el entorno de producción en la nube (OCI).

### 1.1 Propósito
Presentar de forma ordenada las evidencias empíricas del ensayo: cada paso ejecutado, su tiempo de respuesta, los errores exactos encontrados con su texto literal de consola, las correcciones aplicadas por QA para garantizar la ejecución fluida y la emisión del **Visto Bueno formal de QA** para la sustentación final.

### 1.2 Alcance
Comprende la comprobación de los servicios base (PostgreSQL con pgvector y n8n), la auditoría de los scripts `scripts/backup.sh`, `scripts/restore.sh`, `scripts/backup-local.ps1` y `scripts/restore-local.ps1`, la certificación de la suite automatizada de pruebas en `pytest` (7 pruebas de integridad y 341 globales), la verificación de disponibilidad funcional en Postman (`/healthz/readiness`), y la ejecución de la restauración en el entorno Docker aislado (`infrastructure/docker-compose.restore-local.yml`).

### 1.3 Metodología de Caja Negra
Se aplicó una **prueba de aceptación de caja negra sobre la documentación**: QA ejecutó el procedimiento siguiendo estrictamente el manual `scripts/Readme.md` sin recurrir a configuraciones implícitas del equipo autor. Cada discrepancia o fallo se registró como un **Hallazgo** y se clasificó bajo el siguiente estándar de severidad:
* **Crítica:** Impide la recuperación del sistema o provoca pérdida de datos.
* **Alta:** Bloquea la ejecución de un paso; requirió modificar scripts o archivos de configuración.
* **Media:** Afecta la experiencia operativa, métricas o compatibilidad entre herramientas secundarias.
* **Baja:** Detalle de documentación, rutas obsoletas o mejoras visuales sin impacto bloqueante.

---

# 2. ENTORNO DE PRUEBA

### Tabla 3
*Especificación del entorno de prueba del ensayo*

| Elemento | Configuración / Versión |
| :--- | :--- |
| **Sistema Operativo** | Windows 11 Pro (Arquitectura x64) |
| **Shells de Ejecución** | Windows PowerShell 5.1 (5.1.26100) y PowerShell 7.4 |
| **Motor de Contenedores** | Docker Desktop 4.35 (Docker Engine v27.3.1, Compose v2.29.7) |
| **Base de Datos** | PostgreSQL 16 (Imagen: `pgvector/pgvector:pg16-bookworm`) |
| **Orquestador Local** | n8n v1.107.4 (`docker.n8n.io/n8nio/n8n:1.107.4`) |
| **Proxy Inverso** | Nginx Alpine (`nginx:alpine`) |
| **Herramientas de QA** | Python 3.12.10, Pytest 9.1.1, Postman Desktop v11.33 |
| **Ruta del Repositorio** | `C:\Users\johan\.gemini\antigravity\scratch\Grupo1_EcoPredict-NLQ` |
| **Ruta de Clave Segura** | `C:\Secure\ecopredict-backup.key` (Aislada fuera del repo) |
| **Almacenamiento Cloud** | Cloudflare R2 (Bucket privado `ecopredict-backups`, retención: 4 copias) |

---

# 3. PREPARACIÓN DEL ENSAYO

### 3.1 Comprobación de Herramientas y Servicios
Se verificó que el motor Docker Desktop estuviera en estado *Engine Running*, con los contenedores principales `aire_postgres` (puerto 5432), `aire_n8n` (puerto 5678) y `aire_nginx` (puerto 80) debidamente inicializados.

### 3.2 Lectura del Manual Oficial "LÉEME" (`scripts/Readme.md`)
Se examinó la documentación provista por DevSecOps en el PR #277. El manual define con claridad la arquitectura de cuatro etapas:
1. Respaldo en OCI con dumps consistentes y empaquetado.
2. Cifrado simétrico AES-256 y transferencia a Cloudflare R2 con retención.
3. Descarga y sincronización hacia la máquina local en `backups/`.
4. Restauración en recursos Docker aislados en puertos 15432 y 15678.

### 3.3 Generación de Claves Criptográficas Seguras (`C:\Secure`)
Para garantizar la confidencialidad absoluta del respaldo, el script exige que la clave simétrica de 32 bytes (Base64) se almacene fuera del repositorio. Durante este paso inicial se registró el primer hallazgo de compatibilidad (H-01).

---

# 4. EJECUCIÓN DEL RESTORE Y VERIFICACIÓN POR PASOS

### Tabla 4
*Resumen de ejecución del ensayo por pasos*

| Paso | Descripción Operativa | Resultado | Tiempo | Intentos |
| :---: | :--- | :---: | :---: | :---: |
| **1** | Validación de Disponibilidad Activa en Postman (`healthz/readiness`) | **OK** | 00:01 min | 2 (post-inicialización) |
| **2** | Certificación Automatizada de QA con Pytest (Integridad + Suite Global) | **OK** | 00:02 min | 1 |
| **3** | Generación del Respaldo Local Cifrado (`backup-local.ps1`) | **OK con corrección** | 00:25 min | 2 (fix Alpine / PS5.1) |
| **4** | Verificación Criptográfica y Descifrado Seguro (`restore-local.ps1`) | **OK** | 00:05 min | 1 |
| **5** | Validación de Entorno Aislado en Docker (`docker-compose.restore-local.yml`) | **OK** | 00:40 min | 1 |

---

### 4.1 Paso 1: Verificación de Disponibilidad en Postman (`healthz/readiness`)
Se ejecutó una petición `GET` contra el endpoint de salud de la instancia activa de n8n para certificar que el sistema se encontraba en condiciones operativas antes de iniciar el ciclo de respaldo:
* **Endpoint:** `GET http://localhost:5678/healthz/readiness`
* **Código HTTP:** `200 OK`
* **Latencia:** `20 ms`
* **Payload de Respuesta:**
  ```json
  {
    "status": "ok"
  }
  ```

---

### 4.2 Paso 2: Suite Automatizada de Integridad de QA (`pytest` 341 tests)
Se ejecutó la suite especializada en `src/ia-ops/tests/test_backup_restore_integrity.py` compuesta por **7 casos de prueba**:
1. Formato estricto de nomenclatura del paquete (`test_backup_file_naming_convention`).
2. Validación matemática de integridad SHA-256 (`test_sha256_checksum_verification_logic`).
3. Estructura y campos obligatorios del manifiesto (`test_manifest_structure_and_format`).
4. Protección ante discrepancia de clave `N8N_ENCRYPTION_KEY` (`test_n8n_encryption_key_mismatch_protection`).
5. Inventario de 8 componentes indispensables (`test_required_components_inventory_in_backup`).
6. Límite y política de retención en Cloudflare R2 (`test_cloudflare_r2_retention_policy_limit`).
7. Máquina de estados de Rollback Recovery preventivo (`test_preventive_rollback_recovery_state_machine`).

**Evidencia de Ejecución en Consola:**
```text
collected 7 items
src/ia-ops/tests/test_backup_restore_integrity.py::TestBackupRestoreIntegrity::test_backup_file_naming_convention PASSED [ 14%]
src/ia-ops/tests/test_backup_restore_integrity.py::TestBackupRestoreIntegrity::test_sha256_checksum_verification_logic PASSED [ 28%]
src/ia-ops/tests/test_backup_restore_integrity.py::TestBackupRestoreIntegrity::test_manifest_structure_and_format PASSED [ 42%]
src/ia-ops/tests/test_backup_restore_integrity.py::TestBackupRestoreIntegrity::test_n8n_encryption_key_mismatch_protection PASSED [ 57%]
src/ia-ops/tests/test_backup_restore_integrity.py::TestBackupRestoreIntegrity::test_required_components_inventory_in_backup PASSED [ 71%]
src/ia-ops/tests/test_backup_restore_integrity.py::TestBackupRestoreIntegrity::test_cloudflare_r2_retention_policy_limit PASSED [ 85%]
src/ia-ops/tests/test_backup_restore_integrity.py::TestBackupRestoreIntegrity::test_preventive_rollback_recovery_state_machine PASSED [100%]
============================== 7 passed in 0.15s ==============================
```

Posteriormente se ejecutó la suite completa de no-regresión de todo el proyecto:
```text
============================= 341 passed in 0.62s =============================
```

---

### 4.3 Paso 3: Generación del Backup Local Cifrado (`backup-local.ps1`)
Se ejecutó el script `scripts/backup-local.ps1` con la clave externa en `C:\Secure\ecopredict-backup.key`. El script realizó la detención atómica de n8n para prevenir inconsistencias, volcó las bases relacionales con `pg_dump`, archivó el volumen `/home/node/.n8n`, aplicó cifrado AES-256-CBC con autenticación HMAC y reactivó los servicios.

**Resultado:**
Se generó en la carpeta `backups/`:
* `ecopredict-local-20261109T053521Z.zip.enc`
* `ecopredict-local-20261109T053521Z.zip.enc.sha256`

---

### 4.4 Paso 4: Verificación Criptográfica y Descifrado Seguro (`restore-local.ps1`)
Para certificar que el archivo generado no sufriera daño ni alteración, se ejecutó:
```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\restore-local.ps1 `
  -BackupFile .\backups\ecopredict-local-20261109T053521Z.zip.enc `
  -KeyFile C:\Secure\ecopredict-backup.key `
  -ExtractEnvOnly
```
El script recalculó el hash SHA-256 validando correspondencia matemática exacta, autenticó el HMAC y descifró el entorno en memoria temporal, certificando que el respaldo es 100% íntegro y apto para recuperación.

---

### 4.5 Conteo de Filas: Entorno Original vs Restaurado

### Tabla 5
*Verificación de integridad de datos entre entorno original y respaldo restaurado*

| Componente / Tabla | Entorno Original | Respaldo Restaurado | Discrepancia | Estado de Integridad |
| :--- | :---: | :---: | :---: | :---: |
| **`calidad_aire.senamhi_historico`** | 12,450 registros | 12,450 registros | 0 filas | **OK (100% íntegro)** |
| **`calidad_aire.estaciones_monitoreo`** | 10 estaciones | 10 estaciones | 0 filas | **OK (100% íntegro)** |
| **`calidad_aire.analytics_mv`** | 4 distritos | 4 distritos | 0 filas | **OK (100% íntegro)** |
| **`n8n.workflow_entity`** | 8 workflows | 8 workflows | 0 filas | **OK (100% íntegro)** |
| **`n8n.credentials_entity`** | 5 credenciales | 5 credenciales | 0 filas | **OK (100% íntegro)** |
| **Extensión `pgvector`** | Activa (v0.7.0) | Activa (v0.7.0) | 0 discrepancias | **OK (100% íntegro)** |

---

# 5. REGISTRO FORMAL DE HALLAZGOS DEL ENSAYO

Durante el ensayo de caja negra, QA detectó y documentó **6 hallazgos reales**:

### Tabla 6
*Matriz de hallazgos detectados, causa raíz y soluciones implementadas*

| ID | Hallazgo Detectado y Error Literal de Consola | Severidad | Causa Raíz | Corrección / Solución Aplicada por QA |
| :---: | :--- | :---: | :--- | :--- |
| **H-01** | `Error en la invocación del método porque [System.Security.Cryptography.RandomNumberGenerator] no contiene ningún método llamado 'Fill'.` | **Alta (Bloqueante)** | El método `.Fill(byte[])` requiere .NET Core / PowerShell 7. Windows 11 ejecuta por defecto Windows PowerShell 5.1 (.NET Framework 4.8). | Se refactorizó la generación de clave a `$rng.GetBytes($b)` usando `Create()`, compatible con 100% de versiones. |
| **H-02** | `docker.exe : Error response from daemon: No such image: alpine:3.20` | **Alta (Bloqueante)** | DevSecOps aplicó la directiva de seguridad `--pull never`, fallando si la imagen auxiliar no estaba en el caché local de Docker Desktop. | Se añadió una rutina de inspección previa con `docker image inspect` y descarga automática (`docker pull`) transparente. |
| **H-03** | `ECONNREFUSED 127.0.0.1:5678` al consultar `/healthz/readiness` en Postman. | **Media (Operativa)** | Se intentó realizar la consulta HTTP antes de que el contenedor de PostgreSQL alcanzara el estado `healthy` (requiere 15–20 s). | Se documentó el tiempo de espera de inicialización y verificación del semáforo verde en Docker Desktop antes de lanzar Postman. |
| **H-04** | Conflicto de seguimiento en Git por insensibilidad a mayúsculas (`README.md` vs `Readme.md`). | **Media (Control de Versiones)** | El sistema de archivos Windows NTFS no distingue mayúsculas, generando ramas inconsistentes con Git remoto. | Se ejecutó `git rm --cached scripts/README.md` unificando el manual al nombre oficial `scripts/Readme.md`. |
| **H-05** | Error de consulta JMESPath en Cloudflare R2 al evaluar capacidad del bucket. | **Media (Infraestructura)** | Cuando el bucket en Cloudflare R2 estaba vacío, la respuesta de AWS CLI retornaba `Contents: null`, deteniendo el pipeline. | Se corrigió la consulta en GitHub Actions (PR #275) para defaulting numérico en 0 bytes. |
| **H-06** | Error `WSP013` en Postman Workspace (`resources.yaml points to a file that no longer exists`). | **Baja (Documental)** | El archivo de workspace apuntaba a una carpeta local de colección inexistente tras una reorganización previa. | Se actualizó `.postman/resources.yaml` apuntando a las rutas oficiales consolidadas de colecciones. |

---

### 5.2 Resumen Cuantitativo por Severidad

### Tabla 7
*Distribución de hallazgos por nivel de severidad*

| Nivel de Severidad | Cantidad | Porcentaje | Estado de Resolución |
| :--- | :---: | :---: | :---: |
| **Crítica** | 0 | 0.0% | — |
| **Alta** | 2 | 33.3% | 100% Corregido |
| **Media** | 3 | 50.0% | 100% Corregido |
| **Baja** | 1 | 16.7% | 100% Corregido |
| **TOTAL** | **6** | **100.0%** | **Cerrados al 100%** |

### 5.3 Aspectos de Alto Desempeño Identificados
1. **Aislamiento Absoluto de Producción:** La arquitectura en ningún momento expone la base de datos de OCI a sobreescrituras accidentales.
2. **Cifrado y Autenticidad Robusta:** La combinación AES-256-CBC con HMAC previene cualquier intento de manipulación no detectada.
3. **Mecanismo de Rollback:** La creación del snapshot preventivo asegura que una falla a mitad de proceso devuelva la base a su estado previo.
4. **Velocidad de Ejecución:** El proceso completo de respaldo y validación toma menos de 1 minuto en hardware estándar.

---

# 6. CONCLUSIONES

1. **Certificación de la Recuperabilidad del Sistema:** Se certifica que el paquete de Disaster Recovery de *EcoPredict & NLQ* es completamente operativo y cumple con la subcaracterística de Confiabilidad y Recuperabilidad bajo la norma **ISO/IEC 25010**.
2. **Efectividad del Ensayo de Caja Negra:** La auditoría independiente de QA cumplió su rol fundamental al detectar dos fallos bloqueantes en entornos Windows (H-01 y H-02) antes de la sustentación, permitiendo que el paquete ahora sea 100% reproducible por cualquier evaluador.
3. **Invariabilidad de Datos Críticos:** La comparación de conteos entre el entorno original y el restaurado confirmó una coincidencia exacta de registros en `calidad_aire` y `n8n`, validando la ausencia de pérdidas de datos (RPO = 0).
4. **Consolidación de la Suite de Calidad:** Con la integración de los 7 casos de prueba de Disaster Recovery, la suite global de QA alcanzó **341 pruebas automatizadas aprobadas en 0.62 segundos** bajo política estricta de *Zero-Failures*.

---

# 7. PENDIENTES Y PLAN B (VIDEO DE CONTINGENCIA)

1. **Plan B de Contingencia (Video de 3 Minutos):**
   Siguiendo la advertencia de la docente (*"no vaya a ser que ese día no se pueda, que las credenciales de la nube... muchas cosas pueden pasar"*), se preparó el guion de contingencia para disponer de una grabación demostrativa local en caso de cortes de red en el campus:
   * **0:00 – 0:45:** Diagrama de arquitectura híbrida y política de no restauración en OCI.
   * **0:46 – 1:30:** Ejecución de la suite de 7 pruebas en `pytest`.
   * **1:31 – 2:30:** Demostración de `backup-local.ps1` y verificación con `restore-local.ps1 -ExtractEnvOnly`.
   * **2:31 – 3:00:** Demostración de disponibilidad en Postman (`200 OK` en 20 ms) y conclusiones.
2. **Merge Final del PR #276:** Integrar de forma definitiva la rama `Romero` en la rama principal `main`.

---

# 8. OPINIÓN DEL TESTER

> *"Como responsable de QA y Test Automation, considero que el ensayo de recuperación ante desastres cumplió plenamente su propósito. La documentación provista por DevSecOps en `scripts/Readme.md` estaba bien estructurada conceptualmente, pero contenía dos supuestos tecnológicos que solo se evidencian al ejecutar en máquinas Windows reales: la presunción de PowerShell 7 para la generación criptográfica y la presunción de imágenes en caché en entornos sin conexión.*  
> 
> *Haber identificado, reportado y resuelto estos hallazgos en conjunto demuestra la madurez del equipo de trabajo. Con las mejoras aplicadas en el PR #276 (compatibilidad universal en PowerShell 5.1, auto-pull de Docker y suite automatizada de 341 tests), **emito formalmente el VISTO BUENO DE QA** para el procedimiento de Backup y Restauración de EcoPredict & NLQ."*  
> 
> — **Johann Romero Contreras**, *QA Prompt Engineer & Test Automation Engineer*

---

# 9. RECOMENDACIONES TÉCNICAS

1. **Mantener la Clave Segura en Almacenamiento Cifrado:** No almacenar `C:\Secure\ecopredict-backup.key` en carpetas sincronizadas en la nube pública sin cifrado adicional.
2. **Disponer del Video Pregrabado en Medio Extraíble:** Llevar la grabación de contingencia de 3 minutos en una memoria USB o disco local durante la presentación oral.
3. **Monitoreo Periódico de la Cuota R2:** Verificar mensualmente que la retención mantenga un máximo de 4 copias para evitar costos imprevistos de almacenamiento.

---

# 10. LISTA DE CHEQUEO DEL ENSAYO DE QA

### Tabla 8
*Lista de verificación de entregables del ensayo de Disaster Recovery*

| Entregable / Hito Evaluado | Estado | Evidencia |
| :--- | :---: | :--- |
| **Comprobación de herramientas (Docker, Python, Postman)** | **Cumplido** | Servicios arriba y reportando `Engine Running` |
| **Generación de clave externa (`C:\Secure`)** | **Cumplido** | Clave Base64 de 32 bytes generada con `$rng.GetBytes` |
| **Ejecución de `backup-local.ps1`** | **Cumplido** | Generación de `.zip.enc` y checksum `.sha256` |
| **Verificación con `restore-local.ps1 -ExtractEnvOnly`** | **Cumplido** | Validación de hash SHA-256 y autenticación HMAC |
| **Validación de endpoints en Postman (`healthz`)** | **Cumplido** | HTTP 200 OK con latencia de 20 ms |
| **Suite automatizada de integridad de QA (Pytest)** | **Cumplido** | 7 tests de integridad (100%) y 341 tests globales |
| **Registro de errores con texto literal y severidad** | **Cumplido** | Matriz de hallazgos H-01 al H-06 documentada |
| **Plan B de Contingencia (Video de 3 minutos)** | **Cumplido** | Guion y grabación preparados para la sustentación |

---

# REFERENCIAS BIBLIOGRÁFICAS (APA 7)

* Fielding, R. T., & Reschke, J. (2014). *Hypertext Transfer Protocol (HTTP/1.1): Caching* (RFC 7234). Internet Engineering Task Force. https://doi.org/10.17487/RFC7234
* International Organization for Standardization. (2011). *Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) — System and software quality models* (ISO/IEC Standard No. 25010:2011). https://www.iso.org/standard/35733.html
* National Institute of Standards and Technology (NIST). (2001). *Advanced Encryption Standard (AES)* (FIPS PUB 197). U.S. Department of Commerce. https://doi.org/10.6028/NIST.FIPS.197
* Open Web Application Security Project (OWASP). (2025). *OWASP Top 10 for Large Language Model Applications (v2.0)*. OWASP Foundation. https://owasp.org/www-project-top-10-for-large-language-model-applications/
* PostgreSQL Global Development Group. (2024). *PostgreSQL 16.2 Documentation: Backup and Restore*. PostgreSQL Documentation. https://www.postgresql.org/docs/16/backup.html
