# 🛡️ Seguridad y Gobernanza – EcoPredict & NLQ

> **EcoPredict & NLQ – Sistema de Alerta e Investigación Ambiental Ciudadana**

Este documento describe las medidas de **seguridad, protección, calidad y gobernanza** aplicadas al repositorio y a los componentes de la aplicación.

El objetivo es establecer controles que permitan proteger el código fuente, controlar los cambios, validar automáticamente las modificaciones, detectar riesgos de seguridad y mantener un flujo de desarrollo controlado.

---

## 1. Modelo general de protección

La seguridad del proyecto se implementa mediante diferentes capas que actúan sobre el repositorio, el código, los servicios y la aplicación desplegada.

```text
                          ECOPREDICT & NLQ
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
     GOBERNANZA                CÓDIGO                  APLICACIÓN
        │                         │                         │
   Branches / PRs              CodeQL                 OWASP ZAP
   Rulesets                    Validaciones            Análisis DAST
   Revisiones                  CI/CD                   OCI
        │                         │                         │
        └─────────────────────────┼─────────────────────────┘
                                  │
                                  ▼
                          GESTIÓN DE RIESGOS
                                  │
                                  ▼
                     GitHub Code Scanning
```

---

# 2. Gobernanza del repositorio

El repositorio utiliza controles de gobernanza para mantener un flujo de cambios controlado y evitar modificaciones directas no autorizadas sobre la rama principal.

### Protección de ramas

La rama `main` se encuentra protegida mediante las reglas configuradas en GitHub.

Entre los principales controles se consideran:

| Control                | Propósito                                                |
| ---------------------- | -------------------------------------------------------- |
| Protección de `main`   | Evitar modificaciones directas                           |
| Pull Requests          | Integrar cambios mediante revisión                       |
| Checks obligatorios    | Validar automáticamente los cambios                      |
| Revisión de cambios    | Reducir el riesgo de integrar modificaciones incorrectas |
| Reglas del repositorio | Mantener condiciones de integración controladas          |

### 🔄 Flujo de integración

```text
 Desarrollo
      │
      ▼
 Rama de trabajo
      │
      ▼
 Pull Request
      │
      ▼
 Validaciones automáticas
      │
      ▼
 Revisión
      │
      ▼
✅ Aprobación
      │
      ▼
🌳 main
```

---

# 3. Pull Requests

Los cambios destinados a la rama principal se gestionan mediante **Pull Requests**.

Esto permite revisar el código y verificar que las validaciones automáticas hayan sido ejecutadas antes de integrar los cambios.

El repositorio utiliza una plantilla de Pull Request para mantener una estructura uniforme en las solicitudes de integración.

```text
.github/
└── PULL_REQUEST_TEMPLATE.md
```

La plantilla permite registrar información como:

- Descripción del cambio.
- Issue relacionado.
- Validaciones realizadas.
- Revisión de seguridad.
- Confirmación de pruebas.

---

# ⚙️ 4. Integración y validación continua

El proyecto utiliza **GitHub Actions** para automatizar controles durante el desarrollo.

```text
                  GitHub Actions
                        │
       ┌────────────────┼────────────────┐
       │                │                │
       ▼                ▼                ▼
     Frontend          n8n              IA
  Validation       Validation         Testing
       │                │                │
       └────────────────┼────────────────┘
                        │
              ┌─────────┴─────────┐
              │                   │
              ▼                   ▼
            SAST                DAST
           CodeQL             OWASP ZAP
```

Las validaciones permiten detectar errores y problemas potenciales antes de que los cambios sean integrados en la rama principal.

---

# 5. Análisis SAST – CodeQL

**CodeQL** se utiliza para realizar análisis estático de seguridad sobre el código fuente.

Este mecanismo permite identificar patrones de código que pueden estar asociados con vulnerabilidades o prácticas inseguras.

### Objetivo

> Analizar el código fuente para detectar posibles riesgos de seguridad antes de que estos lleguen al entorno de ejecución.

Los resultados se integran en:

```text
GitHub
  └── Security
       └── Code scanning
            └── CodeQL
```

---

# 6. Análisis DAST – OWASP ZAP

Para evaluar la seguridad de la aplicación en ejecución se utiliza **OWASP ZAP**.

A diferencia del análisis SAST, DAST analiza el comportamiento de la aplicación desplegada mediante solicitudes HTTP.

```text
☁️ Aplicación desplegada
          │
          ▼
      OWASP ZAP
          │
          ▼
     Análisis dinámico
          │
          ▼
     Hallazgos
          │
          ▼
 GitHub Code Scanning
```

