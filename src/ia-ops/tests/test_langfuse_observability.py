"""
=============================================================================
EcoPredict & NLQ — Módulo de Aseguramiento de Calidad (QA / IA Ops)
Sprint 3 — Tarea T25 (#185): Auditoría de Observabilidad con Langfuse (HT-08/10)
=============================================================================
Suite de pruebas automatizadas para auditar la integración y exportación de
telemetría hacia el dashboard de Langfuse (OpenAPI v2 Ingestion API).
Verifica contratos de datos, cálculo de costos de tokens (Groq vs Gemini),
generación de Scores del evaluador LLM-as-a-Judge y cumplimiento de SLA.
"""

from datetime import datetime
import json
import os
from pathlib import Path
import sys
import pytest
from typing import Dict, Any

# Agregar directorio src/ia-ops al path de python
RUTA_IA_OPS = Path(__file__).resolve().parent.parent
if str(RUTA_IA_OPS) not in sys.path:
    sys.path.insert(0, str(RUTA_IA_OPS))

from evaluators.langfuse_auditor import (
    AuditorLangfuse,
    LangfuseTracePayload,
    LangfuseGeneration,
    LangfuseScore,
    CATALOGO_PRECIOS_TOKENS
)
from evaluators.llm_judge import EvaluadorCalidadIA, ResultadoJuicio


@pytest.fixture(scope="module")
def auditor():
    """Fixture que provee una instancia del Auditor de Langfuse."""
    return AuditorLangfuse()


@pytest.fixture(scope="module")
def traza_muestra_groq():
    """Fixture con una traza estándar ejecutada con Groq LLaMA 3.3 70B."""
    return {
        "id": "TR-TEST-GROQ-001",
        "pregunta": "¿Cuál es el nivel de PM2.5 en San Borja?",
        "respuesta": "En la estación San Borja el nivel de PM2.5 es de 15.2 µg/m³, calidad buena.",
        "contexto_bd": {"estacion_id": 1, "estacion_nombre": "San Borja (SBJ)", "valor": 15.2},
        "intencion_esperada": "consultar_calidad_aire",
        "modelo_ejecutado": "groq-llama-3.3-70b",
        "es_fallback": False,
        "latencia_ms": 1150,
        "tokens_totales": 140
    }


@pytest.fixture(scope="module")
def traza_muestra_gemini_fallback():
    """Fixture con una traza ejecutada mediante Fallback en Google Gemini 1.5 Flash."""
    return {
        "id": "TR-TEST-GEMINI-002",
        "pregunta": "¿Hay alguna anomalía crítica de PM10 en Carabayllo?",
        "respuesta": "Se detectó un nivel anómalo de PM10 en Carabayllo de 125.0 µg/m³, superando los límites.",
        "contexto_bd": {"estacion_id": 2, "estacion_nombre": "Carabayllo", "valor": 125.0},
        "intencion_esperada": "deteccion_anomalias",
        "modelo_ejecutado": "gemini-1.5-flash",
        "es_fallback": True,
        "latencia_ms": 2900,
        "tokens_totales": 210
    }


