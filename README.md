# Arquitectura del Sistema - EcoPredict & NLQ

Este documento muestra la arquitectura general en 5 capas y la secuencia detallada de los dos flujos principales del proyecto EcoPredict & NLQ.

---

## 1. Arquitectura General del Sistema

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
## 2. Diagrama de Flujos  
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
## 3. Secuencia de Flujo A

Ejecución Programada: Un temporizador interno en n8n activa el flujo de manera automática todos los días a las 06:00 a.m.

Consulta a Fuentes Externas: n8n realiza peticiones HTTP a las APIs externas de OpenAQ y SENAMHI para extraer las lecturas más recientes.

Procesamiento y Persistencia: El orquestador estandariza las mediciones y las guarda estructuradamente dentro de PostgreSQL.

Análisis de Anomalías: La información registrada se evalúa mediante el LLM multi-modelo para determinar picos inusuales de contaminación.

Emisión de Alertas: En caso de confirmarse un patrón anómalo, n8n despacha una notificación de alerta hacia el canal de Telegram.

## 4. Secuencia de Flujo B

Entrada de Consulta: El usuario escribe una pregunta en lenguaje natural a través de la interfaz del Frontend.

Recepción Webhook: El Frontend envía una petición HTTP POST /nlq hacia el punto de entrada de n8n.

Búsqueda Semántica (RAG): n8n ejecuta una consulta vectorial en PostgreSQL (pgvector) para extraer el contexto histórico más relevante.

Generación de Respuesta: La consulta enriquecida con el contexto recuperado se transfiere al LLM multi-modelo, el cual construye una respuesta precisa.

Formateo de Salida: n8n convierte la respuesta recibida en una estructura de datos JSON estandarizada.

Renderizado Visual: El Frontend procesa el archivo JSON y genera gráficos dinámicos interactivos mediante Chart.js.

