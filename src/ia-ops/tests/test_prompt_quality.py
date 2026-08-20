# -*- coding: utf-8 -*-
"""
test_prompt_quality.py — Pruebas de calidad para los prompts NLQ de EcoPredict.

Este módulo valida la integridad estructural, semántica y de formato de todos
los prompts definidos en nlq_prompts.json. Las pruebas garantizan que cada
prompt cumple con el esquema requerido, que no existen duplicados y que los
valores de los campos son coherentes con las especificaciones del proyecto.

Categorías de validación:
    - Estructura JSON y formato del archivo
    - Campos obligatorios por prompt
    - Unicidad de identificadores
    - Valores válidos de prioridad y categoría
    - Presencia de variables en las plantillas
    - Coherencia entre variables declaradas y utilizadas

Autor: Equipo QA — EcoPredict-NLQ (Grupo 1)
Fecha: 2026-08-14
"""

import json
import re
from pathlib import Path
from typing import Any

import pytest

# =============================================================================
# Constantes de Validación
# =============================================================================

# Campos obligatorios que debe tener cada prompt
CAMPOS_OBLIGATORIOS: list[str] = [
    "id",
    "category",
    "prompt_template",
    "expected_output_format",
    "variables",
    "priority",
]

# Valores válidos para el campo 'priority'
PRIORIDADES_VALIDAS: set[str] = {"critical", "high", "medium", "low"}

# Categorías ambientales permitidas en el sistema
CATEGORIAS_PERMITIDAS: set[str] = {
    "calidad_aire",
    "calidad_agua",
    "biodiversidad",
    "alertas_ambientales",
    "deforestacion",
    "deteccion_anomalias",
    "residuos",
    "cambio_climatico",
    "ruido_ambiental",
    "reportes_ciudadanos",
}

# Formatos de salida esperados válidos
FORMATOS_SALIDA_VALIDOS: set[str] = {"json", "tabla", "texto", "csv", "markdown"}

# Patrón regex para detectar placeholders de variables: {nombre_variable}
PATRON_PLACEHOLDER = re.compile(r"\{(\w+)\}")

# Ruta al archivo de prompts (relativa desde la raíz del proyecto)
RAIZ_PROYECTO = Path(__file__).resolve().parent.parent.parent.parent
RUTA_PROMPTS = RAIZ_PROYECTO / "src" / "ia-ops" / "prompts" / "nlq_prompts.json"


# =============================================================================
# Clase de Pruebas: Validación del Archivo JSON
# =============================================================================


class TestArchivoPromptsJSON:
    """Pruebas de validación del archivo nlq_prompts.json como unidad."""

    def test_archivo_existe(self) -> None:
        """Verifica que el archivo nlq_prompts.json existe en la ruta esperada."""
        assert RUTA_PROMPTS.exists(), (
            f"El archivo de prompts no fue encontrado en: {RUTA_PROMPTS}\n"
            f"Ruta esperada: src/ia-ops/prompts/nlq_prompts.json"
        )

    def test_archivo_es_json_valido(self) -> None:
        """Verifica que el contenido del archivo es JSON sintácticamente válido."""
        contenido = RUTA_PROMPTS.read_text(encoding="utf-8")
        try:
            datos = json.loads(contenido)
        except json.JSONDecodeError as e:
            pytest.fail(
                f"El archivo nlq_prompts.json contiene JSON inválido:\n"
                f"  Error: {e.msg}\n"
                f"  Línea: {e.lineno}, Columna: {e.colno}"
            )
        assert isinstance(datos, list), (
            f"Se esperaba una lista JSON en la raíz del archivo, "
            f"pero se encontró: {type(datos).__name__}"
        )

    def test_archivo_no_esta_vacio(self, load_prompts: list[dict]) -> None:
        """Verifica que el archivo contiene al menos un prompt."""
        assert len(load_prompts) > 0, (
            "El archivo nlq_prompts.json no contiene ningún prompt. "
            "Se requiere al menos un prompt definido."
        )

    def test_codificacion_utf8(self) -> None:
        """Verifica que el archivo usa codificación UTF-8 correctamente."""
        try:
            RUTA_PROMPTS.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            pytest.fail(
                "El archivo nlq_prompts.json no está codificado en UTF-8. "
                "Todos los archivos del proyecto deben usar codificación UTF-8."
            )


# =============================================================================
# Clase de Pruebas: Campos Obligatorios
# =============================================================================


