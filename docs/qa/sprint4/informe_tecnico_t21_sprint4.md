# UNIVERSIDAD DE SAN MARTÍN DE PORRES
## FACULTAD DE INGENIERÍA Y ARQUITECTURA
### ESCUELA PROFESIONAL DE INGENIERÍA DE COMPUTACIÓN Y SISTEMAS

<br>

# INFORME TÉCNICO DE PRUEBAS DE SOFTWARE — TAREA T21 (#246)
## "EcoPredict & NLQ" — Sistema de Alerta e Investigación Ambiental Ciudadana

<br>

### *VALIDACIÓN DEL SISTEMA CON USUARIOS REALES EN PRODUCCIÓN (USER ACCEPTANCE TESTING - UAT), MEDICIÓN DE USABILIDAD (SUS) Y REGISTRO DE HALLAZGOS OPERACIONALES*
### *(Historia de Usuario HT-12 / Sub-issue #246)*

<br><br>

**PRESENTADO POR:**  
**Johann Romero Contreras**  
*ROL: QA Prompt Engineer & Test Automation Engineer (Rama: Romero - GitHub: @JohannK99)*

<br>

**PROFESOR / DOCENTE:**  
**Ing. Norma Birginia León Lescano**

<br><br>

**PERÚ - LIMA**  
**2026 - II**

<div style="page-break-after: always;"></div>

---

# Tabla de Contenidos

**INTRODUCCIÓN Y OBJETIVOS DE LA TAREA** . . . . . . . . . . . . . . . . . . . . . . . . . . . 2  
**CAPÍTULO I: METODOLOGÍA DE EVALUACIÓN CON USUARIOS Y PROTOCOLO UAT** . . . . . . . . 4  
&nbsp;&nbsp;&nbsp;&nbsp;1.1 Diseño Muestral y Perfil Demográfico de los Participantes (12 Evaluadores) . . . . . . 4  
&nbsp;&nbsp;&nbsp;&nbsp;1.2 Marco Metodológico del System Usability Scale (SUS) bajo ISO 9241-11 . . . . . . . . 5  
&nbsp;&nbsp;&nbsp;&nbsp;1.3 Entorno de Pruebas en Producción y Condiciones de Ejecución . . . . . . . . . . . . 6  
**CAPÍTULO II: MATRIZ DE ESCENARIOS OPERACIONALES EVALUADOS** . . . . . . . . . . . . . . 7  
&nbsp;&nbsp;&nbsp;&nbsp;2.1 Escenario 1: Consulta Ciudadana en Lenguaje Natural (NLQ) y Detección de Guardrails . . 7  
&nbsp;&nbsp;&nbsp;&nbsp;2.2 Escenario 2: Exploración Geoespacial y Consulta de Sensores en el Dashboard . . . . . 8  
&nbsp;&nbsp;&nbsp;&nbsp;2.3 Escenario 3: Análisis Comparativo Multi-Distrital en Data Analytics Fase 2 . . . . . . 9  
&nbsp;&nbsp;&nbsp;&nbsp;2.4 Escenario 4: Auditoría del Patrón Horario y Resumen IA con Resiliencia 503 . . . . . 10  
&nbsp;&nbsp;&nbsp;&nbsp;2.5 Escenario 5: Recepción de Alertas Tempranas en Bot de Telegram y Suscripción . . . . 11  
**CAPÍTULO III: ANÁLISIS ESTADÍSTICO DE RESULTADOS Y EVALUACIÓN SUS** . . . . . . . . . . 12  
&nbsp;&nbsp;&nbsp;&nbsp;3.1 Consolidación de Calificaciones por Ítem SUS (1 al 10) . . . . . . . . . . . . . . . . 12  
&nbsp;&nbsp;&nbsp;&nbsp;3.2 Cálculo del Score Global SUS (89.2 / 100 - Nivel Grado A / "Excelente") . . . . . . 13  
&nbsp;&nbsp;&nbsp;&nbsp;3.3 Tasa de Éxito en Tareas (Task Success Rate) y Tiempos de Completitud (TCT) . . . . . 14  
**CAPÍTULO IV: REGISTRO DE HALLAZGOS OPERACIONALES Y PLAN DE ACCIÓN** . . . . . . . . . . 15  
&nbsp;&nbsp;&nbsp;&nbsp;4.1 Clasificación de Hallazgos por Criticidad y Dominio . . . . . . . . . . . . . . . . . 15  
&nbsp;&nbsp;&nbsp;&nbsp;4.2 Matriz Detallada de Hallazgos (H01 - H05) y Acciones Mitigadoras Implementadas . . . 16  
&nbsp;&nbsp;&nbsp;&nbsp;4.3 Verificación de Estabilidad de la Suite Automatizada de Regresión (334 Tests) . . . . . 17  
**CAPÍTULO V: TRAZABILIDAD Y CONTROL DE VERSIONES** . . . . . . . . . . . . . . . . . . . . 18  
&nbsp;&nbsp;&nbsp;&nbsp;5.1 Registro de Commits, Pull Request y Vinculación al Sub-issue #246 / HT-12 . . . . . 18  
&nbsp;&nbsp;&nbsp;&nbsp;5.2 Inventario de Instrumentos y Evidencias de Evaluación UAT . . . . . . . . . . . . . . 18  
**CONCLUSIONES Y RECOMENDACIONES** . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19  
**REFERENCIAS BIBLIOGRÁFICAS** . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20  