# =============================================================================
# 1. PRUEBAS DE CONTRATO Y ESQUEMA DE DATOS LANGFUSE (OPENAPI V2)
# =============================================================================
class TestContratoYEsquemaLangfuse:
    """Verifica que los objetos generados cumplan la especificación oficial de Langfuse."""

    def test_estructura_traza_cumple_contrato_openapi(self, auditor, traza_muestra_groq):
        """Verifica que el payload contenga todos los campos obligatorios del esquema de Traza."""
        payload = auditor.construir_payload_traza(traza_muestra_groq)
        assert isinstance(payload, LangfuseTracePayload)
        assert auditor.validar_contrato_langfuse(payload) is True

        d = payload.to_dict()
        assert d["id"] == "TR-TEST-GROQ-001"
        assert d["name"] == "nlq_consulta_ambiental"
        assert isinstance(d["timestamp"], str)
        assert isinstance(d["tags"], list)
        assert len(d["generations"]) == 1
        assert len(d["scores"]) >= 5

    def test_generaciones_llm_contiene_metadatos_completos(self, auditor, traza_muestra_groq):
        """Verifica que la observación de Generación contenga conteo de tokens y latencia."""
        payload = auditor.construir_payload_traza(traza_muestra_groq)
        gen = payload.generations[0]

        assert isinstance(gen, LangfuseGeneration)
        assert gen.model == "groq-llama-3.3-70b"
        assert gen.totalTokens == 140
        assert gen.promptTokens > 0
        assert gen.completionTokens > 0
        assert gen.promptTokens + gen.completionTokens == gen.totalTokens
        assert gen.latencyMs == 1150
        assert gen.calculatedCostUsd > 0.0

    def test_timestamps_en_formato_iso8601_utc(self, auditor, traza_muestra_groq):
        """Verifica que la marca temporal de la traza sea ISO 8601 válida con zona UTC."""
        payload = auditor.construir_payload_traza(traza_muestra_groq)
        # Debe poder parsearse sin lanzar ValueError
        parsed_dt = datetime.fromisoformat(payload.timestamp.replace("Z", "+00:00"))
        assert parsed_dt.year >= 2026

    def test_tags_contienen_clasificacion_taxonomica_correcta(
        self,
        auditor,
        traza_muestra_groq,
        traza_muestra_gemini_fallback
    ):
        """Verifica que las etiquetas distingan el proveedor principal y los eventos de fallback."""
        payload_groq = auditor.construir_payload_traza(traza_muestra_groq)
        assert "provider-groq" in payload_groq.tags
        assert "fallback-failover" not in payload_groq.tags

        payload_gemini = auditor.construir_payload_traza(traza_muestra_gemini_fallback)
        assert "provider-google" in payload_gemini.tags
        assert "fallback-failover" in payload_gemini.tags


# =============================================================================
# 2. PRUEBAS DE CÁLCULO DE COSTOS Y CONSUMO DE TOKENS
# =============================================================================
class TestCalculoCostosYTokens:
    """Verifica la precisión matemática del modelado económico por token en dólares."""

    def test_costo_tokens_groq_llama_calculo_exacto(self, auditor):
        """Verifica el cálculo para Groq ($0.59 input / $0.79 output por 1M tokens)."""
        # 1,000,000 tokens (650k input, 350k output):
        # Costo = (650,000/1M)*0.59 + (350,000/1M)*0.79 = 0.3835 + 0.2765 = 0.6600 USD
        costo = auditor.calcular_costo_tokens("groq-llama-3.3-70b", 1_000_000, ratio_input=0.65)
        assert pytest.approx(costo, rel=1e-3) == 0.6600

    def test_costo_tokens_gemini_flash_calculo_exacto(self, auditor):
        """Verifica el cálculo para Gemini ($0.075 input / $0.30 output por 1M tokens)."""
        # 1,000,000 tokens (650k input, 350k output):
        # Costo = (650,000/1M)*0.075 + (350,000/1M)*0.30 = 0.04875 + 0.1050 = 0.15375 USD
        costo = auditor.calcular_costo_tokens("gemini-1.5-flash", 1_000_000, ratio_input=0.65)
        assert pytest.approx(costo, rel=1e-3) == 0.15375

    def test_gemini_es_mas_economico_que_groq_en_costo_token(self, auditor):
        """Comprueba que el modelo de fallback tenga un costo unitario por token menor."""
        costo_groq = auditor.calcular_costo_tokens("groq-llama-3.3-70b", 10_000)
        costo_gemini = auditor.calcular_costo_tokens("gemini-1.5-flash", 10_000)
        assert costo_gemini < costo_groq


