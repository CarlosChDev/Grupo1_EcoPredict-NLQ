# 📋 REGISTRO OFICIAL DE INCIDENCIAS Y MEJORAS — SPRINT 1
## Proyecto: EcoPredict & NLQ — Aseguramiento de Calidad (QA)

| Campo | Detalle |
|---|---|
| **Historia de Usuario** | **HU-03:** Automatización de pruebas API con Newman y Calidad de Prompts NLQ (#36) |
| **Sub-Issue** | **T15 (#50):** Registrar evidencias, resultados e incidencias y elaborar el informe técnico de calidad |
| **Auditor de Calidad (QA)** | **Johann Romero Contreras** (Rama: `Romero`) |
| **Fecha de Cierre** | 31 de agosto de 2026 |

---

## 📌 1. Resumen Ejecutivo de Incidencias (Bug Tracking)

Durante el Sprint 1 se detectaron, diagnosticaron, corrigieron y certificaron **4 incidencias técnicas (bugs)** y **1 mejora de infraestructura de datos**, garantizando la estabilidad integral del sistema:

```text
ESTADO DE INCIDENCIAS DEL SPRINT 1:
├── Total de Incidencias Reportadas: 4
├── Total de Incidencias Resueltas: 4 (100% Cerradas)
├── Mejoras de Base de Datos Aplicadas: 1 (100% Completada)
└── Bloqueos Pendientes: 0 (Cero defectos críticos)
```

---

## 🛠️ 2. Matriz Detallada de Incidencias

### 🔴 INC-001: Desalineación en el Esquema de Entrada del Webhook
* **Componente:** Backend / n8n (`FLUJO B.json`)
* **Severidad:** Media (Contrato de Datos)
* **Descripción:** En la versión inicial de transición, el webhook esperaba campos anidados bajo `body.consulta.pregunta` en lugar de la convención estándar `{ "pregunta": "..." }`.
* **Causa Raíz:** Falta de estandarización en los contratos de datos entre el Frontend y el nodo de entrada del webhook.
* **Solución Aplicada por QA:** Se homologó el contrato en la colección de Postman y en los tipos de TypeScript (`nlq.types.ts`), estableciendo el campo raíz `"pregunta"`.
* **Estado:** 🟢 **Cerrada y Verificada**

---

### 🔴 INC-002: Error de Sintaxis en Expresión de Respuesta Alternativa en n8n
* **Componente:** Backend / n8n (`FLUJO B.json` — Nodo *Respond 200 sin datos1*)
* **Severidad:** Alta (Crasheo de Frontend)
* **Descripción:** Al realizar consultas sobre contaminantes o fechas sin registros históricos (ej. *ozono del último mes*), n8n devolvía un string que iniciaba con `=` (`={"ok":true...}`), lo que provocaba un error de `SyntaxError` en el cliente.
* **Causa Raíz:** Error tipográfico en el nodo de respuesta de n8n con doble signo de igual (`"responseBody": "=={{...}}"`).
* **Solución Aplicada por QA:** Se corrigió la expresión a `"responseBody": "={{...}}"` en `src/n8n-workflows/FLUJO B.json` y se re-importó el flujo en el contenedor n8n.
* **Estado:** 🟢 **Cerrada y Verificada**

---

### 🔴 INC-003: Vulnerabilidad de Renderizado en el Cliente ante Esquemas Mixtos
* **Componente:** Frontend (`nlqApi.ts` & `ChatMessageItem.tsx`)
* **Severidad:** Media (Resiliencia de UI)
* **Descripción:** El componente de chat quedaba en blanco o lanzaba error en rojo cuando la respuesta del webhook contenía formatos transicionales o respuestas informativas sin series numéricas.
* **Causa Raíz:** Validación rígida con `res.json()` sin lectura previa de buffer de texto (`res.text()`) ni soporte para esquemas sin campo `serie`.
* **Solución Aplicada por QA:** Se implementó en `nlqApi.ts` un parser defensivo que limpia el texto y se adaptó `ChatMessageItem.tsx` para renderizar tanto gráficos de Chart.js como badges informativos y respuestas de texto libre.
* **Estado:** 🟢 **Cerrada y Verificada**

---

### 🔴 INC-004: Falso Positivo de SLA por Latencia de Arranque en Frío (Cold Start)
* **Componente:** Pruebas de Integración (Postman / Newman)
* **Severidad:** Baja (Calibración de Pruebas)
* **Descripción:** En la primera ejecución contra la máquina virtual de Oracle Cloud, el tiempo de respuesta alcanzó 47 segundos debido al arranque en frío de la infraestructura, superando el límite estricto de 15 segundos.
* **Causa Raíz:** Umbral de SLA fijo e invariable entre entornos locales y remotos.
* **Solución Aplicada por QA:** Se calibró la aserción de SLA en `EcoPredict_Sprint1_Collection.json` para leer dinámicamente el `timeout_ms` del entorno (5,000 ms en local y 60,000 ms en Oracle Cloud).
* **Estado:** 🟢 **Cerrada y Verificada**

---

### 💡 MEJ-001: Inyección de Datos Históricos Multicontaminante
* **Componente:** Base de Datos (PostgreSQL — `calidad_aire`)
* **Impacto:** Alto (Experiencia de Usuario y Pruebas)
* **Descripción:** La base de datos local carecía de mediciones para ozono ($O_3$), monóxido ($CO$), dióxido de azufre ($SO_2$) y $PM10$.
* **Acción Aplicada por QA:** Se ejecutó un script SQL que inyectó **1,674 mediciones realistas** para los 6 contaminantes normativos de la OMS y MINAM en las estaciones de Campo de Marte, San Borja y Ate.
* **Estado:** 🟢 **Completada y Verificada**
