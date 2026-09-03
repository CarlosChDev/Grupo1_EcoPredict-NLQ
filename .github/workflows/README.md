# Workflows de GitHub Actions

Esta carpeta reúne las automatizaciones de integración continua, calidad, seguridad, despliegue y seguimiento del proyecto **EcoPredict & NLQ**.

## Frontend CI

- Archivo: [frontend-ci.yml](frontend-ci.yml)
- Objetivo: validar la estructura base del frontend cuando se modifican sus archivos o componentes compartidos.
- Eventos: cualquier Pull Request; `push` a `main`.
- Rutas propias:
  - `src/frontend/**`
  - `.github/workflows/frontend-ci.yml`
- Jobs:
  - `Detect relevant changes`
  - `Frontend Validation`
- Tecnologías: GitHub Actions y `dorny/paths-filter`.
- Validaciones:
  - detecta cambios relevantes del frontend o del proyecto compartido;
  - comprueba que exista `src/frontend`;
  - comprueba la disponibilidad de `src/frontend/package.json`.
- Check visible relevante: `Frontend Validation`.
- Tipo: CI de frontend; puede funcionar como Quality Gate si el Ruleset exige este check.

El workflow mantiene un check visible para cada Pull Request y ejecuta las comprobaciones del frontend cuando los cambios lo requieren.

## Validate n8n Workflows

- Archivo: [n8n-validate-ci.yml](n8n-validate-ci.yml)
- Objetivo: validar los archivos JSON que representan los workflows de n8n.
- Eventos: cualquier Pull Request; `push` a `main`.
- Rutas propias:
  - `src/n8n-workflows/**`
  - `.github/workflows/n8n-validate-ci.yml`
- Jobs:
  - `Detect relevant changes`
  - `Validate n8n JSON`
- Tecnologías: GitHub Actions, `dorny/paths-filter`, Node.js 20 y `JSON.parse`.
- Archivos revisados: todos los archivos `*.json` dentro de `src/n8n-workflows`.
- Validación ejecutada: parseo de cada JSON de workflow n8n.
- Check visible relevante: `Validate n8n JSON`.
- Tipo: CI de workflows n8n; puede funcionar como Quality Gate si el Ruleset lo exige.

Este workflow verifica que los workflows versionados de n8n tengan una estructura JSON válida antes de integrarse al proyecto.

## AI Testing CI

- Archivo: [ai-testing-ci.yml](ai-testing-ci.yml)
- Objetivo: validar activos de IA/ops y ejecutar la suite pytest.
- Eventos: cualquier Pull Request; `push` a `main`.
- Rutas propias:
  - `src/ia-ops/**`
  - `.github/workflows/ai-testing-ci.yml`
- Jobs:
  - `Detect relevant changes`
  - `AI Ops Validation`
- Tecnologías: Python 3.12 y pytest.
- Directorios obligatorios:
  - `src/ia-ops/prompts`
  - `src/ia-ops/tests`
  - `src/ia-ops/config-observability`
- Prueba ejecutada: `pytest src/ia-ops/tests -v`.
- Check visible relevante: `AI Ops Validation`.
- Tipo: CI de IA y QA de código; puede funcionar como Quality Gate si el Ruleset lo exige.

Este workflow cubre pruebas de calidad de prompts, defensas ante prompt injection, benchmark LLM y otras pruebas Python ubicadas en `src/ia-ops/tests`. Complementa a Newman: pytest valida lógica, datasets, prompts y reglas; Newman valida requests HTTP contra un servicio en ejecución.

## Newman QA CI

- Archivo: [newman-ci.yml](newman-ci.yml)
- Objetivo: ejecutar pruebas de API del webhook NLQ en un entorno temporal de CI.
- Eventos:
  - Pull Request hacia `main`;
  - `push` a `main` o `Chavez`;
  - ejecución manual mediante `workflow_dispatch`.