class TestCamposObligatorios:
    """Pruebas para verificar la presencia de campos obligatorios en cada prompt."""

    def test_todos_los_campos_obligatorios_presentes(
        self, load_prompts: list[dict[str, Any]]
    ) -> None:
        """Verifica que cada prompt contiene todos los campos obligatorios."""
        errores: list[str] = []
        for i, prompt in enumerate(load_prompts):
            prompt_id = prompt.get("id", f"<sin_id, índice={i}>")
            campos_faltantes = [
                campo for campo in CAMPOS_OBLIGATORIOS if campo not in prompt
            ]
            if campos_faltantes:
                errores.append(
                    f"Prompt '{prompt_id}': faltan campos {campos_faltantes}"
                )

        assert not errores, (
            f"Se encontraron {len(errores)} prompt(s) con campos faltantes:\n"
            + "\n".join(f"  - {e}" for e in errores)
        )

    @pytest.mark.parametrize("campo", CAMPOS_OBLIGATORIOS)
    def test_campo_no_es_nulo(
        self, load_prompts: list[dict[str, Any]], campo: str
    ) -> None:
        """Verifica que ningún campo obligatorio tenga valor None."""
        errores: list[str] = []
        for i, prompt in enumerate(load_prompts):
            prompt_id = prompt.get("id", f"<sin_id, índice={i}>")
            if campo in prompt and prompt[campo] is None:
                errores.append(
                    f"Prompt '{prompt_id}': campo '{campo}' es None"
                )

        assert not errores, (
            f"Se encontraron campos con valor None:\n"
            + "\n".join(f"  - {e}" for e in errores)
        )

    def test_campo_id_es_string(
        self, load_prompts: list[dict[str, Any]]
    ) -> None:
        """Verifica que el campo 'id' sea de tipo string en cada prompt."""
        errores: list[str] = []
        for i, prompt in enumerate(load_prompts):
            if "id" in prompt and not isinstance(prompt["id"], str):
                errores.append(
                    f"Prompt índice={i}: 'id' es {type(prompt['id']).__name__}, "
                    f"se esperaba str"
                )

        assert not errores, (
            "Se encontraron IDs con tipo incorrecto:\n"
            + "\n".join(f"  - {e}" for e in errores)
        )

    def test_campo_variables_es_lista(
        self, load_prompts: list[dict[str, Any]]
    ) -> None:
        """Verifica que el campo 'variables' sea de tipo lista en cada prompt."""
        errores: list[str] = []
        for i, prompt in enumerate(load_prompts):
            prompt_id = prompt.get("id", f"<sin_id, índice={i}>")
            if "variables" in prompt and not isinstance(prompt["variables"], list):
                errores.append(
                    f"Prompt '{prompt_id}': 'variables' es "
                    f"{type(prompt['variables']).__name__}, se esperaba list"
                )

        assert not errores, (
            "Se encontraron campos 'variables' con tipo incorrecto:\n"
            + "\n".join(f"  - {e}" for e in errores)
        )


# =============================================================================
# Clase de Pruebas: Unicidad de Identificadores
# =============================================================================


class TestUnicidadIdentificadores:
    """Pruebas para verificar que no existen IDs duplicados."""

    def test_sin_ids_duplicados(
        self, load_prompts: list[dict[str, Any]]
    ) -> None:
        """Verifica que cada prompt tiene un ID único dentro del archivo."""
        ids_vistos: dict[str, int] = {}
        duplicados: list[str] = []

        for i, prompt in enumerate(load_prompts):
            prompt_id = prompt.get("id", "")
            if prompt_id in ids_vistos:
                duplicados.append(
                    f"ID '{prompt_id}' duplicado en índices "
                    f"{ids_vistos[prompt_id]} y {i}"
                )
            else:
                ids_vistos[prompt_id] = i

        assert not duplicados, (
            f"Se encontraron {len(duplicados)} ID(s) duplicado(s):\n"
            + "\n".join(f"  - {d}" for d in duplicados)
        )

    def test_ids_no_vacios(
        self, load_prompts: list[dict[str, Any]]
    ) -> None:
        """Verifica que ningún ID esté vacío o contenga solo espacios."""
        errores: list[str] = []
        for i, prompt in enumerate(load_prompts):
            prompt_id = prompt.get("id", "")
            if not prompt_id or not prompt_id.strip():
                errores.append(f"Prompt en índice {i} tiene ID vacío.")

        assert not errores, (
            "Se encontraron prompts con IDs vacíos:\n"
            + "\n".join(f"  - {e}" for e in errores)
        )


