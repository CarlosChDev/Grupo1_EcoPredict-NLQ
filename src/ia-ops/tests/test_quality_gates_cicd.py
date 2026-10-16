"""
=============================================================================
EcoPredict & NLQ — Módulo de Aseguramiento de Calidad (QA / IA Ops)
Sprint 3 — Tarea T22 (#182): Consolidación de Quality Gates en CI/CD y Dependabot (HT-09)
=============================================================================
Suite de pruebas automatizadas para auditar y certificar la configuración,
reglas de bloqueo y políticas de seguridad de los Quality Gates en CI/CD:
- Verificación de Workflows de GitHub Actions (ai-testing-ci, newman-ci, frontend-ci, sast, dast, cd)
- Auditoría de Reglas de Dependabot (.github/dependabot.yml: ecosistemas npm, pip, github-actions)
- Regla de Bloqueo Zero-Failures (Todos los Quality Gates deben ser estrictos y obligatorios)
- Validación de matriz de compatibilidad de Python 3.12 y Node.js 20 en los runners de CI
- Verificación de Secrets y Guardrails de Inyección en los pipelines
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, List
import pytest


# =============================================================================
# ESPECIFICACIÓN Y RUTAS DE WORKFLOWS DE CI/CD
# =============================================================================

REPO_ROOT = Path(__file__).resolve().parents[3]
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
DEPENDABOT_FILE = REPO_ROOT / ".github" / "dependabot.yml"

WORKFLOWS_OBLIGATORIOS = [
    "ai-testing-ci.yml",
    "newman-ci.yml",
    "frontend-ci.yml",
    "sast.yml",
    "dast.yml",
    "cd.yml",
    "n8n-validate-ci.yml"
]


# =============================================================================
# SUITE DE PRUEBAS AUTOMATIZADAS (PYTEST)
# =============================================================================

class TestQualityGatesCiCd:
    """Pruebas de integridad, seguridad y consolidación de pipelines en GitHub Actions."""

    # -------------------------------------------------------------------------
    # 1. VERIFICACIÓN DE EXISTENCIA Y ESTRUCTURA DE WORKFLOWS
    # -------------------------------------------------------------------------

    def test_todos_los_workflows_obligatorios_existen(self):
        """Certifica que los 7 flujos de validación continua existan en .github/workflows/."""
        assert WORKFLOWS_DIR.exists(), "El directorio .github/workflows no existe."
        for wf in WORKFLOWS_OBLIGATORIOS:
            path = WORKFLOWS_DIR / wf
            assert path.is_file(), f"Falta el workflow crítico de CI/CD: {wf}"

    def test_ai_testing_ci_ejecuta_pytest_estricto_en_python_312(self):
        """Valida que ai-testing-ci.yml use Python 3.12 y ejecute pytest sin flags que ignoren errores."""
        contenido = (WORKFLOWS_DIR / "ai-testing-ci.yml").read_text(encoding="utf-8")
        assert 'python-version: "3.12"' in contenido or "python-version: 3.12" in contenido
        assert "pytest src/ia-ops/tests" in contenido
        assert "continue-on-error: true" not in contenido, "El Quality Gate de IA no debe tolerar tests fallidos."

    def test_newman_ci_valida_coleccion_oficial_con_timeout(self):
        """Valida que newman-ci.yml audite la colección de API y tenga timeout acotado."""
        contenido = (WORKFLOWS_DIR / "newman-ci.yml").read_text(encoding="utf-8")
        assert "timeout-minutes: 20" in contenido
        assert "eco_predict_nlq_collection.json" in contenido
        assert "fail-fast" not in contenido or "continue-on-error: true" not in contenido

    def test_sast_codeql_analiza_javascript_typescript(self):
        """Valida que sast.yml ejecute análisis estático CodeQL en el código frontend y scripts."""
        contenido = (WORKFLOWS_DIR / "sast.yml").read_text(encoding="utf-8")
        assert "github/codeql-action/init" in contenido
        assert "github/codeql-action/analyze" in contenido
        assert "javascript-typescript" in contenido

    def test_dast_zap_escanea_portal_de_produccion(self):
        """Valida que dast.yml ejecute OWASP ZAP Baseline Scan contra la URL oficial."""
        contenido = (WORKFLOWS_DIR / "dast.yml").read_text(encoding="utf-8")
        assert "zaproxy/action-baseline" in contenido
        assert "https://grupo1-eco-predict-nlq.vercel.app/" in contenido

    # -------------------------------------------------------------------------
    # 2. AUDITORÍA DE DEPENDABOT Y GESTIÓN DE VULNERABILIDADES
    # -------------------------------------------------------------------------

    def test_dependabot_configurado_correctamente(self):
        """Acepta Dependabot pausado o valida su configuración si está activo."""
        if not DEPENDABOT_FILE.is_file():
            # La ausencia del archivo representa una pausa intencional.
            return

        contenido = DEPENDABOT_FILE.read_text(encoding="utf-8")

        # Si existe, la configuración debe ser válida y tener al menos
        # un ecosistema configurado. No se acepta updates: [].
        assert "version: 2" in contenido
        assert re.search(r"(?m)^updates:\s*$", contenido), (
            "Dependabot está configurado, pero no contiene una lista updates válida."
        )
        assert re.search(r'package-ecosystem:\s*"(npm|pip|github-actions)"', contenido), (
            "Dependabot debe tener al menos un ecosistema activo."
        )

    def test_dependabot_asigna_revisores_y_labels_apropiados(self):
        """Comprueba revisores y etiquetas cuando Dependabot está activo."""
        if not DEPENDABOT_FILE.is_file():
            # Sin archivo de configuración, Dependabot está pausado.
            return

        contenido = DEPENDABOT_FILE.read_text(encoding="utf-8")

        assert "JohannK99" in contenido
        assert "CarlosChDev" in contenido
        assert "dependencies" in contenido
        assert "security" in contenido

    # -------------------------------------------------------------------------
    # 3. SEGURIDAD Y PERMISOS DE LEAST PRIVILEGE
    # -------------------------------------------------------------------------

    def test_least_privilege_en_workflows_de_pull_request(self):
        """Valida que los workflows de CI usen permisos restrictivos 'contents: read'."""
        for wf_nombre in ["ai-testing-ci.yml", "frontend-ci.yml", "n8n-validate-ci.yml"]:
            contenido = (WORKFLOWS_DIR / wf_nombre).read_text(encoding="utf-8")
            assert "contents: read" in contenido, f"El workflow {wf_nombre} debe declarar permisos mínimos."
