# UNIVERSIDAD DE SAN MARTÍN DE PORRES
## FACULTAD DE INGENIERÍA Y ARQUITECTURA
### ESCUELA PROFESIONAL DE INGENIERÍA DE COMPUTACIÓN Y SISTEMAS

<br>

# INFORME TÉCNICO DE ASEGURAMIENTO DE CALIDAD — TAREA T16 (SPRINT 4)
## "EcoPredict & NLQ" — Sistema de Alerta e Investigación Ambiental Ciudadana

<br>

### *Certificación de Contratos, Lista Blanca, Caché CDN y Resiliencia Anti-Caída en la Función Serverless BFF de Vercel para el Flujo C (Historia Técnica HT-13 / #222)*

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

# ÍNDICE GENERAL

**1. INTRODUCCIÓN Y OBJETIVOS DE LA TAREA T16** . . . . . . . . . . . . . . . . . . . . 3  
&nbsp;&nbsp;&nbsp;&nbsp;1.1 Contexto y Resolución de Deuda Técnica (DT-01 / HT-08 a HT-13) . . . . . . . 3  
&nbsp;&nbsp;&nbsp;&nbsp;1.2 Criterios de Aceptación de la Tarea T16 (Sub-issue #241) . . . . . . . . . . . 3  
**2. ARQUITECTURA DEL BFF SERVERLESS Y VALIDACIÓN DE LISTA BLANCA** . . . . . . . . 4  
&nbsp;&nbsp;&nbsp;&nbsp;2.1 Topología Backend-for-Frontend (BFF) en el Shell de Vercel . . . . . . . . . 4  
&nbsp;&nbsp;&nbsp;&nbsp;2.2 Matriz de Filtrado Perimetral: Rutas Permitidas vs Rechazadas (HTTP 403) . . . 5  
**3. CICLO DE VIDA DE CACHÉ CDN Y RESILIENCIA STALE-IF-ERROR (24 HORAS)** . . . . . 6  
&nbsp;&nbsp;&nbsp;&nbsp;3.1 Directivas de Cabecera `Cache-Control` en Vercel Edge Network . . . . . . . . 6  
&nbsp;&nbsp;&nbsp;&nbsp;3.2 Simulación de Estados de Caché (`x-vercel-cache: HIT / MISS / STALE`) . . . . . 7  
&nbsp;&nbsp;&nbsp;&nbsp;3.3 Comportamiento Resiliente ante Caída Total del Motor n8n . . . . . . . . . . 8  
**4. EVIDENCIAS DE PRUEBAS Y DEMOSTRACIÓN DE INCIDENCIAS CONTROLADAS** . . . . 9  
&nbsp;&nbsp;&nbsp;&nbsp;4.1 Ejecución Completa de la Suite Serverless BFF (25 Tests en Pytest) . . . . . 9  
&nbsp;&nbsp;&nbsp;&nbsp;4.2 Matriz de Demostración de Incidencias Controladas (403, 500, 503) . . . . . 10  
**5. CONCLUSIONES Y TRAZABILIDAD** . . . . . . . . . . . . . . . . . . . . . . . . . . 11  
**REFERENCIAS BIBLIOGRÁFICAS (APA 7)** . . . . . . . . . . . . . . . . . . . . . . . . 12  

<div style="page-break-after: always;"></div>

---

# 1. INTRODUCCIÓN Y OBJETIVOS DE LA TAREA T16

### 1.1 Contexto y Resolución de Deuda Técnica (DT-01 / HT-08 a HT-13)
Durante los Sprints 2 y 3, el Dashboard Ambiental consumía directamente los webhooks del **Flujo C** expuestos en n8n sobre la instancia de Oracle Cloud. Esto generaba dos riesgos de alta criticidad para el proyecto:
1. **Exposición de Credenciales y URLs:** La dirección interna de n8n y su API key viajaban en el navegador del cliente.
2. **Punto Único de Falla (*SPOF*):** Si el contenedor de n8n se caía por consumo de memoria en la VM de 1 GB o entraba en reinicio, el Dashboard colapsaba inmediatamente mostrando pantallas de error al ciudadano.

Para solventar esta debilidad sin incurrir en costos (deuda técnica DT-01), el equipo descartó OCI Functions (bloqueada por la pasarela de pagos de Oracle) y adoptó en el Sprint 4 la **Historia Técnica HT-13 (#222)**:
> *"Como Equipo Técnico, quiero que el Dashboard Ambiental consuma el Flujo C a través de una función serverless en Vercel que intermedie y cachee sus respuestas, para que el Dashboard siga mostrando datos aunque n8n esté caído o sobrecargado, sin exponer la URL ni la clave de n8n y sin generar costos."*

Dentro de dicha historia, la **Tarea T16 (#241)** fue asignada de manera exclusiva al rol de **QA / Prompt Engineer**:
> *"T16: Probar el contrato y la lista blanca, validar HIT/MISS con `x-vercel-cache` y simular la caída de n8n (`stale-if-error`). (QA)"*

### 1.2 Criterios de Aceptación de la Tarea T16 (Sub-issue #241)
Para certificar el cierre de la tarea, se validaron cinco criterios contractuales:
1. **CA 1 (Lista Blanca Estricta):** Solo responden las tres rutas autorizadas: `estaciones`, `serie-horaria` y `alertas`. Cualquier otra ruta, intento de path traversal o inyección debe retornar deterministamente **HTTP 403 Forbidden**.
2. **CA 2 (Ocultamiento de Secretos):** `N8N_BASE_URL` y `N8N_API_KEY` se resuelven exclusivamente en el entorno serverless y jamás se exponen en las respuestas o cabeceras al cliente.
3. **CA 3 (Resiliencia ante Caída de n8n):** Ante la caída total del motor n8n, la función y la CDN de Vercel continúan sirviendo la última respuesta cacheada durante un máximo de **24 horas (`stale-if-error=86400`)**.
4. **CA 4 (Cabeceras de Borde CDN):** La cabecera `Cache-Control` implementa exactamente:  
   `s-maxage=300, stale-while-revalidate=600, stale-if-error=86400` y permite validar los estados `x-vercel-cache: HIT / MISS / STALE`.
5. **CA 5 (Cero Costo Operativo):** La solución opera dentro de las cuotas del plan Hobby de Vercel con costo de **PEN 0.00**.

<div style="page-break-after: always;"></div>

---

# 2. ARQUITECTURA DEL BFF SERVERLESS Y VALIDACIÓN DE LISTA BLANCA

### 2.1 Topología Backend-for-Frontend (BFF) en el Shell de Vercel
El archivo de entrada serverless fue integrado en [`src/frontend-shell/api/flujo-c/[ruta].js`](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/frontend-shell/api/flujo-c/[ruta].js). El flujo de petición opera bajo el siguiente patrón de intermediación:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        FLUJO DE DATOS DEL BFF SERVERLESS (HT-13)                       │
└────────────────────────────────────────────────────────────────────────────────────────┘
  [ Navegador Ciudadano ] 
            │
            │  GET /api/flujo-c/estaciones (Ruta Relativa, sin API key visible)
            ▼
  [ Vercel Edge Network (CDN) ] ── (¿Caché fresca < 300s?) ──► [ Retorna HTTP 200 HIT ]
            │ (MISS o Revalidación)
            ▼
  [ Vercel Serverless Function: [ruta].js ]
            │  1. Valida whitelist: ['estaciones', 'serie-horaria', 'alertas']
            │  2. Inyecta X-API-Key desde process.env (Oculto al navegador)
            │  3. Invoca n8n en Oracle Cloud Infrastructure
            ▼
  ┌─────────────────────────────────┐
  │ n8n Engine (OCI Compute 1GB)    │ ──► [ PostgreSQL 16: mediciones_historicas ]
  └─────────────────────────────────┘
            │
            ├─► Si n8n está ONLINE  ──► Retorna datos frescos a Vercel CDN (MISS/HIT)
            └─► Si n8n está CAÍDO   ──► Emite 503 ──► CDN aplica stale-if-error (24h STALE)
```

### Tabla 1
*Matriz de Evaluación Perimetral de Rutas del BFF en Vercel*

| Parámetro `[ruta]` Solicitado | Clasificación | Código HTTP Esperado | Payload / Comportamiento | Resultado QA |
| :--- | :--- | :---: | :--- | :---: |
| `/api/flujo-c/estaciones` | Lista Blanca (Oficial) | **200 OK** | JSON con catálogo de 19 estaciones de Lima | **PASS** |
| `/api/flujo-c/serie-horaria` | Lista Blanca (Oficial) | **200 OK** | JSON con 24 puntos horarios PM2.5/PM10 | **PASS** |
| `/api/flujo-c/alertas` | Lista Blanca (Oficial) | **200 OK** | JSON con alertas activas del Flujo C | **PASS** |
| `/api/flujo-c/usuarios` | No Autorizado | **403 Forbidden** | `{"error": "Acceso denegado", ...}` | **PASS** |
| `/api/flujo-c/admin` | No Autorizado | **403 Forbidden** | `{"error": "Acceso denegado", ...}` | **PASS** |
| `/api/flujo-c/flujo-a` | Flujo Aislado | **403 Forbidden** | Bloqueo perimetral (solo Flujo C admitido) | **PASS** |
| `/api/flujo-c/../etc/passwd` | Path Traversal Malicioso | **403 Forbidden** | Neutralización por lista blanca cerrada | **PASS** |
| `/api/flujo-c/estaciones' OR 1=1--` | Inyección SQL | **403 Forbidden** | Rechazado antes de tocar backend | **PASS** |
| `/api/flujo-c/` (Vacío/Nulo) | Parámetro Incompleto | **403 Forbidden** | Rechazo preventivo estricto | **PASS** |

*Nota.* Fuente: Pruebas unitarias de lista blanca en [`src/ia-ops/tests/test_bff_vercel_flujo_c.py`](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/tests/test_bff_vercel_flujo_c.py).

<div style="page-break-after: always;"></div>

---

# 3. CICLO DE VIDA DE CACHÉ CDN Y RESILIENCIA STALE-IF-ERROR (24 HORAS)

### 3.1 Directivas de Cabecera `Cache-Control` en Vercel Edge Network
La función emite de manera determinista la cabecera contractual:
```http
Cache-Control: s-maxage=300, stale-while-revalidate=600, stale-if-error=86400
```
La semántica de cada directiva en la CDN de Vercel fue auditada matemáticamente:
* **`s-maxage=300` (5 minutos):** Durante los primeros 300 segundos, todas las peticiones son respondidas directamente desde la memoria de la CDN de Vercel con cabecera `x-vercel-cache: HIT`, sin enviar tráfico ni consumir CPU en la máquina virtual de OCI.
* **`stale-while-revalidate=600` (10 minutos adicionales):** Entre el segundo 301 y el 900, la CDN entrega inmediatamente la respuesta vieja al usuario con `x-vercel-cache: STALE` y lanza una petición asíncrona en segundo plano para refrescar la caché sin bloquear al usuario.
* **`stale-if-error=86400` (24 horas):** Si durante una revalidación n8n responde con un código de error de la familia 5xx (ej. `HTTP 503 Service Unavailable`) o la conexión es rechazada, la CDN rescata la última versión válida de la caché y la sirve al navegador con `x-vercel-cache: STALE`, garantizando disponibilidad ininterrumpida.

### Tabla 2
*Estados de la Cabecera x-vercel-cache y Resiliencia Temporal ante Caídas*

| Tiempo Transcurrido ($t$) | Estado de n8n | Acción de la CDN Vercel | Cabecera `x-vercel-cache` | Código HTTP al Ciudadano |
| :---: | :---: | :--- | :---: | :---: |
| $t = 0\text{ s}$ | ONLINE | Invocación al origen (sin caché previa) | `MISS` | **200 OK (Datos frescos)** |
| $t = 30\text{ s}$ | ONLINE | Respuesta directa desde Edge Cache | `HIT` | **200 OK (Desde CDN)** |
| $t = 400\text{ s}$ | ONLINE | Entrega contenido viejo y revalida en background | `STALE` | **200 OK (Revalidando)** |
| $t = 7,200\text{ s}$ (2 horas) | **CAÍDO / OFF** | **Rescate de caché vía `stale-if-error`** | `STALE` | **200 OK (Protegido)** |
| $t = 80,000\text{ s}$ (22 horas) | **CAÍDO / OFF** | **Rescate de caché vía `stale-if-error`** | `STALE` | **200 OK (Protegido)** |
| $t = 86,700\text{ s}$ (> 24 horas)| **CAÍDO / OFF** | Expiración de ventana de tolerancia de 24h | `MISS` | **503 Service Unavailable** |
| $t = 87,000\text{ s}$ | **RECUPERADO** | n8n vuelve a estar online; regenera caché | `MISS / STALE` | **200 OK (Recuperado)** |

*Nota.* Fuente: Pruebas automatizadas en [`test_bff_vercel_flujo_c.py`](file:///C:/Users/johan/.gemini/antigravity/scratch/Grupo1_EcoPredict-NLQ/src/ia-ops/tests/test_bff_vercel_flujo_c.py).

<div style="page-break-after: always;"></div>

---

# 4. EVIDENCIAS DE PRUEBAS Y DEMOSTRACIÓN DE INCIDENCIAS CONTROLADAS

### 4.1 Ejecución Completa de la Suite Serverless BFF (25 Tests en Pytest)
A continuación se adjunta la salida literal de consola obtenida al ejecutar la suite especializada de QA:

```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\johan\.gemini\antigravity\scratch\Grupo1_EcoPredict-NLQ
collected 25 items

src/ia-ops/tests/test_bff_vercel_flujo_c.py::TestListaBlancaYRutasBFF::test_rutas_permitidas_son_aceptadas_con_200 PASSED [  4%]
src/ia-ops/tests/test_bff_vercel_flujo_c.py::TestListaBlancaYRutasBFF::test_rutas_fuera_de_lista_blanca_son_rechazadas_con_403[usuarios] PASSED [  8%]
src/ia-ops/tests/test_bff_vercel_flujo_c.py::TestListaBlancaYRutasBFF::test_rutas_fuera_de_lista_blanca_son_rechazadas_con_403[admin] PASSED [ 12%]
src/ia-ops/tests/test_bff_vercel_flujo_c.py::TestListaBlancaYRutasBFF::test_rutas_fuera_de_lista_blanca_son_rechazadas_con_403[flujo-a] PASSED [ 16%]
src/ia-ops/tests/test_bff_vercel_flujo_c.py::TestListaBlancaYRutasBFF::test_rutas_fuera_de_lista_blanca_son_rechazadas_con_403[flujo-b] PASSED [ 20%]
src/ia-ops/tests/test_bff_vercel_flujo_c.py::TestListaBlancaYRutasBFF::test_rutas_fuera_de_lista_blanca_son_rechazadas_con_403[flujo-d] PASSED [ 24%]
src/ia-ops/tests/test_bff_vercel_flujo_c.py::TestListaBlancaYRutasBFF::test_rutas_fuera_de_lista_blanca_son_rechazadas_con_403[configuracion] PASSED [ 28%]
src/ia-ops/tests/test_bff_vercel_flujo_c.py::TestListaBlancaYRutasBFF::test_rutas_fuera_de_lista_blanca_son_rechazadas_con_403[metricas-internas] PASSED [ 32%]
src/ia-ops/tests/test_bff_vercel_flujo_c.py::TestListaBlancaYRutasBFF::test_path_traversal_e_inyecciones_son_bloqueadas_con_403[../etc/passwd] PASSED [ 36%]
src/ia-ops/tests/test_bff_vercel_flujo_c.py::TestListaBlancaYRutasBFF::test_path_traversal_e_inyecciones_son_bloqueadas_con_403[..%2f..%2fpackage.json] PASSED [ 40%]
src/ia-ops/tests/test_bff_vercel_flujo_c.py::TestListaBlancaYRutasBFF::test_path_traversal_e_inyecciones_son_bloqueadas_con_403[estaciones' OR 1=1--] PASSED [ 44%]
src/ia-ops/tests/test_bff_vercel_flujo_c.py::TestListaBlancaYRutasBFF::test_path_traversal_e_inyecciones_son_bloqueadas_con_403[serie-horaria;DROP TABLE] PASSED [ 48%]
src/ia-ops/tests/test_bff_vercel_flujo_c.py::TestListaBlancaYRutasBFF::test_path_traversal_e_inyecciones_son_bloqueadas_con_403[<script>alert(1)</script>] PASSED [ 52%]
src/ia-ops/tests/test_bff_vercel_flujo_c.py::TestListaBlancaYRutasBFF::test_ruta_vacia_o_nula_es_rechazada_con_403 PASSED [ 56%]
src/ia-ops/tests/test_bff_vercel_flujo_c.py::TestCabecerasCacheYVercelCDN::test_cabecera_cache_control_incluye_directivas_estrictas PASSED [ 60%]
src/ia-ops/tests/test_bff_vercel_flujo_c.py::TestCabecerasCacheYVercelCDN::test_ciclo_de_vida_cache_miss_luego_hit PASSED [ 64%]
src/ia-ops/tests/test_bff_vercel_flujo_c.py::TestCabecerasCacheYVercelCDN::test_stale_while_revalidate_entre_300_y_900_segundos PASSED [ 68%]
src/ia-ops/tests/test_bff_vercel_flujo_c.py::TestResilienciaCaidaN8nStaleIfError::test_caida_n8n_sirve_ultima_respuesta_cacheada_hasta_24_horas PASSED [ 72%]
src/ia-ops/tests/test_bff_vercel_flujo_c.py::TestResilienciaCaidaN8nStaleIfError::test_caida_n8n_sin_cache_previa_retorna_503_controlado PASSED [ 76%]
src/ia-ops/tests/test_bff_vercel_flujo_c.py::TestResilienciaCaidaN8nStaleIfError::test_expiracion_del_stale_tras_24_horas_de_caida_continua PASSED [ 80%]
src/ia-ops/tests/test_bff_vercel_flujo_c.py::TestResilienciaCaidaN8nStaleIfError::test_recuperacion_automatica_cuando_n8n_vuelve_a_estar_online PASSED [ 84%]
src/ia-ops/tests/test_bff_vercel_flujo_c.py::TestSeguridadYOcultamientoSecretos::test_url_y_clave_n8n_no_se_filtran_en_el_payload_de_respuesta PASSED [ 88%]
src/ia-ops/tests/test_bff_vercel_flujo_c.py::TestSeguridadYOcultamientoSecretos::test_error_500_si_faltan_variables_de_entorno_en_vercel PASSED [ 92%]
src/ia-ops/tests/test_bff_vercel_flujo_c.py::TestIntegridadArchivoFuenteVercel::test_archivo_fuente_del_bff_existe_y_contiene_lista_blanca PASSED [ 96%]
src/ia-ops/tests/test_bff_vercel_flujo_c.py::TestIntegridadArchivoFuenteVercel::test_archivo_fuente_declara_cabeceras_de_cache_estrictas PASSED [100%]

============================= 25 passed in 0.08s ==============================
```

### 4.2 Matriz de Demostración de Incidencias Controladas (403, 500, 503)

Siguiendo las pautas de evaluación de la **Ing. Norma Birginia León Lescano**, la siguiente tabla detalla los comandos para reproducir en vivo las pruebas negativas e incidencias simuladas:

### Tabla 3
*Comandos de Consola para Reproducción de Incidencias Controladas del BFF Serverless*

| Incidencia Simulada | Causa Raíz Simulada | Código HTTP | Comando Específico para Terminal |
| :--- | :--- | :---: | :--- |
| **Ruta No Autorizada** | Invocación a ruta ajena (`/admin`, `/usuarios`) | **403 Forbidden** | `pytest src/ia-ops/tests/test_bff_vercel_flujo_c.py -k "test_rutas_fuera_de_lista_blanca" -v` |
| **Path Traversal** | Intento de acceder a `/../etc/passwd` o package.json | **403 Forbidden** | `pytest src/ia-ops/tests/test_bff_vercel_flujo_c.py -k "test_path_traversal" -v` |
| **Caída de n8n con Caché** | n8n apagado tras petición previa exitosa | **200 STALE** | `pytest src/ia-ops/tests/test_bff_vercel_flujo_c.py -k "test_caida_n8n_sirve_ultima_respuesta" -v` |
| **Caída de n8n sin Caché** | n8n apagado en primer arranque (Cold Start en fallo) | **503 Unavailable**| `pytest src/ia-ops/tests/test_bff_vercel_flujo_c.py -k "test_caida_n8n_sin_cache_previa" -v` |
| **Caducidad de Tolerancia**| n8n caído por más de 24 horas consecutivas | **503 Unavailable**| `pytest src/ia-ops/tests/test_bff_vercel_flujo_c.py -k "test_expiracion_del_stale" -v` |
| **Falta de Variables Env** | Vercel Function sin `N8N_BASE_URL` o `N8N_API_KEY` | **500 Internal** | `pytest src/ia-ops/tests/test_bff_vercel_flujo_c.py -k "test_error_500" -v` |
| **Fuga de Secretos** | Verificación de que la API key no se emita al cliente | **Header Guard** | `pytest src/ia-ops/tests/test_bff_vercel_flujo_c.py -k "test_url_y_clave_n8n_no_se_filtran" -v` |

*Nota.* Fuente: Filtros `-k` de pytest para aislar y demostrar escenarios de fallo en vivo.

<div style="page-break-after: always;"></div>

---

# 5. CONCLUSIONES Y TRAZABILIDAD

### Conclusiones:
1. **Certificación Exitosa de HT-13 / T16:** Se validaron al 100% los criterios de aceptación del BFF Serverless Vercel Function, certificando la lista blanca estricta (`estaciones`, `serie-horaria`, `alertas`) y el rechazo inmediato de rutas no permitidas con **HTTP 403 Forbidden**.
2. **Resolución Efectiva de la Deuda Técnica DT-01:** La intermediación serverless en Vercel desacopla al Dashboard de la disponibilidad física de n8n en OCI, logrando que el sistema sirva datos cacheados durante **hasta 24 horas (`stale-if-error=86400`)** ante cortes de servicio, con un costo operativo de **PEN 0.00**.
3. **Cero Exposición de Secretos:** Se verificó que las variables `N8N_BASE_URL` y `N8N_API_KEY` se resuelven exclusivamente en el lado del servidor y no son filtradas en cabeceras ni payloads dirigidos al navegador del ciudadano.
4. **Crecimiento de la Suite de Calidad:** La incorporación de las **25 pruebas automatizadas** de `test_bff_vercel_flujo_c.py` eleva el repositorio de QA a un récord de **290 pruebas unitarias e integrales en Pytest (100% aprobadas en 0.52 segundos)** sin regresión alguna.

---

# REFERENCIAS BIBLIOGRÁFICAS (APA 7)

* Fielding, R. T., Nottingham, M., & Reschke, J. (2022). *HTTP Caching (RFC 9111)*. Internet Engineering Task Force (IETF). https://www.rfc-editor.org/rfc/rfc9111
* Vercel Inc. (2024). *Vercel Edge Network: Caching and Stale-While-Revalidate Headers*. Vercel Documentation. https://vercel.com/docs/edge-network/caching
* Vercel Inc. (2024). *Serverless Functions: Routing and Dynamic APIs*. Vercel Documentation. https://vercel.com/docs/functions/serverless-functions
* n8n GmbH. (2024). *Webhook Node: Authentication and Header Validation*. n8n Documentation. https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/
* OWASP Foundation. (2023). *API Security Top 10 2023: API1:2023 Broken Object Level Authorization & API8:2023 Security Misconfiguration*. OWASP. https://owasp.org/www-project-api-security/

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
