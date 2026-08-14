# 📬 Pruebas de API con Postman — EcoPredict-NLQ

**Proyecto:** EcoPredict-NLQ — Sistema de Alerta e Investigación Ambiental Ciudadana  
**Fecha:** 2026-08-14  
**Autor:** Equipo QA — Grupo 1  
**Rol responsable:** QA Prompt Engineer  

---

## 1. Descripción General

Esta carpeta contiene los archivos de **colección y entorno de Postman** utilizados para las pruebas automatizadas de la API NLQ de EcoPredict. Las pruebas verifican el comportamiento funcional del endpoint de consultas en lenguaje natural, la seguridad contra inyección de prompts y la validación del formato de respuestas.

### Archivos incluidos

| Archivo | Descripción |
|---------|-------------|
| `eco_predict_nlq_collection.json` | Colección Postman v2.1 con todas las pruebas de API organizadas en carpetas. |
| `eco_predict_nlq_environment.json` | Variables de entorno para configurar la URL base, clave API y parámetros. |
| `README.md` | Este documento de documentación. |

### Workspace de Postman

El equipo mantiene un workspace colaborativo en Postman:

🔗 **[EcoPredict-NLQ QA Workspace](https://gslan99-419711.postman.co/workspace/6a886e46-0703-4dba-a30f-cdb6f4d72921)**

---

## 2. Estructura de la Colección

La colección **"EcoPredict NLQ - QA Tests"** está organizada en las siguientes carpetas:

```
📁 EcoPredict NLQ - QA Tests
├── 📂 Consultas NLQ
│   ├── POST Consulta de calidad del aire
│   ├── POST Consulta de contaminación del agua
│   └── POST Consulta de anomalías de temperatura
├── 📂 Seguridad — Inyección de Prompts
│   ├── POST Inyección SQL en consulta NLQ
│   └── POST Intento de sobrescritura de prompt
└── 📂 Validación de Respuestas
    └── POST Validar formato de respuesta JSON
```

Cada request incluye:
- **Pre-request Script:** Configuración de datos dinámicos y timestamps.
- **Test Script:** Aserciones con `pm.test()` para validar status codes, estructura de respuesta, tiempos y contenido.

---

## 3. Cómo Importar la Colección

### 3.1 Importar en Postman (GUI)

1. Abra **Postman** en su computadora.
2. Haga clic en **Import** (botón en la esquina superior izquierda).
3. Seleccione la pestaña **File**.
4. Arrastre o seleccione los siguientes archivos:
   - `eco_predict_nlq_collection.json`
   - `eco_predict_nlq_environment.json`
5. Haga clic en **Import** para confirmar.
6. En la esquina superior derecha, seleccione el entorno **"EcoPredict-NLQ - QA Environment"** del menú desplegable de entornos.

### 3.2 Importar desde el Workspace Compartido

1. Acceda al [workspace de Postman](https://gslan99-419711.postman.co/workspace/6a886e46-0703-4dba-a30f-cdb6f4d72921).
2. La colección y el entorno ya están disponibles para todos los miembros del equipo.
3. Si necesita una copia local, use **Fork Collection** para crear su propia rama de trabajo.

---

## 4. Configuración de Variables de Entorno

El archivo de entorno define las siguientes variables:

| Variable | Valor Inicial | Descripción |
|----------|---------------|-------------|
| `base_url` | `http://localhost:3000/api` | URL base del servidor API. Cambiar según el entorno (local, staging, producción). |
| `api_key` | `your-api-key-here` | Clave de autenticación para el API. **No commitear claves reales.** |
| `nlq_endpoint` | `/v1/nlq/query` | Ruta del endpoint de consultas NLQ. |
| `timeout_ms` | `5000` | Timeout máximo en milisegundos para las peticiones. |

### Configurar para diferentes entornos

**Local:**
```
base_url = http://localhost:3000/api
```

**Staging:**
```
base_url = https://staging-api.ecopredict.dev/api
```

**Producción:**
```
base_url = https://api.ecopredict.dev/api
```

> ⚠️ **Importante:** Nunca almacene claves API reales en el archivo de entorno que se commitea al repositorio. Use variables de entorno del sistema o secretos de GitHub Actions.

---

## 5. Ejecución con Newman (CLI)

[Newman](https://github.com/postmanlabs/newman) es la herramienta CLI oficial de Postman para ejecutar colecciones desde la línea de comandos y en pipelines CI/CD.

### 5.1 Instalación de Newman

```bash
# Instalación global
npm install -g newman

# Instalación del reporter HTML para reportes visuales
npm install -g newman-reporter-htmlextra
```

### 5.2 Ejecución Básica

```bash
newman run src/ia-ops/tests/postman/eco_predict_nlq_collection.json \
  -e src/ia-ops/tests/postman/eco_predict_nlq_environment.json
```

### 5.3 Ejecución con Reportes

```bash
newman run src/ia-ops/tests/postman/eco_predict_nlq_collection.json \
  -e src/ia-ops/tests/postman/eco_predict_nlq_environment.json \
  --reporters cli,junit,htmlextra \
  --reporter-junit-export reports/newman-results.xml \
  --reporter-htmlextra-export reports/newman-report.html
```

### 5.4 Ejecución con Variables Overrideadas

```bash
newman run src/ia-ops/tests/postman/eco_predict_nlq_collection.json \
  -e src/ia-ops/tests/postman/eco_predict_nlq_environment.json \
  --env-var "base_url=https://staging-api.ecopredict.dev/api" \
  --env-var "api_key=$API_KEY"
```

### 5.5 Opciones Útiles de Newman

| Opción | Descripción |
|--------|-------------|
| `--timeout 10000` | Timeout global en milisegundos |
| `--timeout-request 5000` | Timeout por request |
| `--delay-request 500` | Delay entre requests (ms) |
| `--iteration-count 3` | Número de iteraciones de la colección |
| `--bail` | Detener al primer fallo |
| `--verbose` | Output detallado |

---

## 6. Integración con GitHub Actions

### 6.1 Configuración del Workflow

El siguiente paso se integra en el workflow `ai-testing-ci.yml` para ejecutar las pruebas de Postman como parte del pipeline CI/CD:

```yaml
name: AI Testing CI

on:
  push:
    branches: [main, develop]
    paths:
      - 'src/ia-ops/**'
  pull_request:
    branches: [main]
    paths:
      - 'src/ia-ops/**'

jobs:
  test-prompts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # --- Pruebas unitarias con pytest ---
      - name: Configurar Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Instalar dependencias de pytest
        run: pip install pytest

      - name: Ejecutar pruebas de prompts
        run: |
          pytest src/ia-ops/tests/ -v --tb=short \
            --junitxml=reports/pytest-results.xml

      # --- Pruebas de API con Newman ---
      - name: Configurar Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Instalar Newman y reporters
        run: npm install -g newman newman-reporter-htmlextra

      - name: Ejecutar pruebas de API con Newman
        run: |
          newman run src/ia-ops/tests/postman/eco_predict_nlq_collection.json \
            -e src/ia-ops/tests/postman/eco_predict_nlq_environment.json \
            --env-var "base_url=${{ secrets.API_BASE_URL }}" \
            --env-var "api_key=${{ secrets.API_KEY }}" \
            --reporters cli,junit,htmlextra \
            --reporter-junit-export reports/newman-results.xml \
            --reporter-htmlextra-export reports/newman-report.html
        continue-on-error: false

      # --- Publicar artefactos ---
      - name: Subir reportes de pruebas
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-reports
          path: reports/
          retention-days: 30
```

### 6.2 Secretos Necesarios en GitHub

Configure los siguientes secretos en **Settings → Secrets and variables → Actions**:

| Secreto | Descripción |
|---------|-------------|
| `API_BASE_URL` | URL base del API para el entorno de CI (ej: `https://staging-api.ecopredict.dev/api`) |
| `API_KEY` | Clave de autenticación para el API en el entorno de CI |

### 6.3 Artefactos Generados

Después de cada ejecución del workflow, los siguientes artefactos estarán disponibles para descarga en GitHub Actions:

| Artefacto | Formato | Descripción |
|-----------|---------|-------------|
| `reports/pytest-results.xml` | JUnit XML | Resultados de pruebas pytest |
| `reports/newman-results.xml` | JUnit XML | Resultados de pruebas Newman |
| `reports/newman-report.html` | HTML | Reporte visual detallado de Newman |

---

## 7. Escritura de Tests en Postman

### 7.1 Estructura de un Test Script

```javascript
// Verificar código de estado
pm.test("Status code es 200", function () {
    pm.response.to.have.status(200);
});

// Verificar estructura de respuesta
pm.test("La respuesta tiene el campo 'data'", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property("data");
});

// Verificar tiempo de respuesta
pm.test("Tiempo de respuesta menor a 5 segundos", function () {
    pm.expect(pm.response.responseTime).to.be.below(5000);
});
```

### 7.2 Convenciones del Equipo

- Todos los tests deben tener nombres descriptivos en español.
- Usar `pm.expect()` (Chai assertions) para las validaciones.
- Incluir validación de tiempo de respuesta en cada request.
- Documentar el propósito de cada request en la descripción de Postman.

---

## 8. Solución de Problemas

### Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `connect ECONNREFUSED` | El servidor API no está corriendo | Iniciar el servidor local o verificar la URL base |
| `TIMEOUT` | El servidor tarda demasiado en responder | Aumentar `timeout_ms` o verificar el rendimiento del servidor |
| `401 Unauthorized` | Clave API inválida o no configurada | Verificar la variable `api_key` en el entorno |
| `newman: command not found` | Newman no está instalado | Ejecutar `npm install -g newman` |

---

## 9. Referencias

- [Documentación oficial de Postman](https://learning.postman.com/docs/)
- [Newman en GitHub](https://github.com/postmanlabs/newman)
- [newman-reporter-htmlextra](https://github.com/DannyDainton/newman-reporter-htmlextra)
- [GitHub Actions — Documentación](https://docs.github.com/es/actions)
- [EcoPredict-NLQ QA Workspace](https://gslan99-419711.postman.co/workspace/6a886e46-0703-4dba-a30f-cdb6f4d72921)
