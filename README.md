# EcoPredict & NLQ

**Sistema de Alerta e Investigación Ambiental Ciudadana**

EcoPredict & NLQ es un sistema de análisis de la calidad del aire que combina **Open Data, automatización con n8n, Inteligencia Artificial y consultas en lenguaje natural (NLQ)**. Ingesta mediciones ambientales, detecta anomalías, envía alertas por Telegram, responde preguntas ciudadanas con respaldo normativo (RAG) y ofrece analítica histórica por distrito.

![Vercel](https://img.shields.io/badge/Frontend-Vercel-000000?logo=vercel&logoColor=white)
![Oracle Cloud](https://img.shields.io/badge/Backend-Oracle%20Cloud-F80000?logo=oracle&logoColor=white)
![n8n](https://img.shields.io/badge/Orquestador-n8n-EA4B71?logo=n8n&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/BD-PostgreSQL%2016%20%2B%20pgvector-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Contenedores-Docker%20Compose-2496ED?logo=docker&logoColor=white)

---

## Contenido

- [Objetivos](#objetivos)
- [Arquitectura del sistema](#arquitectura-del-sistema)
- [Diagrama de despliegue](#diagrama-de-despliegue)
- [Flujos de orquestación](#flujos-de-orquestación)
- [Microfrontends y rutas](#microfrontends-y-rutas)
- [Endpoints](#endpoints)
- [Base de datos](#base-de-datos)
- [Seguridad](#seguridad)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Uso local](#uso-local)
- [Costos](#costos)
- [Estado](#estado)

---

## Objetivos

- Integrar fuentes de datos ambientales abiertas (OpenAQ y SENAMHI).
- Automatizar la ingesta, el procesamiento y la detección de anomalías.
- Enviar alertas proactivas por Telegram a los ciudadanos suscritos a cada zona.
- Responder consultas en lenguaje natural con IA y respaldo normativo mediante RAG.
- Ofrecer indicadores históricos de calidad del aire por distrito.
- Aplicar buenas prácticas de **DevSecOps**: CI/CD, mínimo privilegio y observabilidad.

---

## Arquitectura del sistema

Vista de contexto: qué hace cada componente y cómo se relacionan.

```mermaid
flowchart LR
    U(["👤 Usuario web"])
    CIU(["👤 Ciudadano<br/>Telegram"])

    subgraph ECO["EcoPredict & NLQ"]
        direction LR
        FE["Frontend<br/>React + Vite · Microfrontends<br/>Vercel"]
        BFF["Capa serverless (BFF)<br/>Vercel Function + CDN"]
        N8N["n8n — Orquestador<br/>Flujos A · B · C · D · Bot"]
        DB[("PostgreSQL 16 + pgvector<br/>Datos · Vectores RAG · Analítica")]
    end

    EXT["Fuentes de datos<br/>OpenAQ API v3 · SENAMHI"]
    LLM["LLM multimodelo<br/>Groq + Gemini (failover)"]
    OBS["IA Ops<br/>Langfuse Cloud"]
    TG["Telegram Bot API"]

    U --> FE
    FE -->|"chat · estado · analítica"| N8N
    FE -->|"dashboard"| BFF --> N8N
    EXT --> N8N
    N8N <--> DB
    N8N <-->|"embeddings · juez · resúmenes"| LLM
    N8N -->|"trazas"| OBS
    N8N <--> TG <--> CIU

    classDef core fill:#E0F2FE,stroke:#0284C7,color:#0C4A6E
    classDef data fill:#E0E7FF,stroke:#4338CA,color:#1E1B4B
    classDef ext fill:#FEF3C7,stroke:#D97706,color:#78350F
    classDef person fill:#F1F5F9,stroke:#64748B,color:#0F172A
    class FE,BFF,N8N core
    class DB data
    class EXT,LLM,OBS,TG ext
    class U,CIU person
```

---

## Diagrama de despliegue

Infraestructura real: frontend en **Vercel**, backend en una VM de **Oracle Cloud Infrastructure (OCI)** con Docker Compose, CI/CD en **GitHub** y servicios externos.

```mermaid
flowchart TB
    U(["👤 Usuario web"])

    subgraph GH["GitHub · Monorepo"]
        direction TB
        REPO["Repositorio"] --> CI["CI · build<br/>frontend-ci.yml"]
        REPO --> CD["CD · deploy<br/>cd.yml"]
    end

    subgraph VERCEL["Vercel"]
        direction TB
        SHELL["frontend-shell<br/>vercel.json · rewrites"]
        subgraph MFS["Microfrontends"]
            direction LR
            CHAT["nlq-chat"]
            EST["estado"]
            ANA["analytics"]
            AJU["ajustes"]
            DASH["dashboard"]
        end
        PROXY["/api-proxy<br/>rewrite → VM · Flujos B y D"]
        subgraph SLS["Serverless · BFF"]
            direction LR
            CDN["CDN · caché"] -->|"MISS"| FN["Vercel Function<br/>api/flujo-c/[ruta].js · Flujo C"]
        end
        SHELL -->|"rewrites"| MFS
    end

    subgraph OCI["Oracle Cloud Infrastructure"]
        direction TB
        subgraph VCN["VCN ecopredict-vcn · 10.0.0.0/16 · Subred pública 10.0.1.0/24"]
            direction TB
            IGW["Internet Gateway<br/>HTTPS 443"]
            subgraph VM["VM ecopredict-server · Ubuntu 22.04 · 1 GB RAM · 144.22.203.51"]
                direction TB
                subgraph NET["Docker Compose · eco_network"]
                    direction TB
                    NGINX["aire_nginx<br/>Proxy inverso HTTPS"]
                    N8N["aire_n8n<br/>Flujos A · B · C · D · Bot de Telegram"]
                    PG[("aire_postgres<br/>PostgreSQL 16 + pgvector")]
                end
            end
        end
        BV[("OCI Block Volume<br/>datos de PostgreSQL")]
    end

    subgraph EXT["Servicios externos"]
        direction TB
        OAQ["OpenAQ API v3"]
        TG["Telegram Bot API"]
        GEM["Google Gemini<br/>embeddings · failover"]
        GRQ["Groq<br/>gpt-oss-120b"]
        LF["Langfuse Cloud<br/>trazas de LLM"]
    end

    SEN["SENAMHI .xlsx"]
    CIU(["👤 Ciudadano"])

    U -->|"HTTPS"| SHELL
    CHAT & EST & ANA -.->|"fetch()"| PROXY
    DASH -.->|"fetch()"| CDN
    PROXY -.->|"HTTPS · X-API-Key"| IGW
    FN -.->|"HTTPS · X-API-Key"| IGW
    IGW --> NGINX -->|"proxy_pass"| N8N
    N8N <-->|"SQL · TCP 5432"| PG
    PG <--> BV
    SEN -.->|"import (QA)"| PG
    N8N --> OAQ
    N8N <--> TG
    N8N --> GEM
    N8N --> GRQ
    N8N -.-> LF
    TG <--> CIU
    CI -.->|"deploy"| VERCEL
    CD -.->|"SSH + docker compose up"| VM

    classDef vercel fill:#F8FAFC,stroke:#0F172A,color:#0F172A
    classDef sls fill:#DCFCE7,stroke:#059669,color:#064E3B
    classDef oci fill:#FEE2E2,stroke:#DC2626,color:#7F1D1D
    classDef svc fill:#DBEAFE,stroke:#2563EB,color:#1E3A8A
    classDef ext fill:#FEF3C7,stroke:#D97706,color:#78350F
    classDef gh fill:#F1F5F9,stroke:#475569,color:#0F172A
    class SHELL,CHAT,EST,ANA,AJU,DASH,PROXY vercel
    class CDN,FN sls
    class IGW,BV oci
    class NGINX,N8N,PG svc
    class OAQ,TG,GEM,GRQ,LF,SEN ext
    class REPO,CI,CD gh
```

| Capa | Plataforma | Componentes | Responsabilidad |
| --- | --- | --- | --- |
| Presentación | Vercel | `frontend-shell`, 5 microfrontends, `/api-proxy` | Interfaz ciudadana y enrutamiento de solicitudes |
| Serverless (BFF) | Vercel | CDN con caché y Vercel Function | Intermediario seguro y con caché para el Flujo C |
| CI/CD | GitHub | Monorepo, `frontend-ci.yml`, `cd.yml` | Compilación y despliegue automático |
| Cómputo | OCI | `aire_nginx`, `aire_n8n` | Entrada HTTPS y orquestación de flujos |
| Persistencia | OCI | `aire_postgres`, OCI Block Volume | Datos ambientales, vectores, analítica y suscriptores |
| Servicios externos | Nube | OpenAQ, Telegram, Gemini, Groq, Langfuse | Datos, mensajería, IA y observabilidad |

---

## Flujos de orquestación

Todos los flujos se ejecutan en `aire_n8n`. Las llamadas a modelos de lenguaje se registran en **Langfuse** mediante un sub-workflow compartido.

| Flujo | Disparador | Qué hace | Consumidor |
| --- | --- | --- | --- |
| **A** · Ingesta y alertas | Cron 06:00 | Ingesta OpenAQ, detecta anomalías (z-score) y envía alertas por zona | Telegram |
| **Bot de Telegram** | Webhook del bot | Altas y bajas de suscriptores (`/start`, `/suscribir`, `/baja`) | Ciudadano |
| **B** · NLQ con RAG | `POST /nlq` | Responde preguntas en lenguaje natural con respaldo normativo | `nlq-chat`, `estado` |
| **C** · Lectura del dashboard | Webhooks GET | Devuelve estaciones, series horarias y alertas | `dashboard` (vía BFF) |
| **D** · Analítica histórica | Cron 06:30, cron lunes 07:00 y 5 webhooks GET | Agregados diarios, resumen semanal con IA e indicadores por distrito | `analytics` |

### Flujo A · Ingesta y alertas + Bot de Telegram

```mermaid
flowchart TB
    subgraph A["Flujo A · Ingesta y alertas"]
        direction LR
        A1["⏰ Cron 06:00"] --> A2["Ingesta<br/>OpenAQ API v3"]
        A2 --> A3[("mediciones_aire")]
        A3 --> A4["Detección de anomalías<br/>z-score por estación"]
        A4 --> A5["Filtro por zona<br/>suscriptores de la estación"]
        A5 --> A6{"¿Cooldown<br/>vigente?"}
        A6 -->|"Sí"| A7["Omitir envío"]
        A6 -->|"No"| A8["sendMessage<br/>Telegram Bot API"]
        A8 --> A9[("Registrar último envío")]
    end

    subgraph T["Bot de Telegram"]
        direction LR
        T1(["👤 Ciudadano"]) -->|"/start · /suscribir · /baja"| T2["Webhook del bot"]
        T2 --> T3["Alta / baja de suscriptor"]
        T3 --> T4[("suscriptores_telegram")]
        T3 --> T5["Respuesta al ciudadano"]
    end

    T4 -.->|"consulta suscriptores y cooldown"| A5

    classDef step fill:#FFEDD5,stroke:#EA580C,color:#7C2D12
    classDef data fill:#E0E7FF,stroke:#4338CA,color:#1E1B4B
    classDef dec fill:#FEF9C3,stroke:#CA8A04,color:#713F12
    class A1,A2,A4,A5,A7,A8,T2,T3,T5 step
    class A3,A9,T4 data
    class A6 dec
```

### Flujo B · Consulta en lenguaje natural con RAG

La rama normativa usa **RAG (Retrieval-Augmented Generation)**: antes de responder, recupera fragmentos reales de la normativa desde `pgvector`, de modo que el modelo no invente normas.

```mermaid
flowchart TD
    B1["💬 nlq-chat<br/>pregunta del ciudadano"] -->|"POST /nlq vía /api-proxy"| B2["aire_nginx → aire_n8n"]
    B2 --> B3{"Extracción de intención"}
    B3 -->|"Datos / lugares"| B4["Consulta directa<br/>SQL parametrizado · rol nlq_reader"]
    B3 -->|"Normativa"| B5["Embedding de la pregunta<br/>Gemini · 768 dimensiones"]
    B5 --> B6[("pgvector · documentos_rag<br/>Top-5 por distancia coseno (<=>)<br/>índice HNSW")]
    B6 --> B7["Juez LLM · Groq<br/>elige el fragmento y valida el ID"]
    B4 --> B8["Respuesta JSON"]
    B7 --> B8
    B8 --> B9["💬 nlq-chat"]
    B8 -.-> B10[("logs_consultas_nlq<br/>auditoría")]
    B7 -.-> B11["Langfuse<br/>trazas"]

    classDef step fill:#FFEDD5,stroke:#EA580C,color:#7C2D12
    classDef data fill:#E0E7FF,stroke:#4338CA,color:#1E1B4B
    classDef dec fill:#FEF9C3,stroke:#CA8A04,color:#713F12
    classDef ext fill:#FEF3C7,stroke:#D97706,color:#78350F
    class B1,B2,B4,B5,B7,B8,B9 step
    class B6,B10 data
    class B3 dec
    class B11 ext
```

### Flujo C · Lectura del dashboard con capa serverless (BFF)

El dashboard no llama directo a n8n: pasa por una **Vercel Function** que custodia la clave `X-API-Key`, solo acepta rutas de una lista blanca y deja que la **CDN** sirva respuestas en caché, incluso si n8n no está disponible (`stale-if-error`).

```mermaid
sequenceDiagram
    autonumber
    participant MF as dashboard
    participant CDN as Vercel CDN
    participant FN as Vercel Function
    participant NG as aire_nginx
    participant N8 as n8n · Flujo C
    participant DB as PostgreSQL

    MF->>CDN: GET /api/flujo-c/estaciones (sin clave)
    alt Copia vigente en caché (HIT)
        CDN-->>MF: JSON desde caché
    else Sin copia vigente (MISS)
        CDN->>FN: invoca la función
        FN->>FN: valida la ruta (lista blanca)
        FN->>NG: HTTPS + X-API-Key (desde el servidor)
        NG->>N8: proxy_pass al webhook
        N8->>DB: SELECT
        DB-->>N8: filas
        N8-->>FN: JSON
        FN-->>CDN: JSON + Cache-Control
        CDN-->>MF: JSON
    end
    Note over CDN,FN: Cache-Control: s-maxage=300 · stale-while-revalidate=600 · stale-if-error=86400
```

### Flujo D · Analítica histórica de calidad del aire

Reutiliza las mediciones que el Flujo A ya guarda (sin volver a consultar OpenAQ ni SENAMHI) y sirve indicadores por distrito al microfrontend **Data Analytics**. Sus tres partes son independientes.

```mermaid
flowchart LR
    subgraph P1["Parte 1 · Agregación diaria"]
        direction TB
        D1["⏰ Cron 06:30<br/>30 min después del Flujo A"] --> D2{"¿Flujo A ya<br/>ingestó hoy?"}
        D2 -->|"No"| D3["Espera 10 min<br/>y reintenta"]
        D2 -->|"Sí"| D4["Agregación SQL<br/>PM2.5 y PM10 por distrito y día"]
        D4 --> D5[("UPSERT<br/>analitica_diaria")]
    end

    subgraph P2["Parte 2 · Resumen semanal con IA"]
        direction TB
        D6["⏰ Cron lunes 07:00"] --> D7["Lee agregados de la semana"]
        D7 --> D8["Groq (principal)<br/>Gemini (failover)"]
        D8 --> D9["Valida texto<br/>sin SQL · cifras de los agregados"]
        D9 --> D10[("UPSERT<br/>analitica_insights")]
    end

    subgraph P3["Parte 3 · Endpoints de lectura"]
        direction TB
        D11["📊 analytics<br/>vía /api-proxy"] -->|"GET /analitica/*"| D12["Valida X-API-Key<br/>y parámetros"]
        D12 --> D13["Consulta SQL<br/>rol nlq_reader"]
        D13 --> D14["JSON camelCase"]
    end

    D5 -.-> D7
    D5 -.-> D13
    D10 -.-> D13

    classDef step fill:#FFEDD5,stroke:#EA580C,color:#7C2D12
    classDef data fill:#EDE9FE,stroke:#7C3AED,color:#2E1065
    classDef dec fill:#FEF9C3,stroke:#CA8A04,color:#713F12
    class D1,D3,D4,D6,D7,D8,D9,D11,D12,D13,D14 step
    class D5,D10 data
    class D2 dec
```

---

## Microfrontends y rutas

| Microfrontend | Proyecto en Vercel | Ruta en el shell | Acceso al backend |
| --- | --- | --- | --- |
| Shell principal | `grupo1-eco-predict-nlq` | `/` | — |
| nlq-chat | `ecopredict-nlq-chat` | `/nlq-chat` | `/api-proxy` → Flujo B |
| estado | `ecopredict-estado-sistema` | `/estado-sistema` | `/api-proxy` → Flujo B |
| analytics | `ecopredict-data-analytics` | `/data-analytics` | `/api-proxy` → Flujo D |
| dashboard | `ecopredict-dashboard-ambiental` | `/dashboard-ambiental` | Vercel Function → Flujo C |
| ajustes | `ecopredict-ajustes` | `/ajustes` | Sin acceso al backend |

---

## Endpoints

| Flujo | Método | Ruta pública | Descripción |
| --- | --- | --- | --- |
| B | `POST` | `/api-proxy/webhook/nlq` | Consulta en lenguaje natural |
| C | `GET` | `/api/flujo-c/estaciones` | Estaciones de monitoreo (vía BFF) |
| C | `GET` | `/api/flujo-c/serie-horaria` | Serie horaria de una estación (vía BFF) |
| C | `GET` | `/api/flujo-c/alertas` | Alertas generadas (vía BFF) |
| D | `GET` | `/analitica/comparativo` | Promedios, variación y tendencia por distrito |
| D | `GET` | `/analitica/ranking-eca` | Distritos ordenados por días sobre el ECA |
| D | `GET` | `/analitica/patron-horario` | Promedio por hora del día |
| D | `GET` | `/analitica/resumen-ia` | Último resumen semanal con IA |
| D | `GET` | `/analitica/distritos` | Distritos con datos y su cobertura |

Las rutas del Flujo D se consumen a través del `/api-proxy`. Todas las llamadas a n8n requieren la cabecera `X-API-Key`.

---

## Base de datos

`aire_postgres` (PostgreSQL 16 + pgvector) · base `calidad_aire`

| Grupo | Tablas principales | Flujo |
| --- | --- | --- |
| Ambientales | `estaciones`, `mediciones_aire`, `ingesta_estado` | A (escribe) · C y D (leen) |
| Alertas | alertas generadas | A |
| Telegram | `suscriptores_telegram` (estación · cooldown) | A y Bot de Telegram |
| NLQ · IA | `logs_consultas_nlq` | B |
| RAG · pgvector | `documentos_rag` (768 dimensiones · índice HNSW) | B |
| Analítica | `analitica_diaria`, `analitica_insights` | D |
| Referencia QA | datos importados de SENAMHI | Calidad de datos |

---

## Seguridad

- **HTTPS extremo a extremo:** el navegador solo habla con su propio dominio en Vercel; el `/api-proxy` y la Vercel Function llegan a la VM por HTTPS a través de `aire_nginx`.
- **Clave en el servidor (BFF):** el dashboard no envía credenciales; la Vercel Function agrega `X-API-Key` desde variables de entorno sin prefijo `VITE_`.
- **Lista blanca de rutas:** la función del Flujo C rechaza con `403` cualquier ruta no autorizada.
- **Mínimo privilegio en la BD:** las consultas del Flujo B y los endpoints del Flujo D usan el rol de solo lectura `nlq_reader`.
- **IA controlada:** el RAG valida el identificador del fragmento elegido y el resumen semanal valida que no contenga SQL ni cifras ajenas a los agregados.
- **Secretos fuera del repositorio:** no se suben archivos `.env` reales.

---

## Estructura del repositorio

```text
Grupo1_EcoPredict-NLQ/
├── .github/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/                 # frontend-ci.yml · cd.yml
├── infrastructure/
│   ├── docker-compose.yml
│   ├── docker-compose.production.yml
│   └── .env.example
├── packages/
├── postman/                       # Colecciones de pruebas de endpoints
├── src/
│   ├── frontend-shell/            # Shell principal (Vercel)
│   │   ├── api/flujo-c/[ruta].js  # Vercel Function · BFF del Flujo C
│   │   ├── src/
│   │   └── vercel.json            # rewrites y /api-proxy
│   ├── frontend/                  # Microfrontends
│   ├── n8n-workflows/             # Workflows exportados de n8n
│   ├── database/
│   │   └── migrations/            # Migraciones (incluye 004_flujo_d_analitica.sql)
│   └── ia-ops/                    # Prompts, pruebas y configuración de IA
├── .gitignore
├── LICENSE
└── README.md
```

---

## Uso local

1. Copia las variables de entorno de ejemplo y completa los valores:

   ```bash
   cp infrastructure/.env.example infrastructure/.env
   ```

2. Levanta los servicios del backend (Nginx, n8n y PostgreSQL):

   ```bash
   docker compose -f infrastructure/docker-compose.yml up -d
   ```

3. Instala y ejecuta el frontend shell:

   ```bash
   cd src/frontend-shell
   npm install
   npm run dev
   ```

> No subas archivos `.env` reales. Las variables de producción se configuran en Vercel y en la VM de OCI.

**Variables de entorno principales**

| Variable | Dónde | Uso |
| --- | --- | --- |
| `VITE_N8N_WEBHOOK_URL` | Microfrontends (Vercel) | Ruta del webhook vía `/api-proxy` |
| `VITE_N8N_API_KEY` | Microfrontends (Vercel) | Clave para los flujos que van por `/api-proxy` |
| `N8N_BASE_URL` | Vercel Function | URL base de los webhooks de n8n |
| `N8N_API_KEY` | Vercel Function | Clave de n8n custodiada en el servidor |

---

## Costos

| Proveedor | Plan | Costo |
| --- | --- | --- |
| Vercel | Hobby (6 proyectos + Vercel Function) | PEN 0.00 |
| Oracle Cloud | Always Free | PEN 0.00 |
| **Total asumido por el equipo** | | **PEN 0.00** |

---

## Estado

**Sprint 4 · Implementación e integración.**

- ✅ Ingesta diaria y alertas por zona con cooldown (Flujo A + Bot de Telegram).
- ✅ Consulta en lenguaje natural con RAG y pgvector (Flujo B).
- ✅ Capa serverless BFF con caché para el dashboard (Flujo C · HT-07).
- ✅ Analítica histórica por distrito con resumen semanal con IA (Flujo D).
- ✅ Integración del Flujo D en CI/CD y pruebas de contrato de QA.