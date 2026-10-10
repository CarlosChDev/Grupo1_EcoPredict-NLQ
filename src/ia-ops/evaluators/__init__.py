"""
Módulo de Evaluadores de Calidad de Inteligencia Artificial (IA Ops).
Contiene el motor de evaluación LLM-as-a-Judge y métricas de producción.
"""

from .llm_judge import EvaluadorCalidadIA, ResultadoJuicio, MetricasProduccionIA
from .langfuse_auditor import (
    AuditorLangfuse,
    LangfuseTracePayload,
    LangfuseGeneration,
    LangfuseScore,
    CATALOGO_PRECIOS_TOKENS
)

__all__ = [
    "EvaluadorCalidadIA",
    "ResultadoJuicio",
    "MetricasProduccionIA",
    "AuditorLangfuse",
    "LangfuseTracePayload",
    "LangfuseGeneration",
    "LangfuseScore",
    "CATALOGO_PRECIOS_TOKENS"
]
