# EcoPredict & NLQ

**Sistema de Alerta e Investigación Ambiental Ciudadana**

EcoPredict & NLQ es un sistema orientado al análisis de información ambiental mediante **Open Data, automatización, Inteligencia Artificial y consultas en lenguaje natural (NLQ)**.

## Objetivo

- Integrar fuentes de datos ambientales.
- Automatizar la ingesta y procesamiento de información.
- Utilizar IA para detectar patrones y anomalías.
- Permitir consultas mediante lenguaje natural.
- Aplicar buenas prácticas de **DevSecOps**.

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
## 🚀 Diagrama de Despliegue — EcoPredict & NLQ en OCI

Representación de la infraestructura desplegada en **Oracle Cloud Infrastructure (OCI)**, mostrando la red, el nodo de cómputo, los servicios internos y las integraciones externas.

```mermaid
flowchart TD
    Usuario(["Usuario"])

    subgraph OCI["Oracle Cloud Infrastructure «cloud»"]
        direction TB
        subgraph VCN["VCN: ecopredict-vcn — 10.0.0.0/16 «network»"]
            direction TB
            subgraph SUBNET["Subred Pública — 10.0.1.0/24 «subnet»"]
                direction TB
                IGW["Internet Gateway<br/>«node»<br/>Recibe HTTPS 443 / HTTP 80"]

                subgraph SERVER["ecopredict-server «node»<br/>VM.Standard.E2.1.Micro · Always Free<br/>1 OCPU / 6 GB RAM · Ubuntu x86_64<br/>IP pública: 144.22.203.51"]
                    direction TB
                    NGINX["Nginx<br/>Reverse Proxy"]
                    PM2["PM2<br/>Process Manager"]
                    FE["Frontend<br/>Vite / React — Microfrontend"]
                    N8N["n8n<br/>Orquestador"]
                    DB[("PostgreSQL 16")]

                    NGINX -->|"proxy_pass<br/>localhost:3000"| FE
                    NGINX -->|"proxy_pass /webhook/<br/>:5678"| N8N
                    PM2 -.->|"Supervisa / reinicia"| FE
                    N8N -->|"TCP/5432"| DB
                end

                IGW -->|"Enruta tráfico entrante"| NGINX
            end
        end
    end

    OpenAQ[["OpenAQ API v3<br/>Sistema Externo<br/>Datos de calidad del aire"]]
    SENAMHI[["SENAMHI Source<br/>Fuente Externa<br/>Sin API pública"]]

    Usuario -->|"HTTP / HTTPS · 80 / 443"| IGW
    N8N -->|"HTTPS GET api.openaq.org/v3<br/>ingesta programada"| OpenAQ
    N8N -->|"Carga manual de reporte<br/>HTTPS"| SENAMHI

    classDef cloudStyle fill:#0f1b2d,stroke:#5da8ff,stroke-width:1.5px,color:#fff
    classDef netStyle fill:#1a2e1a,stroke:#7fd97f,stroke-width:1px,color:#fff
    classDef subnetStyle fill:#2e2410,stroke:#e0a83b,stroke-width:1px,color:#fff
    classDef nodeStyle fill:#111,stroke:#5da8ff,stroke-width:1px,color:#fff
    classDef svcStyle fill:#5da8ff,stroke:#0f1b2d,color:#0f1b2d,font-weight:bold
    classDef extStyle fill:#555,stroke:#ccc,color:#fff

    class OCI cloudStyle
    class VCN netStyle
    class SUBNET subnetStyle
    class SERVER nodeStyle
    class NGINX,PM2,FE,N8N,DB,IGW svcStyle
    class OpenAQ,SENAMHI extStyle
```

## Diagrama de Flujos

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

- `.github/` — Plantillas y workflows de CI/CD.
- `src/frontend/` — Código del frontend.
- `src/n8n-workflows/` — Workflows de n8n.
- `src/database/` — Migraciones y seeders.
- `src/ia-ops/` — Prompts, pruebas y configuración de IA.
- `infrastructure/` — Configuración de infraestructura local.

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

- `main` será la rama principal y estará protegida.
- Los cambios deberán realizarse mediante **Pull Requests**.
- Todo PR deberá pasar las validaciones automáticas.
- Los desarrolladores trabajarán en ramas independientes.
- No se deben incluir credenciales, tokens ni secretos en el repositorio.
- Los workflows de n8n deberán revisarse antes de incorporarse.
- Las validaciones de calidad y seguridad se automatizarán mediante **GitHub Actions**.

---

## Estado

Fase actual: Implementación e integración de la solución.

El proyecto se encuentra en proceso de implementación e integración de sus componentes de infraestructura, backend, n8n, base de datos, QA, seguridad, automatización CI/CD y frontend, de acuerdo con las tareas definidas para el desarrollo de la solución.