# =============================================================================
# Clase de Pruebas: Valores de Prioridad
# =============================================================================


class TestValoresPrioridad:
    """Pruebas para validar que los valores de prioridad son válidos."""

    def test_prioridades_validas(
        self, load_prompts: list[dict[str, Any]]
    ) -> None:
        """Verifica que cada prompt usa un valor de prioridad permitido."""
        errores: list[str] = []
        for i, prompt in enumerate(load_prompts):
            prompt_id = prompt.get("id", f"<sin_id, índice={i}>")
            prioridad = prompt.get("priority", "")
            if prioridad not in PRIORIDADES_VALIDAS:
                errores.append(
                    f"Prompt '{prompt_id}': prioridad '{prioridad}' no es válida. "
                    f"Valores permitidos: {sorted(PRIORIDADES_VALIDAS)}"
                )

        assert not errores, (
            "Se encontraron prioridades inválidas:\n"
            + "\n".join(f"  - {e}" for e in errores)
        )

    def test_al_menos_un_prompt_critico(
        self, load_prompts: list[dict[str, Any]]
    ) -> None:
        """Verifica que exista al menos un prompt con prioridad 'critical'."""
        criticos = [
            p for p in load_prompts if p.get("priority") == "critical"
        ]
        assert len(criticos) > 0, (
            "No se encontró ningún prompt con prioridad 'critical'. "
            "El sistema requiere al menos un prompt crítico."
        )


# =============================================================================
# Clase de Pruebas: Plantillas y Variables
# =============================================================================


class TestPlantillasVariables:
    """Pruebas para validar las plantillas de prompts y sus variables."""

    def test_plantilla_contiene_al_menos_un_placeholder(
        self, load_prompts: list[dict[str, Any]]
    ) -> None:
        """Verifica que cada plantilla contiene al menos un placeholder {variable}."""
        errores: list[str] = []
        for i, prompt in enumerate(load_prompts):
            prompt_id = prompt.get("id", f"<sin_id, índice={i}>")
            plantilla = prompt.get("prompt_template", "")
            placeholders = PATRON_PLACEHOLDER.findall(plantilla)
            if not placeholders:
                errores.append(
                    f"Prompt '{prompt_id}': la plantilla no contiene "
                    f"ningún placeholder {{variable}}."
                )

        assert not errores, (
            "Se encontraron plantillas sin placeholders:\n"
            + "\n".join(f"  - {e}" for e in errores)
        )

    def test_variables_declaradas_coinciden_con_placeholders(
        self, load_prompts: list[dict[str, Any]]
    ) -> None:
        """
        Verifica que las variables declaradas en el campo 'variables'
        coincidan con los placeholders usados en la plantilla.
        """
        errores: list[str] = []
        for i, prompt in enumerate(load_prompts):
            prompt_id = prompt.get("id", f"<sin_id, índice={i}>")
            plantilla = prompt.get("prompt_template", "")
            variables_declaradas = set(prompt.get("variables", []))
            placeholders_encontrados = set(PATRON_PLACEHOLDER.findall(plantilla))

            # Variables declaradas pero no usadas en la plantilla
            no_usadas = variables_declaradas - placeholders_encontrados
            if no_usadas:
                errores.append(
                    f"Prompt '{prompt_id}': variables declaradas pero no usadas "
                    f"en la plantilla: {sorted(no_usadas)}"
                )

            # Placeholders en la plantilla pero no declarados en variables
            no_declaradas = placeholders_encontrados - variables_declaradas
            if no_declaradas:
                errores.append(
                    f"Prompt '{prompt_id}': placeholders en la plantilla sin "
                    f"declarar en 'variables': {sorted(no_declaradas)}"
                )

        assert not errores, (
            "Se encontraron inconsistencias entre variables y placeholders:\n"
            + "\n".join(f"  - {e}" for e in errores)
        )

    def test_plantilla_no_esta_vacia(
        self, load_prompts: list[dict[str, Any]]
    ) -> None:
        """Verifica que ninguna plantilla de prompt esté vacía."""
        errores: list[str] = []
        for i, prompt in enumerate(load_prompts):
            prompt_id = prompt.get("id", f"<sin_id, índice={i}>")
            plantilla = prompt.get("prompt_template", "")
            if not plantilla or not plantilla.strip():
                errores.append(
                    f"Prompt '{prompt_id}': la plantilla está vacía."
                )

        assert not errores, (
            "Se encontraron plantillas vacías:\n"
            + "\n".join(f"  - {e}" for e in errores)
        )

    def test_variables_lista_no_vacia(
        self, load_prompts: list[dict[str, Any]]
    ) -> None:
        """Verifica que la lista de variables no esté vacía en cada prompt."""
        errores: list[str] = []
        for i, prompt in enumerate(load_prompts):
            prompt_id = prompt.get("id", f"<sin_id, índice={i}>")
            variables = prompt.get("variables", [])
            if isinstance(variables, list) and len(variables) == 0:
                errores.append(
                    f"Prompt '{prompt_id}': la lista de variables está vacía."
                )

        assert not errores, (
            "Se encontraron prompts con lista de variables vacía:\n"
            + "\n".join(f"  - {e}" for e in errores)
        )


