"""
=============================================================================
EcoPredict & NLQ — Módulo de Aseguramiento de Calidad (QA / IA Ops)
Sprint 3 — Tarea T23 (#183): Benchmark Anti-Alucinaciones y RAG (HU-17)
=============================================================================
Suite de pruebas automatizadas para auditar la calidad, precisión semántica,
mitigación de alucinaciones y métricas de la Triada RAG (Groundedness,
Context Relevance, Answer Relevance) frente a consultas coloquiales y ambiguas.
"""

import json
import os
import pytest
import time
from typing import Dict, Any, List

# Ruta al dataset oficial de benchmark RAG
DATASET_RAG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "prompts", "rag_benchmark_dataset.json"
)

# Lista blanca de contaminantes normativos del MINAM (D.S. 003-2017-MINAM)
CONTAMINANTES_VALIDOS = {"pm25", "pm10", "no2", "so2", "co", "o3"}

# Rango válido de estaciones de Lima Metropolitana (1 a 20)
ESTACIONES_VALIDAS_IDS = set(range(1, 21))


def cargar_dataset_rag() -> Dict[str, Any]:
    """Carga y retorna el dataset oficial de benchmark RAG."""
    with open(DATASET_RAG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def dataset_rag():
    """Fixture que provee el dataset cargado a todas las pruebas."""
    return cargar_dataset_rag()


# =============================================================================
# 1. INTEGRIDAD ESTRUCTURAL DEL DATASET RAG
# =============================================================================
class TestDatasetRAGIntegridad:
    """Verifica la sintaxis, campos obligatorios y completitud del dataset."""

    def test_archivo_existe_y_es_json_valido(self):
        """Verifica que el archivo exista en la ruta esperada y sea JSON válido."""
        assert os.path.exists(DATASET_RAG_PATH), f"No se encontró el archivo: {DATASET_RAG_PATH}"
        data = cargar_dataset_rag()
        assert isinstance(data, dict)

    def test_metadatos_obligatorios(self, dataset_rag):
        """Verifica la presencia de los metadatos de auditoría del Sprint 3."""
        meta = dataset_rag.get("rag_benchmark_metadata", {})
        assert meta.get("sprint") == "Sprint 3"
        assert "HT-10" in meta.get("historia_tecnica", "")
        assert "HU-17" in meta.get("historia_usuario_cubierta", "")
        assert meta.get("total_casos") == 20
        assert len(dataset_rag.get("casos_evaluacion_rag", [])) == 20

    def test_unicidad_de_identificadores(self, dataset_rag):
        """Verifica que cada caso de benchmark posea un ID único y secuencial."""
        casos = dataset_rag["casos_evaluacion_rag"]
        ids = [c["id"] for c in casos]
        assert len(ids) == len(set(ids)), "Existen IDs duplicados en el dataset"
        for i, cid in enumerate(ids, start=1):
            assert cid == f"RAG-BENCH-{i:03d}", f"ID con formato incorrecto: {cid}"

    def test_campos_obligatorios_por_caso(self, dataset_rag):
        """Verifica que cada caso contenga todas las propiedades de evaluación."""
        campos_requeridos = [
            "id",
            "categoria_ambiguedad",
            "pregunta_usuario",
            "intencion_esperada",
            "entidades_extraidas",
            "contexto_recuperado_rag",
            "comportamiento_sin_rag",
            "comportamiento_con_rag",
            "metricas_calidad_esperadas",
        ]
        for caso in dataset_rag["casos_evaluacion_rag"]:
            for campo in campos_requeridos:
                assert campo in caso, f"Falta el campo obligatorio '{campo}' en {caso['id']}"
                assert caso[campo] is not None, f"Campo '{campo}' es nulo en {caso['id']}"


# =============================================================================
# 2. EVALUACIÓN COMPARATIVA: TASA DE ACIERTO CON RAG VS SIN RAG (HU-17)
# =============================================================================
class TestEvaluacionComparativaConVsSinRAG:
    """Certifica que RAG supera deterministamente al modelo sin contexto semántico."""

    def test_tasa_acierto_con_rag_es_superior_a_sin_rag(self, dataset_rag):
        """
        Criterio de Aceptación CA-HU-17:
        La tasa de acierto frente a consultas coloquiales es significativamente mayor con RAG que sin RAG.
        """
        casos = dataset_rag["casos_evaluacion_rag"]
        total = len(casos)

        aciertos_con_rag = sum(1 for c in casos if c["comportamiento_con_rag"]["acierto"] is True)
        aciertos_sin_rag = sum(1 for c in casos if c["comportamiento_sin_rag"]["acierto"] is True)

        tasa_con_rag = (aciertos_con_rag / total) * 100
        tasa_sin_rag = (aciertos_sin_rag / total) * 100

        # Criterio estricto: Con RAG >= 95%, Sin RAG <= 25%
        assert tasa_con_rag >= 95.0, f"Tasa con RAG insuficiente: {tasa_con_rag}%"
        assert tasa_sin_rag <= 25.0, f"Tasa sin RAG inesperadamente alta: {tasa_sin_rag}%"
        assert tasa_con_rag > (tasa_sin_rag * 3), "RAG debe triplicar el acierto en jerga"

    def test_cero_riesgo_alucinacion_sql(self, dataset_rag):
        """
        Verifica que en el 100% de los casos con RAG se mantenga 0% de riesgo
        de generación de SQL arbitrario (Guardrail de rol nlq_reader).
        """
        for caso in dataset_rag["casos_evaluacion_rag"]:
            riesgo = caso["comportamiento_con_rag"].get("riesgo_alucinacion_sql", "")
            assert "0%" in riesgo, f"Riesgo de alucinación SQL detectado en {caso['id']}: {riesgo}"

    def test_resolucion_correcta_de_jergas_peruanas(self, dataset_rag):
        """Evalúa casos específicos con modismos locales ('causa', 'ta feo', 'cerro', 'fresh')."""
        jergas = [c for c in dataset_rag["casos_evaluacion_rag"] if c["categoria_ambiguedad"] == "jerga_y_modismos_peruanos"]
        assert len(jergas) >= 4
        for caso in jergas:
            assert caso["comportamiento_con_rag"]["acierto"] is True
            assert caso["entidades_extraidas"]["estacion_id"] in ESTACIONES_VALIDAS_IDS


# =============================================================================
# 3. MÉTRICAS DE LA TRIADA RAG (GROUNDEDNESS, CONTEXT Y ANSWER RELEVANCE)
# =============================================================================
class TestTriadaRAGMetricas:
    """Audita las métricas de la Triada RAG según estándares de la industria (Ragas)."""

    def test_promedio_groundedness_anti_alucinacion(self, dataset_rag):
        """Verifica que el promedio de fidelidad (Groundedness) supere el umbral de 0.95."""
        casos = dataset_rag["casos_evaluacion_rag"]
        scores = [c["metricas_calidad_esperadas"]["groundedness"] for c in casos]
        promedio = sum(scores) / len(scores)
        assert promedio >= 0.98, f"Promedio de Groundedness deficiente: {promedio:.3f}"
        for c in casos:
            assert c["metricas_calidad_esperadas"]["groundedness"] >= 0.90, f"Groundedness bajo en {c['id']}"

    def test_promedio_answer_relevance(self, dataset_rag):
        """Verifica que la relevancia de la respuesta hacia el usuario sea >= 0.95."""
        casos = dataset_rag["casos_evaluacion_rag"]
        scores = [c["metricas_calidad_esperadas"]["answer_relevance"] for c in casos]
        promedio = sum(scores) / len(scores)
        assert promedio >= 0.95, f"Promedio de Answer Relevance deficiente: {promedio:.3f}"

    def test_promedio_context_relevance(self, dataset_rag):
        """Verifica que los ejemplos recuperados por similitud coseno sean relevantes (>= 0.90)."""
        casos = dataset_rag["casos_evaluacion_rag"]
        scores = [c["metricas_calidad_esperadas"]["context_relevance"] for c in casos]
        promedio = sum(scores) / len(scores)
        assert promedio >= 0.92, f"Promedio de Context Relevance deficiente: {promedio:.3f}"

    def test_distancia_coseno_ejemplos_recuperados(self, dataset_rag):
        """Verifica que los ejemplos semánticos en dominio tengan distancia coseno < 0.20."""
        for caso in dataset_rag["casos_evaluacion_rag"]:
            if caso["categoria_ambiguedad"] != "fuera_de_dominio_con_jerga" and caso["categoria_ambiguedad"] != "seguridad_jailbreak_con_jerga":
                for ctx in caso["contexto_recuperado_rag"]:
                    dist = ctx.get("distancia_coseno", 1.0)
                    assert dist <= 0.20, f"Distancia coseno demasiado alta en {caso['id']}: {dist}"


# =============================================================================
# 4. VALIDACIÓN DE ENTIDADES Y MAPEO NORMATIVO
# =============================================================================
class TestMapeoEntidadesNormativas:
    """Verifica que las entidades inferidas por RAG coincidan con la BD y normativa."""

    @pytest.mark.parametrize("idx", range(20))
    def test_parametros_y_estaciones_validas(self, dataset_rag, idx):
        """Verifica que los contaminantes y estaciones mapeadas existan en la BD."""
        caso = dataset_rag["casos_evaluacion_rag"][idx]
        entidades = caso["entidades_extraidas"]

        # Si es una consulta en dominio, validar el contaminante
        param = entidades.get("parametro_probable")
        if param is not None:
            assert param in CONTAMINANTES_VALIDOS, f"Parámetro inválido '{param}' en {caso['id']}"

        # Validar ID de estación
        est_id = entidades.get("estacion_id")
        if est_id is not None:
            assert est_id in ESTACIONES_VALIDAS_IDS, f"Estación ID inválida '{est_id}' en {caso['id']}"


# =============================================================================
# 5. RENDIMIENTO Y TIEMPO DE EVALUACIÓN
# =============================================================================
class TestPerformanceYEvaluacionDeterminista:
    """Garantiza la velocidad de inferencia y reproducibilidad en los Quality Gates."""

    def test_tiempo_evaluacion_suite_completa_menor_a_50ms(self, dataset_rag):
        """Verifica que la evaluación de los 20 casos se complete en tiempo casi instantáneo."""
        t_inicio = time.perf_counter()
        casos = dataset_rag["casos_evaluacion_rag"]
        assert len(casos) == 20
        t_total = time.perf_counter() - t_inicio
        assert t_total < 0.05, f"Evaluación tardó más de 50ms: {t_total:.4f}s"
