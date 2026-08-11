\# EcoPredict \& NLQ



\*\*Sistema de Alerta e Investigación Ambiental Ciudadana\*\*



EcoPredict \& NLQ es un sistema orientado al análisis de información ambiental mediante \*\*Open Data, automatización, Inteligencia Artificial y consultas en lenguaje natural (NLQ)\*\*.



\## Objetivo



\-   Integrar fuentes de datos ambientales.

&#x20;   

\-   Automatizar la ingesta y procesamiento de información.

&#x20;   

\-   Utilizar IA para detectar patrones y anomalías.

&#x20;   

\-   Permitir consultas mediante lenguaje natural.

&#x20;   

\-   Aplicar buenas prácticas de \*\*DevSecOps\*\*.

&#x20;   



\----------



\## 📁 Estructura principal



```text

├── .github/

│   ├── PULL\_REQUEST\_TEMPLATE.md

│   └── workflows/

│

├── src/

│   ├── frontend/

│   ├── n8n-workflows/

│   ├── database/

│   └── ia-ops/

│

├── infrastructure/

│

├── .gitignore

├── LICENSE

└── README.md



```

\-   `.github/`  - Plantillas y workflows de CI/CD.

\-   `src/frontend/`  - Código del microfrontend.

\-   `src/n8n-workflows/production/`  - Workflows n8n de producción.

\-   `src/n8n-workflows/templates/`  - Plantillas de workflows n8n.

\-   `database/migrations/`  - Migraciones de base de datos.

\-   `database/seeders/`  - Seeders de datos.

\-   `ia-ops/prompts/`  - Prompts y definiciones para IA.

\-   `ia-ops/tests/`  - Pruebas enfocadas en IA y prompts.

\-   `infrastructure/`  - Infraestructura local y despliegue.

\----------



\## Uso local



El proyecto se encuentra actualmente en fase de \*\*estructuración y configuración\*\*.



La configuración y requisitos para ejecutar cada componente serán documentados conforme se integren al proyecto.



Las variables de entorno deberán utilizar:



```text

infrastructure/.env.example



```



No se deben subir archivos `.env` reales.



\----------



\## Gobernanza



\-   `main` será la rama principal y estará protegida.

&#x20;   

\-   Los cambios deberán realizarse mediante \*\*Pull Requests\*\*.

&#x20;   

\-   Todo PR deberá pasar las validaciones automáticas correspondientes.

&#x20;   

\-   Los cambios deberán realizarse en ramas de trabajo.





Los workflows de n8n deberán exportarse como `.json` y revisarse antes de incorporarlos al repositorio.



Las validaciones de seguridad y calidad se automatizarán mediante \*\*GitHub Actions\*\*.



\----------



\## Estado



\*\*Fase actual:\*\* Estructuración y gobernanza DevSecOps.

Próximamente se integrarán los componentes de frontend, backend, n8n, base de datos e IA.