El workflow correspondiente se encuentra en:

```text
.github/workflows/dast.yml
```

Los resultados obtenidos permiten identificar problemas relacionados con configuraciones, cabeceras de seguridad, exposición de información y otros aspectos observables durante la ejecución de la aplicación.

---

# 7. Gestión y centralización de riesgos

Los resultados provenientes de los análisis de seguridad se centralizan mediante **GitHub Code Scanning**.

Esto permite mantener en un mismo lugar los resultados generados por diferentes herramientas.

| Análisis | Herramienta | Objetivo                       |
| -------- | ----------- | ------------------------------ |
| SAST     | CodeQL      | Analizar código fuente         |
| DAST     | OWASP ZAP   | Analizar aplicación desplegada |

La integración de los resultados DAST se realiza mediante el formato **SARIF**, permitiendo que los hallazgos de OWASP ZAP sean registrados dentro de Code Scanning.

---

# 8. Clasificación de riesgos

Los hallazgos de seguridad son evaluados considerando su severidad y el posible impacto sobre la aplicación.

Para el proyecto se utiliza la siguiente clasificación:

| Severidad        | Nivel de riesgo | Prioridad |
| ---------------- | --------------- | --------- |
| 🔴 High          | Crítico         | Inmediata |
| 🟠 Medium        | Alto            | Alta      |
| 🟡 Low           | Moderado        | Media     |
| 🔵 Informational | Informativo     | Revisión  |

Esta clasificación facilita determinar qué resultados requieren mayor atención y cuáles pueden mantenerse bajo seguimiento.

---

# 9. Protección de información sensible

La información sensible no debe almacenarse directamente dentro del código fuente ni dentro de archivos versionados.

Para documentar las variables necesarias para la configuración se utiliza una plantilla:

```text
infrastructure/
└── .env.example
```

El archivo `.env.example` sirve como referencia para identificar las variables requeridas sin almacenar valores sensibles reales.

> ⚠️ Las credenciales, tokens, claves privadas y otros secretos deben mantenerse fuera del código fuente.

---

# 10. Seguridad de la infraestructura

La aplicación utiliza componentes desplegados mediante contenedores y configuraciones de infraestructura.

La validación mediante Docker Compose permite verificar que la definición de los servicios mantenga una configuración coherente antes de utilizarla en un entorno de despliegue.

```text
 Docker Compose
      │
      ▼
 Configuración de servicios
      │
      ▼
 Validación
      │
      ▼
✅ Configuración válida
```

Entre los componentes considerados se encuentran servicios de aplicación, n8n y PostgreSQL.

---

# 11. Aplicación desplegada

La seguridad también considera el entorno donde la aplicación se encuentra ejecutándose.

Para las pruebas DAST se utiliza la aplicación desplegada en **Oracle Cloud Infrastructure (OCI)**.

```text
 OCI
 │
 ├──  Aplicación
 ├──  Servicios
 ├──  PostgreSQL
 └──  Configuración
       │
       ▼
 OWASP ZAP
       │
       ▼
 Code Scanning
```

De esta forma, el análisis de seguridad no se limita al código fuente, sino que también contempla el comportamiento de la aplicación en ejecución.

---

# 📁 12. Organización de los controles

Los principales mecanismos de seguridad y gobernanza se encuentran distribuidos en el repositorio de la siguiente manera:

```text
.github/
├── workflows/
│   ├── frontend.yml
│   ├── n8n-validation.yml
│   ├── ai-testing.yml
│   ├── codeql.yml
│   ├── dast.yml
│   └── cd.yml
│
├── scripts/
│   └── zap-to-sarif.py
│
└── PULL_REQUEST_TEMPLATE.md

infrastructure/
├── docker-compose.yml
└── .env.example
```

> 📌 Los nombres exactos de los workflows pueden variar según la configuración vigente del repositorio.

---

# 📋 13. Resumen de controles

| Área            | Control                    | Estado |
| --------------- | -------------------------- | :----: |
| Gobernanza      | Protección de ramas        |   ✅   |
| Integración     | Pull Requests              |   ✅   |
| Automatización  | GitHub Actions             |   ✅   |
| Calidad         | Validaciones CI            |   ✅   |
| Seguridad       | CodeQL / SAST              |   ✅   |
| Seguridad       | OWASP ZAP / DAST           |   ✅   |
| Gestión         | GitHub Code Scanning       |   ✅   |
| Riesgos         | Clasificación de hallazgos |   ✅   |
| Infraestructura | Docker Compose Validation  |   ✅   |
| Configuración   | `.env.example`             |   ✅   |

---