- Job: `Newman API Quality Gate`.
- Tecnologías: Docker Compose, PostgreSQL, n8n, curl, Node.js y Newman `6.2.1`.
- Colección utilizada: `src/ia-ops/tests/postman/eco_predict_nlq_collection.json`.
- Entorno probado:
  - PostgreSQL temporal;
  - n8n temporal;
  - webhook `POST /webhook/nlq`.
- Pasos principales:
  - verifica que la colección QA exista;
  - crea variables temporales del runner;
  - valida y levanta Docker Compose;
  - espera la salud de PostgreSQL y la disponibilidad de n8n;
  - importa y activa `FLUJO B.json`;
  - verifica el webhook NLQ;
  - instala Newman y ejecuta la colección;
  - muestra logs cuando corresponde;
  - elimina los contenedores y volúmenes temporales.
- Check visible relevante: `Newman API Quality Gate`.
- Tipo: QA de integración HTTP.

El workflow ejecuta las pruebas de API dentro de un runner temporal de GitHub Actions y no utiliza el servidor OCI como destino de pruebas.

## SAST - CodeQL

- Archivo: [sast.yml](sast.yml)
- Objetivo: realizar análisis estático de seguridad sobre el código JavaScript y TypeScript.
- Eventos:
  - Pull Request hacia `main`;
  - `push` a `main`;
  - ejecución manual mediante `workflow_dispatch`.
- Job: `CodeQL Security Analysis`.
- Tecnologías: GitHub CodeQL y acciones oficiales de CodeQL.
- Lenguaje analizado: `javascript-typescript`.
- Permisos utilizados:
  - lectura de contenidos;
  - escritura de eventos de seguridad;
  - lectura de acciones.
- Check visible relevante: `CodeQL Security Analysis` con la categoría de JavaScript/TypeScript.
- Tipo: SAST; puede funcionar como Quality Gate si el Ruleset exige este check.

CodeQL analiza el código fuente para generar resultados de seguridad que se publican en las herramientas de seguridad del repositorio.

## CD - Pre-deployment Validation

- Archivo: [cd.yml](cd.yml)
- Objetivo: validar los servicios Docker Compose antes del despliegue y desplegar `main` en OCI después de una actualización de esa rama.
- Eventos:
  - `push` a `main`;
  - ejecución manual mediante `workflow_dispatch`.
- Jobs:
  - `Validate Docker Compose services`
  - `Deploy main to OCI`
- Tecnologías: Docker Compose, PostgreSQL, n8n, SSH, npm, PM2, curl y GitHub Actions.
- Validación previa al despliegue:
  - comprueba la estructura del proyecto;
  - crea variables temporales del runner;
  - valida la configuración Compose;
  - levanta PostgreSQL y n8n temporalmente;
  - verifica PostgreSQL healthy;
  - verifica el endpoint de readiness de n8n;
  - elimina los servicios temporales.
- Despliegue OCI:
  - se ejecuta exclusivamente después de un `push` a `main`;
  - utiliza los secretos SSH configurados en GitHub;
  - sincroniza la rama `main` en el servidor;
  - instala dependencias reproducibles del frontend con `npm ci`;
  - reinicia el frontend administrado por PM2;
  - levanta los servicios Compose;
  - verifica PostgreSQL, n8n y el frontend.
- Check visible relevante: `Validate Docker Compose services` y `Deploy main to OCI`.
- Tipo: CD y validación previa al despliegue.

La ejecución manual permite comprobar la validación de Compose. El despliegue se reserva para actualizaciones que llegan a `main`.

## Relación general

```text
Pull Request o push
        ↓
Frontend CI · n8n Validate CI · AI Testing CI · Newman QA CI · SAST - CodeQL
        ↓
Checks de GitHub Actions
        ↓
Ruleset de main, cuando un check está configurado como obligatorio
        ↓
Merge o push a main
        ↓
CD - Pre-deployment Validation
        ↓
Despliegue OCI
```

Los workflows de CI, QA y SAST producen checks. El Ruleset de GitHub determina cuáles de esos checks deben completarse para permitir la integración de cambios hacia `main`.