# =============================================================================
# 3. PRUEBAS DE VINCULACIÓN DE SCORES DEL LLM-AS-A-JUDGE
# =============================================================================
class TestMapeoScoresEvaluador:
    """Verifica que las métricas del evaluador se mapeen fielmente a Scores en Langfuse."""

    def test_score_groundedness_normalizado_cero_a_uno(self, auditor, traza_muestra_groq):
        """Verifica que el puntaje de fidelidad (1.0 a 5.0) se normalice a escala [0.0, 1.0]."""
        payload = auditor.construir_payload_traza(traza_muestra_groq)
        scores_map = {s.name: s for s in payload.scores}

        assert "groundedness" in scores_map
        score_g = scores_map["groundedness"]
        assert score_g.dataType == "NUMERIC"
        assert 0.0 <= score_g.value <= 1.0
        # Respuesta fidedigna (5.0 / 5.0) -> 1.0
        assert score_g.value == 1.0

    def test_score_alucinacion_detectada_booleano_y_comentario(self, auditor):
        """Verifica que una alucinación inyectada active el score booleano true."""
        traza_alucinada = {
            "id": "TR-TEST-ALUC-999",
            "pregunta": "¿Cuánto PM2.5 hay en San Borja?",
            "respuesta": "En San Borja el valor es 999.0 µg/m³ peligro extremo.",
            "contexto_bd": {"estacion_id": 1, "estacion_nombre": "San Borja (SBJ)", "valor": 15.2},
            "intencion_esperada": "consultar_calidad_aire",
            "modelo_ejecutado": "groq-llama-3.3-70b",
            "es_fallback": False,
            "latencia_ms": 1100,
            "tokens_totales": 120
        }
        payload = auditor.construir_payload_traza(traza_alucinada)
        scores_map = {s.name: s for s in payload.scores}

        assert scores_map["hallucination_detected"].value is True
        assert scores_map["groundedness"].value == 0.2  # 1.0 / 5.0 normalizado
        assert "falsificacion_numerica" in scores_map["hallucination_detected"].comment
        assert "alerta-alucinacion" in payload.tags

    def test_score_sla_latency_detecta_incumplimientos(self, auditor):
        """Verifica que latencias superiores a 5,000 ms activen el score de infracción de SLA."""
        traza_lenta = {
            "id": "TR-TEST-SLOW-001",
            "pregunta": "¿Reporte histórico de todo el año?",
            "respuesta": "El reporte histórico indica valores estables.",
            "contexto_bd": {"estacion_id": 1, "estacion_nombre": "San Borja"},
            "intencion_esperada": "consultar_historico",
            "modelo_ejecutado": "groq-llama-3.3-70b",
            "es_fallback": False,
            "latencia_ms": 5800,  # Supera SLA de 5000 ms
            "tokens_totales": 300
        }
        payload = auditor.construir_payload_traza(traza_lenta)
        scores_map = {s.name: s for s in payload.scores}

        assert scores_map["latency_sla_breach"].value is True
        assert payload.metadata["sla_cumplido"] is False


# =============================================================================
# 4. PRUEBAS DE AUDITORÍA Y EXPORTACIÓN CONSOLIDADA
# =============================================================================
class TestAuditoriaYExportacionConsolidada:
    """Verifica la exportación del lote de 20 trazas de producción hacia Langfuse."""

    def test_dataset_completo_exporta_20_trazas(self, auditor):
        """Verifica que el reporte consolide las 20 trazas sin excepciones."""
        reporte = auditor.auditar_y_exportar_dataset()

        assert reporte["total_trazas_procesadas"] == 20
        assert len(reporte["trazas_exportadas"]) == 20
        assert reporte["resumen_costos"]["costo_total_acumulado_usd"] > 0.0
        assert reporte["resumen_costos"]["tokens_totales_consumidos"] > 2000

    def test_metricas_observabilidad_consistentes_con_llm_judge(self, auditor):
        """Verifica que las tasas observadas coincidan con la calibración del Sprint (10% aluc, 20% fallback, 100% SLA)."""
        reporte = auditor.auditar_y_exportar_dataset()
        metricas = reporte["metricas_calidad_observadas"]

        assert metricas["tasa_alucinacion_porcentaje"] == 10.0
        assert metricas["tasa_fallback_porcentaje"] == 20.0
        assert metricas["tasa_cumplimiento_sla_porcentaje"] == 100.0
