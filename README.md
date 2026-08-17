# EcoPredict & NLQ

**Sistema de Alerta e Investigación Ambiental Ciudadana**

EcoPredict & NLQ es un sistema orientado al análisis de información ambiental mediante **Open Data, automatización, Inteligencia Artificial y consultas en lenguaje natural (NLQ)**.

## Objetivo

* Integrar fuentes de datos ambientales.
* Automatizar la ingesta y procesamiento de información.
* Utilizar IA para detectar patrones y anomalías.
* Permitir consultas mediante lenguaje natural.
* Aplicar buenas prácticas de **DevSecOps**.

---
## Arquitectura del Sistema - EcoPredict & NLQ
```mermaid
flowchart TD
    U["Usuario<br/>[Persona]"]

    subgraph EcoPredict ["EcoPredict & NLQ"]
        FE["Frontend<br/>[Container: React/Vue]"]
        N8N["n8n — Orquestador<br/>[Container: Self-hosted]"]
        DB[("PostgreSQL<br/>BD vectorial (RAG)")]
        LLM["LLM multi-modelo<br/>Multimodelo (failover)"]
        IAOPS["IA Ops / MLOps<br/>[Container: LangSmith/Langfuse]"]
    end

    EXT_API["APIs externas<br/>OpenAQ, SENAMHI"]
    TG["Telegram<br/>Canal externo"]

    U --> FE
    FE --> N8N
    EXT_API --> N8N
    N8N --> DB
    N8N --> LLM
    DB <--->|RAG| LLM
    LLM --> TG
    DB --> IAOPS
    LLM --> IAOPS

```
##  Diagrama de Flujos  
```mermaid
flowchart TD
    A1["n8n<br/>Cron 06:00 a.m."]
    A2["APIs externas<br/>OpenAQ, SENAMHI"]
    A3[("PostgreSQL<br/>Guarda datos limpios")]
    A4["LLM multi-modelo<br/>Detecta anomalías"]
    A5["Telegram<br/>Alerta si hay anomalía"]

    A1 -->|1| A2
    A2 -->|2| A3
    A3 -->|3| A4
    A4 -->|4| A5 


    B1["Frontend<br/>Usuario escribe pregunta"]
    B2["n8n<br/>Webhook POST /nlq"]
    B3[("PostgreSQL<br/>RAG: recupera contexto")]
    B4["LLM multi-modelo<br/>Responde con contexto"]
    B5["n8n<br/>Formatea respuesta JSON"]
    B6["Frontend<br/>Chart.js renderiza gráfico"]

    B1 -->|1| B2
    B2 -->|2| B3
    B3 -->|3| B4
    B4 -->|4| B5
    B5 -->|5| B6 
```    
## 📁 Estructura principal

```text
├── .github/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│
├── src/
│   ├── frontend/
│   ├── n8n-workflows/
│   ├── database/
│   └── ia-ops/
│
├── infrastructure/
├── .gitignore
├── LICENSE
└── README.md
```

* `.github/` — Plantillas y workflows de CI/CD.
* `src/frontend/` — Código del frontend.
* `src/n8n-workflows/` — Workflows de n8n.
* `src/database/` — Migraciones y seeders.
* `src/ia-ops/` — Prompts, pruebas y configuración de IA.
* `infrastructure/` — Configuración de infraestructura local.

---

## Uso local

El proyecto se encuentra actualmente en fase de **estructuración y configuración**.

Los requisitos y pasos de ejecución de cada componente se documentarán conforme avance la integración.

Las variables de entorno deberán basarse en:

```text
infrastructure/.env.example
```

No se deben subir archivos `.env` reales.

---

## Gobernanza y seguridad

* `main` será la rama principal y estará protegida.
* Los cambios deberán realizarse mediante **Pull Requests**.
* Todo PR deberá pasar las validaciones automáticas.
* Los desarrolladores trabajarán en ramas independientes.
* No se deben incluir credenciales, tokens ni secretos en el repositorio.
* Los workflows de n8n deberán revisarse antes de incorporarse.
* Las validaciones de calidad y seguridad se automatizarán mediante **GitHub Actions**.

---

## Estado

**Fase actual:** Estructuración y gobernanza DevSecOps.

La integración de frontend, backend, n8n, base de datos e IA se realizará progresivamente.