# =============================================================================
# Clase de Pruebas: Categorías
# =============================================================================


class TestCategorias:
    """Pruebas para validar las categorías de los prompts."""

    def test_categorias_validas(
        self, load_prompts: list[dict[str, Any]]
    ) -> None:
        """Verifica que cada prompt usa una categoría de la lista permitida."""
        errores: list[str] = []
        for i, prompt in enumerate(load_prompts):
            prompt_id = prompt.get("id", f"<sin_id, índice={i}>")
            categoria = prompt.get("category", "")
            if categoria not in CATEGORIAS_PERMITIDAS:
                errores.append(
                    f"Prompt '{prompt_id}': categoría '{categoria}' no es válida. "
                    f"Categorías permitidas: {sorted(CATEGORIAS_PERMITIDAS)}"
                )

        assert not errores, (
            "Se encontraron categorías inválidas:\n"
            + "\n".join(f"  - {e}" for e in errores)
        )

    def test_formato_salida_valido(
        self, load_prompts: list[dict[str, Any]]
    ) -> None:
        """Verifica que el formato de salida esperado es uno de los permitidos."""
        errores: list[str] = []
        for i, prompt in enumerate(load_prompts):
            prompt_id = prompt.get("id", f"<sin_id, índice={i}>")
            formato = prompt.get("expected_output_format", "")
            if formato not in FORMATOS_SALIDA_VALIDOS:
                errores.append(
                    f"Prompt '{prompt_id}': formato '{formato}' no es válido. "
                    f"Formatos permitidos: {sorted(FORMATOS_SALIDA_VALIDOS)}"
                )

        assert not errores, (
            "Se encontraron formatos de salida inválidos:\n"
            + "\n".join(f"  - {e}" for e in errores)
        )


# =============================================================================
# Clase de Pruebas: Validaciones Adicionales de Calidad
# =============================================================================


class TestCalidadAdicional:
    """Pruebas adicionales de calidad y buenas prácticas."""

    def test_longitud_minima_plantilla(
        self, load_prompts: list[dict[str, Any]]
    ) -> None:
        """
        Verifica que las plantillas tengan una longitud mínima razonable.
        Un prompt demasiado corto probablemente no es suficientemente descriptivo.
        """
        LONGITUD_MINIMA = 20  # caracteres
        errores: list[str] = []
        for i, prompt in enumerate(load_prompts):
            prompt_id = prompt.get("id", f"<sin_id, índice={i}>")
            plantilla = prompt.get("prompt_template", "")
            if len(plantilla) < LONGITUD_MINIMA:
                errores.append(
                    f"Prompt '{prompt_id}': plantilla muy corta "
                    f"({len(plantilla)} caracteres, mínimo: {LONGITUD_MINIMA})."
                )

        assert not errores, (
            "Se encontraron plantillas demasiado cortas:\n"
            + "\n".join(f"  - {e}" for e in errores)
        )

    def test_id_sigue_convención_nomenclatura(
        self, load_prompts: list[dict[str, Any]]
    ) -> None:
        """
        Verifica que los IDs siguen la convención de nomenclatura: NLQ-XXX.

        La convención esperada es un prefijo 'NLQ-' seguido de un número
        de tres dígitos (ej: NLQ-001, NLQ-042, NLQ-100).
        """
        patron_id = re.compile(r"^NLQ-\d{3}$")
        errores: list[str] = []
        for i, prompt in enumerate(load_prompts):
            prompt_id = prompt.get("id", "")
            if not patron_id.match(prompt_id):
                errores.append(
                    f"Prompt índice={i}: ID '{prompt_id}' no sigue la "
                    f"convención NLQ-XXX (ej: NLQ-001)."
                )

        assert not errores, (
            "Se encontraron IDs que no siguen la convención:\n"
            + "\n".join(f"  - {e}" for e in errores)
        )