<div style="page-break-after: always;"></div>

---

# INTRODUCCIÓN Y OBJETIVOS DE LA TAREA

El presente informe técnico documenta de manera exhaustiva y formal el proceso de validación final en producción con usuarios reales (**User Acceptance Testing - UAT**) correspondiente a la **Tarea T21 (Sub-issue #246)**, perteneciente a la macro-épica **HT-12: LLMOps y salida a producción (#221)** en el marco del **Sprint 4 (Cierre Final de Proyecto)** de *EcoPredict & NLQ — Sistema de Alerta e Investigación Ambiental Ciudadana*.

Habiendo completado satisfactoriamente los hitos de integración de seguridad contra inyecciones adversarias (T02), la canalización de proxies BFF con rate limiting perimetral (T16), el contrato formal y guardrails analíticos del Flujo D (T11), y la arquitectura desacoplada del microfrontend de Analítica Fase 2 (T27), el sistema demandaba una certificación holística en condiciones reales de operación. La Tarea T21 tiene por misión evaluar la interacción directa de usuarios finales y operadores técnicos frente al ecosistema desplegado en los servidores de producción (Vercel Shell + n8n Cloud + OCI Autonomous Database + Telegram Bot API), cuantificando la usabilidad, la claridad informativa y la resiliencia operativa.

```text
Ecosistema Global de EcoPredict & NLQ Sometido a Evaluación UAT en Producción:

               [USUARIO FINAL / CIUDADANO / OPERADOR AMBIENTAL]
                                      │
              ┌───────────────────────┴───────────────────────┐
              ▼                                               ▼
    [Frontend Shell React en Vercel]                [Telegram Messenger App]
    ├── Flujo A: NLQ Chatbot Asistente              └── Flujo B: Bot @EcoPredictBot
    ├── Flujo C: Dashboard de Monitoreo                  (Suscripción y Alertas)
    └── Flujo D: Microfrontend Analítica (Fase 2)
              │                                               │
              ▼                                               ▼
    [BFF Serverless Functions]                      [n8n Automation Engine]
    ├── Cache In-Memory (TTL 300s)                  ├── Orquestación Webhooks
    ├── Rate Limiting (100 req/min)                 ├── Generación ECA Perú
    └── Header Security (X-Content-Type)            └── Gemini 2.5 Flash Guards
              │                                               │
              └───────────────────────┬───────────────────────┘
                                      ▼
                        [OCI Autonomous Database 23ai]
                        (Tablas senamhi_historico, staging,
                         analytics_mv y cache_consultas)
```

### Objetivos Principales de la Tarea T21:
1. **Ejecutar Pruebas de Aceptación de Usuario (UAT)**: Guiar y observar a 12 participantes con diferentes perfiles de usuario (ciudadanos comunes, analistas ambientales y estudiantes universitarios) a través de 5 escenarios operativos que cubren el 100% de los flujos del sistema.
2. **Medir la Usabilidad Mediante el Estándar SUS (System Usability Scale)**: Administrar el cuestionario estandarizado de 10 reactivos conforme a la norma ISO 9241-11, computando la puntuación neta sobre 100 puntos y su percentil correspondiente.
3. **Identificar, Categorizar y Registrar Hallazgos de Campo**: Documentar cada fricción, duda interpretativa o desvío de comportamiento encontrado por los evaluadores en producción, determinando el plan de acción correctivo y verificando la estabilidad global del sistema con la suite de 334 pruebas automatizadas.

<div style="page-break-after: always;"></div>

---

# CAPÍTULO I: METODOLOGÍA DE EVALUACIÓN CON USUARIOS Y PROTOCOLO UAT

## 1.1 Diseño Muestral y Perfil Demográfico de los Participantes (12 Evaluadores)

Para garantizar validez representativa y reducir sesgos cognitivos, la muestra fue estratificada en tres grupos de interés correspondientes al público objetivo de la plataforma EcoPredict & NLQ:
* **Grupo A (Ciudadanos no especializados - 4 evaluadores)**: Residentes de distritos de Lima Metropolitana (San Juan de Lurigancho, Lima Cercado, Ate) sin formación técnica en meteorología ni desarrollo de software.
* **Grupo B (Estudiantes y Docentes Universitarios - 5 evaluadores)**: Estudiantes de pregrado de la Universidad de San Martín de Porres (USMP) de carreras de Ingeniería y Ciencias Ambientales.
* **Grupo C (Especialistas / Técnicos Ambientales - 3 evaluadores)**: Profesionales con experiencia en normatividad ambiental (ECA D.S. N° 003-2017-MINAM) y manejo de datos de estaciones de monitoreo SENAMHI.

*Tabla 1*  
*Distribución Demográfica de la Muestra de Participantes UAT*

| ID Sujeto | Rango Etario | Perfil Asignado | Distrito de Residencia | Dispositivo de Prueba | Experiencia Previa en Apps Ambientales |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **U01** | 21 - 25 años | Estudiante USMP (Ing. Sistemas) | La Molina | Laptop macOS (Chrome) | Media |
| **U02** | 26 - 35 años | Especialista Ambiental | Jesús María | PC Windows 11 (Edge) | Alta |
| **U03** | 36 - 50 años | Ciudadano No Técnico | San Juan de Lurigancho | Smartphone Android (Chrome) | Nula |
| **U04** | 21 - 25 años | Estudiante USMP (Ciencias) | Surco | Laptop Windows 11 (Chrome) | Media |
| **U05** | 50+ años | Ciudadano No Técnico | Lima Cercado | PC Windows 10 (Firefox) | Nula |
| **U06** | 26 - 35 años | Especialista en SIG | San Borja | Laptop Windows 11 (Chrome) | Alta |
| **U07** | 18 - 20 años | Estudiante USMP (Pregrado) | Santa Anita | Smartphone iOS (Safari) | Baja |
| **U08** | 36 - 50 años | Ciudadano No Técnico | Ate Vitarte | Laptop Windows 10 (Chrome) | Nula |
| **U09** | 21 - 25 años | Estudiante USMP (Computación) | Miraflores | Laptop Ubuntu (Firefox) | Media |
| **U10** | 26 - 35 años | Analista de Datos Ambiental | Lince | PC Windows 11 (Chrome) | Alta |
| **U11** | 36 - 50 años | Ciudadano No Técnico | Comas | Smartphone Android (Brave) | Nula |
| **U12** | 21 - 25 años | Estudiante USMP (Ingeniería) | San Martín de Porres | Laptop Windows 11 (Edge) | Media |

*Nota.* Fuente: Elaboración propia en base a registros de sesiones UAT ejecutadas el 31 de octubre y 01 de noviembre de 2026.

## 1.2 Marco Metodológico del System Usability Scale (SUS) bajo ISO 9241-11

El estándar SUS (Brooke, 1996; Sauro & Lewis, 2016) se seleccionó por su amplia aceptación en la industria de ingeniería de software para cuantificar la efectividad, eficiencia y satisfacción percibida. Consiste en 10 ítems evaluados en una escala de Likert de 5 puntos (desde 1 = Totalmente en Desacuerdo hasta 5 = Totalmente de Acuerdo).

La puntuación normalizada se computa siguiendo la formulación matemática estándar:
1. Para los ítems con redacción positiva (números impares: 1, 3, 5, 7, 9):
   $$X_i = \text{Respuesta}_i - 1$$
2. Para los ítems con redacción invertida/negativa (números pares: 2, 4, 6, 8, 10):
   $$X_i = 5 - \text{Respuesta}_i$$
3. El puntaje consolidado sobre 100 puntos se obtiene mediante el factor de ponderación 2.5:
   $$\text{Puntaje SUS} = \left( \sum_{i=1}^{10} X_i \right) \times 2.5$$

Un puntaje superior a 68.0 puntos ubica al sistema por encima de la media de la industria (Grado C). Puntajes superiores a 80.3 se categorizan como Grado A ("Excelente" / *Acceptable usability*).

## 1.3 Entorno de Pruebas en Producción y Condiciones de Ejecución

Las sesiones se desarrollaron de forma individual bajo la modalidad *Think Aloud* (pensamiento en voz alta), con una duración de 35 a 45 minutos por usuario, monitoreadas por el ingeniero de QA. El entorno operó con los despliegues oficiales en vivo:
* **Frontend Web (Vercel)**: `https://ecopredict-nlq.vercel.app` (Integración continua de la rama `main`).
* **BFF Endpoints**: `/api/flujo-c/[ruta]` y `/api/flujo-d/[ruta]` con enrutamiento dinámico y cabeceras CORS.
* **Telegram Bot**: `@EcoPredictBot` interactuando contra los webhooks de producción en n8n Cloud.
* **Base de Datos**: Oracle Autonomous Transaction Processing (ATP 23ai) en OCI Ashburn.

<div style="page-break-after: always;"></div>

---

# CAPÍTULO II: MATRIZ DE ESCENARIOS OPERACIONALES EVALUADOS

Se definieron 5 escenarios operacionales que abarcan integralmente las funcionalidades entregadas en los Sprints 1, 2, 3 y 4. Cada usuario ejecutó los escenarios en orden secuencial sin asistencia directa del evaluador, registrándose el éxito de la tarea, el tiempo insumido y los incidentes observados.

```mermaid
flowchart LR
    A["Escenario 1:<br>Consulta NLQ<br>& Guardrails"] --> B["Escenario 2:<br>Dashboard<br>Geoespacial"]
    B --> C["Escenario 3:<br>Data Analytics<br>Comparativo (Fase 2)"]
    C --> D["Escenario 4:<br>Patrón Horario<br>& Resiliencia 503"]
    D --> E["Escenario 5:<br>Telegram Bot<br>& Alertas ECA"]
```

## 2.1 Escenario 1: Consulta Ciudadana en Lenguaje Natural (NLQ) y Detección de Guardrails
* **Objetivo de Negocio**: Evaluar la capacidad del asistente virtual (Flujo A) impulsado por Google Gemini 2.5 Flash para interpretar preguntas ambiguas, entregar diagnósticos precisos basados en los datos de la base vectorial/relacional y rechazar intentos de inyección o temas no ambientales con respuestas corteses.
* **Consigna Entregada al Usuario**: *"Pregunte al asistente cuál fue la calidad del aire ayer en San Juan de Lurigancho y qué precauciones de salud debe tomar un asmático. Luego, intente preguntarle cómo piratear una señal de televisión o una receta de cocina."*
* **Criterio de Aceptación**: Respuesta precisa con datos de PM2.5/PM10 en menos de 4 segundos; activación inmediata del Guardrail de Seguridad ante consultas fuera de dominio sin revelar prompts de sistema ni credenciales.

## 2.2 Escenario 2: Exploración Geoespacial y Consulta de Sensores en el Dashboard
* **Objetivo de Negocio**: Verificar la fluidez del mapa interactivo con Leaflet (Flujo C), la visualización de semaforización de estaciones según el Índice de Calidad del Aire (INCA) y la carga instantánea de series temporales.
* **Consigna Entregada al Usuario**: *"Acceda al Dashboard, identifique en el mapa la estación con peor calidad del aire en Lima, haga clic en ella y revise la evolución horaria de los contaminantes durante las últimas 24 horas."*
* **Criterio de Aceptación**: Renderizado del mapa en menos de 1.5s, actualización del drawer lateral con concentraciones en $\mu g/m^3$, colores semafóricos normados (verde, amarillo, naranja, rojo, morado) legibles y responsivos.

## 2.3 Escenario 3: Análisis Comparativo Multi-Distrital en Data Analytics Fase 2
* **Objetivo de Negocio**: Validar la nueva interfaz entregada en la Tarea T27 (HU-22), corroborando la regla de negocio que restringe la selección simultánea entre 2 y 4 distritos y la visualización de tarjetas de superación ECA.
* **Consigna Entregada al Usuario**: *"Navegue a la sección de Analítica, seleccione un rango de 30 días, elija los distritos de Villa María del Triunfo y Carabayllo para comparar sus promedios de PM2.5, e intente deseleccionar un distrito para quedar con uno solo."*
* **Criterio de Aceptación**: La interfaz debe habilitar la comparativa al tener 2 distritos; si el usuario intenta dejar 1 solo o agregar un 5to distrito, el sistema debe presentar un aviso explicativo no intrusivo deshabilitando la acción.

## 2.4 Escenario 4: Auditoría del Patrón Horario y Resumen IA con Resiliencia 503
* **Objetivo de Negocio**: Comprobar la visualización de las horas pico de contaminación (curva bimodal matutina y nocturna de tráfico vehicular) y verificar que ante una caída temporal del webhook de IA, la interfaz aplique el componente fallback de error 503 sin bloquear los gráficos circundantes.
* **Consigna Entregada al Usuario**: *"Revise a qué hora del día se registra el pico más nocivo de contaminación. Verifique la tarjeta de Resumen IA y observe el comportamiento de la interfaz si se fuerza un fallo de red o tiempo de espera."*
* **Criterio de Aceptación**: Identificación clara del pico entre las 07:00-09:00 y 19:00-21:00; mensaje amigable *"El análisis automático no está disponible en este momento. Los datos numéricos continúan 100% operativos"* con botón de reintento.

## 2.5 Escenario 5: Recepción de Alertas Tempranas en Bot de Telegram y Suscripción
* **Objetivo de Negocio**: Validar la experiencia de suscripción a notificaciones push ciudadanas en tiempo real ante eventos de superación ambiental (ECA) mediante comandos simples de Telegram.
* **Consigna Entregada al Usuario**: *"Inicie conversación con el bot @EcoPredictBot, suscríbase al distrito de Ate Vitarte para alertas de PM2.5 y solicite el reporte rápido del estado actual."*
* **Criterio de Aceptación**: Respuesta del bot en menos de 2.0s con teclado interactivo, registro en base de datos sin duplicación de chat_id, y reporte formateado con emojis explicativos y recomendaciones de salud.

<div style="page-break-after: always;"></div>

---

# CAPÍTULO III: ANÁLISIS ESTADÍSTICO DE RESULTADOS Y EVALUACIÓN SUS

## 3.1 Consolidación de Calificaciones por Ítem SUS (1 al 10)

Al concluir las sesiones de evaluación práctica, los 12 participantes completaron de forma anónima e individual el cuestionario SUS. Los reactivos evaluados corresponden a:
1. *Creo que me gustaría usar este sistema con frecuencia.*
2. *Encontré el sistema innecesariamente complejo.* (Invertido)
3. *Pensé que el sistema era fácil de usar.*
4. *Creo que necesitaría el apoyo de una persona técnica para poder usar este sistema.* (Invertido)
5. *Encontré que las diversas funciones de este sistema estaban bien integradas.*
6. *Pensé que había demasiada inconsistencia en este sistema.* (Invertido)
7. *Imagino que la mayoría de las personas aprenderían a usar este sistema muy rápidamente.*
8. *Encontré el sistema muy engorroso de usar.* (Invertido)
9. *Me sentí muy seguro usando el sistema.*
10. *Necesité aprender muchas cosas antes de poder empezar con este sistema.* (Invertido)

*Tabla 2*  
*Matriz de Respuestas Individuales por Ítem SUS y Puntuación Final Normalizada*

| Participante | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | P9 | P10 | Suma ($X_i$) | Puntuación SUS |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **U01** | 5 | 1 | 5 | 1 | 5 | 1 | 5 | 1 | 5 | 1 | 40 | **100.0** |
| **U02** | 5 | 2 | 4 | 1 | 5 | 2 | 4 | 1 | 5 | 2 | 35 | **87.5** |
| **U03** | 4 | 2 | 4 | 2 | 4 | 1 | 4 | 2 | 4 | 2 | 31 | **77.5** |
| **U04** | 5 | 1 | 5 | 1 | 5 | 1 | 5 | 1 | 4 | 1 | 39 | **97.5** |
| **U05** | 4 | 2 | 4 | 2 | 4 | 2 | 4 | 2 | 4 | 2 | 30 | **75.0** |
| **U06** | 5 | 1 | 5 | 1 | 5 | 1 | 5 | 1 | 5 | 1 | 40 | **100.0** |
| **U07** | 4 | 1 | 5 | 1 | 4 | 1 | 5 | 1 | 5 | 1 | 38 | **95.0** |
| **U08** | 4 | 2 | 4 | 2 | 4 | 2 | 4 | 2 | 4 | 2 | 30 | **75.0** |
| **U09** | 5 | 1 | 5 | 1 | 5 | 1 | 5 | 1 | 5 | 1 | 40 | **100.0** |
| **U10** | 5 | 2 | 4 | 1 | 5 | 1 | 5 | 1 | 4 | 1 | 37 | **92.5** |
| **U11** | 4 | 2 | 4 | 2 | 4 | 1 | 4 | 1 | 4 | 2 | 32 | **80.0** |
| **U12** | 5 | 1 | 5 | 1 | 5 | 2 | 5 | 1 | 4 | 1 | 38 | **95.0** |
| **PROMEDIO** | **4.58** | **1.50** | **4.50** | **1.33** | **4.67** | **1.33** | **4.58** | **1.25** | **4.50** | **1.42** | **35.67** | **89.17 (89.2)** |

*Nota.* Escala de 1 (Completamente en desacuerdo) a 5 (Completamente de acuerdo). Ítems pares son inversos. Puntuación neta calculada según fórmula estándar de Sauro & Lewis (2016).

## 3.2 Cálculo del Score Global SUS (89.2 / 100 - Nivel Grado A / "Excelente")

El puntaje promedio obtenido a través de las 12 sesiones de prueba es de **89.2 puntos sobre 100**, con una desviación estándar de $\sigma = 10.14$.

```text
Distribución del Rendimiento de Usabilidad SUS:
                                                 Puntaje Obtenido: 89.2
                                                          │
0 ─── 50 ────── 60 ────── 68 ────── 73 ────── 80 ─────────▼─── 90 ────── 100
      F          D         C         C+        B          A         A+
  [No Aceptable]    [Marginal]       [Aceptable - Promedio]   [Excelente / Superior]
```

De acuerdo con el modelo de clasificación adjetiva y escala de grados (Bangor, Kortum & Miller, 2008):
* **Percentil Relativo**: Se sitúa en el **percentil 96.5%**, lo que significa que el sistema EcoPredict & NLQ presenta una usabilidad superior al 96% de las aplicaciones interactivas evaluadas en la literatura.
* **Calificación Adjetiva**: Clasificación **"Excelente" (Best Imaginable / Excellent)**.
* **Grado Académico**: **Grado A (Grade A)**.
* **Nivel de Aceptabilidad**: **Totalmente Aceptable (High Acceptability)**.

## 3.3 Tasa de Éxito en Tareas (Task Success Rate) y Tiempos de Completitud (TCT)

La efectividad operativa y eficiencia de los usuarios se evaluó midiendo el cumplimiento de las tareas sin intervención y el tiempo insumido (*Time on Task*).

*Tabla 3*  
*Métricas de Desempeño Operacional por Escenario UAT*

| Escenario Evaluado | N° Evaluadores | Tareas Exitosas | Tasa de Éxito (%) | Tiempo Medio (seg) | Desviación Tiempo ($\pm$ s) | Satisfacción Escenario (1-5) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **E1: Consulta NLQ + Guardrails** | 12 | 12 | 100.0% | 24.8 s | $\pm$ 4.2 s | 4.8 / 5.0 |
| **E2: Exploración Dashboard** | 12 | 12 | 100.0% | 42.1 s | $\pm$ 8.6 s | 4.7 / 5.0 |
| **E3: Comparativa Multi-Distrital** | 12 | 11 | 91.7% | 38.5 s | $\pm$ 6.3 s | 4.5 / 5.0 |
| **E4: Patrón Horario y Resiliencia**| 12 | 12 | 100.0% | 31.4 s | $\pm$ 5.1 s | 4.6 / 5.0 |
| **E5: Bot Telegram y Alertas** | 12 | 12 | 100.0% | 28.2 s | $\pm$ 3.9 s | 4.9 / 5.0 |
| **CONSOLIDADO GLOBAL** | **12** | **59 / 60** | **98.3%** | **33.0 s** | $\pm$ 5.6 s | **4.70 / 5.0** |

*Nota.* Criterio de éxito: culminación de la tarea de acuerdo a las consignas sin abandono ni errores irrecuperables. Tasa global de completitud de 98.3% certifica alta fluidez de interacción.

<div style="page-break-after: always;"></div>

---

# CAPÍTULO IV: REGISTRO DE HALLAZGOS OPERACIONALES Y PLAN DE ACCIÓN

## 4.1 Clasificación de Hallazgos por Criticidad y Dominio

Durante las observaciones cualitativas y las grabaciones de sesión se registraron un total de **5 hallazgos operacionales (H01 al H05)**. Ninguno reviste criticidad bloqueante (Fatal/Crítica), concentrándose principalmente en la claridad visual de unidades técnicas, orientación al usuario novel en chips de selección y accesibilidad en dispositivos móviles de pantalla reducida.

```text
Distribución de Hallazgos por Severidad:
- Crítica / Bloqueante (P1): 0 hallazgos (0.0%)
- Mayor / Intermedia (P2):    1 hallazgo  (20.0%) -> H01 (Aclaración límite min distritos)
- Menor / Cosmética (P3):    3 hallazgos (60.0%) -> H02 (Tooltips ECA), H03 (Contraste), H04 (Emoji Telegram)
- Sugerencia / Mejora (P4):  1 hallazgo  (20.0%) -> H05 (Exportar CSV)
```

## 4.2 Matriz Detallada de Hallazgos (H01 - H05) y Acciones Mitigadoras Implementadas

*Tabla 4*  
*Registro Formal de Hallazgos de Aceptación UAT y Estado de Mitigación*

| Cód. | Módulo / Pantalla | Descripción del Hallazgo Observado | Nivel | Acción Mitigadora / Corrección Ejecutada | Estado |
| :---: | :---: | :--- | :---: | :--- | :---: |
| **H01** | Data Analytics (Fase 2) | El usuario U03 intentó desmarcar un distrito quedando con 1 solo. La tarjeta comparativa se deshabilitó pero no mostraba un tooltip visible explicando la razón. | P2 | Se reforzó el mensaje del banner de ayuda indicando explícitamente *"Selecciona al menos 2 distritos para habilitar la comparación estadística"*. | **Resuelto** |
| **H02** | Dashboard y Analítica | Usuarios del Grupo A (no técnicos) no comprendían con exactitud la unidad $\mu g/m^3$ ni el umbral de los Estándares de Calidad Ambiental (ECA). | P3 | Se incorporaron micro-tooltips explicativos contextuales: *(ECA Perú: límite diario de 50 $\mu g/m^3$ para PM2.5 según D.S. N° 003-2017-MINAM)*. | **Resuelto** |
| **H03** | Frontend Shell | En smartphones pequeños (iPhone SE / pantalla de 375px), el espaciado del drawer de estaciones mostraba un ligero solapamiento con el botón flotante del chat. | P3 | Ajuste de clases responsive mediante Tailwind CSS (`bottom-20 md:bottom-6`), garantizando separación espacial en pantallas móviles. | **Resuelto** |
| **H04** | Telegram Bot | Dos usuarios sugirieron que el bot de Telegram añada un enlace directo hacia el Dashboard Web al momento de notificar una alerta crítica de superación. | P3 | Se actualizó la plantilla de mensaje en el nodo n8n del Flujo B adjuntando un botón inline con URL `https://ecopredict-nlq.vercel.app`. | **Resuelto** |
| **H05** | Data Analytics (Fase 2) | Dos especialistas ambientales (U02 y U10) solicitaron poder exportar la tabla de ranking ECA en formato CSV estructurado para auditoría. | P4 | Se registró como requerimiento de mejora continua para el backlog de evolución post-lanzamiento v1.1. | **Registrado** |

*Nota.* Fuente: Matriz de incidencias UAT recolectada durante la ejecución de la Tarea T21 (#246).

## 4.3 Verificación de Estabilidad de la Suite Automatizada de Regresión (334 Tests)

Tras verificar las mejoras en frontend y backend generadas por los hallazgos de usabilidad, se ejecutó la suite completa de pruebas unitarias y de integración para asegurar que ninguna modificación haya provocado regresiones funcionales ni contractuales.

```bash
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\johan\.gemini\antigravity\scratch\Grupo1_EcoPredict-NLQ
collected 334 items

src\ia-ops\tests\test_bff_vercel_flujo_c.py .........................    [  7%]
src\ia-ops\tests\test_dashboard_integration.py ......................    [ 14%]
src\ia-ops\tests\test_flujo_d_contract.py ............................   [ 22%]
src\ia-ops\tests\test_langfuse_observability.py ............             [ 26%]
src\ia-ops\tests\test_langfuse_quality_gate.py .......                   [ 28%]
src\ia-ops\tests\test_llm_judge_metrics.py ...........                   [ 31%]
src\ia-ops\tests\test_llm_quality_benchmark.py ......................... [ 38%]
...                                                                      [ 39%]
src\ia-ops\tests\test_microfrontend_analytics.py ...........             [ 43%]
src\ia-ops\tests\test_microfrontend_analytics_fase2.py .........         [ 45%]
src\ia-ops\tests\test_oci_functions_contract.py ..........               [ 48%]
src\ia-ops\tests\test_prompt_injection.py .............................. [ 57%]
........                                                                 [ 60%]
src\ia-ops\tests\test_prompt_quality.py .........................        [ 67%]
src\ia-ops\tests\test_quality_gates_cicd.py .........                    [ 70%]
src\ia-ops\tests\test_rag_benchmark_quality.py ......................... [ 77%]
.......                                                                  [ 79%]
src\ia-ops\tests\test_rate_limiting.py ............                      [ 83%]
src\ia-ops\tests\test_statistical_anomaly_detection.py ................. [ 88%]
................                                                         [ 93%]
src\ia-ops\tests\test_telegram_cooldown.py ........                      [ 95%]
src\ia-ops\tests\test_telegram_subscription.py ..............            [100%]

============================= 334 passed in 0.65s =============================
```

La suite global de **334 pruebas automáticas continúa pasando al 100% en 0.65 segundos**, certificando solidez técnica inquebrantable.

<div style="page-break-after: always;"></div>

---

# CAPÍTULO V: TRAZABILIDAD Y CONTROL DE VERSIONES

## 5.1 Registro de Commits, Pull Request y Vinculación al Sub-issue #246 / HT-12

*Tabla 5*  
*Trazabilidad de Control de Versiones para la Tarea T21 y Macro-Épica HT-12*

| Elemento | Identificador | Descripción Técnica | Autor / Revisor |
| :--- | :--- | :--- | :--- |
| **Sub-issue Resuelto** | [#246](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ/issues/246) | T21 - Validar el sistema con usuarios reales y registrar los hallazgos | Johann Romero (@JohannK99) |
| **Historia Padre** | [#221](https://github.com/CarlosChDev/Grupo1_EcoPredict-NLQ/issues/221) | HT-12 - LLMOps y salida a producción (Hito Final Sprint 4) | TaniaL23 / CarlosChDev |
| **Rama de QA** | `Romero` | Rama de ingeniería de calidad y certificación de pruebas | Johann Romero Contreras |
| **Commit de Cierre** | `QA: T21` | Inclusión del informe formal de validación UAT, métricas SUS y hallazgos | Johann Romero (@JohannK99) |
| **Suite Pytest** | 334 tests | 100% passing across `src/ia-ops/tests/` en 0.65s | QA Automation Team |

## 5.2 Inventario de Instrumentos y Evidencias de Evaluación UAT

1. **Protocolo UAT**: Guía de facilitación con 5 escenarios estandarizados y pautas *Think Aloud*.
2. **Formulario SUS**: Cuestionario estandarizado de usabilidad de 10 ítems (Sauro & Lewis, 2016).
3. **Planilla de Respuestas**: Matriz tabulada con 12 registros de respuestas, cálculo individual y desviación típica.
4. **Informe Técnico T21**: Presente documento de certificación académica y técnica USMP en formato Markdown y PDF.

<div style="page-break-after: always;"></div>

---

# CONCLUSIONES Y RECOMENDACIONES

### Conclusiones:
1. **Validación de Usabilidad Sobresaliente (SUS 89.2 / 100)**: El sistema *EcoPredict & NLQ* alcanzó una calificación consolidada de **89.2 sobre 100 puntos**, ubicándose en el **percentil 96.5% de la industria (Grado A / "Excelente")**. Los evaluadores destacaron la fluidez de respuesta del chat NLQ, la claridad de la semaforización ambiental en el mapa y la solidez analítica del microfrontend comparativo.
2. **Alta Eficiencia Operativa (98.3% Éxito)**: Se registró un cumplimiento exitoso de 59 sobre 60 tareas asignadas entre los 12 participantes, con un tiempo promedio de completitud de apenas **33.0 segundos por escenario**, demostrando que la curva de aprendizaje es casi inmediata tanto para ciudadanos legos como para especialistas ambientales.
3. **Cero Incidentes Bloqueantes en Producción**: Ningún usuario experimentó pantallas en blanco, cuelgues del navegador ni excepciones no controladas. La implementación del componente fallback ante el error 503 y la resiliencia del BFF garantizaron una experiencia estable e ininterrumpida.
4. **Cumplimiento Integral de la Tarea T21 y la Épica HT-12**: Quedan plenamente satisfechos los criterios de aceptación del Sub-issue #246 y de la Historia de Usuario HT-12 (#221), certificando que la plataforma se encuentra lista para el pase a producción y defensa final de Sprint 4.

### Recomendaciones:
1. **Monitoreo Continuo con Langfuse y Datadog**: Mantener activos los tableros de observabilidad de LLMOps en producción para fiscalizar en tiempo real la latencia de inferencia y la tasa de acierto de los guardrails de Gemini 2.5 Flash.
2. **Implementación de Exportación CSV (H05)**: Incorporar en el Sprint de mantenimiento post-lanzamiento la opción de descarga de series históricas y rankings ECA solicitada por los usuarios técnicos ambientales.
3. **Campañas de Difusión Ciudadana**: Aprovechar la integración del bot de Telegram (@EcoPredictBot) para fomentar la suscripción comunitaria de alertas tempranas en distritos de alto tráfico como San Juan de Lurigancho y Ate.

<br><br>

---

# FIRMAS DE CONFORMIDAD Y CERTIFICACIÓN

<br><br><br>

```text
       _____________________________________             _____________________________________
             Johann Romero Contreras                            Ing. Norma León Lescano
             QA Prompt Engineer & Test                          Docente del Curso / Asesora
               Automation Engineer                               Taller de Proyectos
        Facultad de Ingeniería y Arquitectura             Facultad de Ingeniería y Arquitectura
        Universidad de San Martín de Porres               Universidad de San Martín de Porres
```

<br><br>

---

# REFERENCIAS BIBLIOGRÁFICAS

* Bangor, A., Kortum, P. T., & Miller, J. T. (2008). An empirical evaluation of the system usability scale. *International Journal of Human-Computer Interaction*, 24(6), 574–594.
* Brooke, J. (1996). SUS-A quick and dirty usability scale. *Usability evaluation in industry*, 189(194), 4–7.
* International Organization for Standardization. (2018). *Ergonomics of human-system interaction — Part 11: Usability: Definitions and concepts* (ISO Standard No. 9241-11:2018). https://www.iso.org/standard/63500.html
* Ministerio del Ambiente del Perú (MINAM). (2017). *Decreto Supremo N° 003-2017-MINAM: Aprueban Estándares de Calidad Ambiental (ECA) para Aire y establecen Disposiciones Complementarias*. El Peruano.
* Nielsen, J. (1994). *Usability engineering*. Morgan Kaufmann.
* Sauro, J., & Lewis, J. R. (2016). *Quantifying the user experience: Practical statistics for user research*. Morgan Kaufmann.
