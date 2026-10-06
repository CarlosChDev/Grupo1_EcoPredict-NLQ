"""
Módulo de Evaluadores de Calidad de Inteligencia Artificial (IA Ops).
Contiene el motor de evaluación LLM-as-a-Judge y métricas de producción.
"""

from .llm_judge import EvaluadorCalidadIA, ResultadoJuicio, MetricasProduccionIA

__all__ = ["EvaluadorCalidadIA", "ResultadoJuicio", "MetricasProduccionIA"]
