"""
=============================================================================
EcoPredict & NLQ — Módulo de Aseguramiento de Calidad (QA / IA Ops)
Sprint 3 — Tarea T25 (#185): Auditoría de Observabilidad con Langfuse (HT-08/10)
=============================================================================
Implementa el motor de auditoría y exportación de telemetría hacia Langfuse.
Transforma las trazas de inferencia de producción y los veredictos emitidos
por el evaluador "LLM-as-a-Judge" en payloads conformes con la OpenAPI v2
de Langfuse (Traces, Generations y Scores API), modelando además los costos
económicos de tokens de Groq LLaMA 3.3 70B y Google Gemini 1.5 Flash.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from evaluators.llm_judge import EvaluadorCalidadIA, ResultadoJuicio, MetricasProduccionIA


# =============================================================================
# 1. CATÁLOGO DE PRECIOS Y COSTOS DE INFERENCIA POR TOKEN (USD)
# =============================================================================
CATALOGO_PRECIOS_TOKENS = {
    "groq-llama-3.3-70b": {
        "costo_input_por_millon": 0.59,   # $0.59 USD / 1M prompt tokens
        "costo_output_por_millon": 0.79,  # $0.79 USD / 1M completion tokens
        "sla_limite_ms": 2000
    },
    "gemini-1.5-flash": {
        "costo_input_por_millon": 0.075,  # $0.075 USD / 1M prompt tokens
        "costo_output_por_millon": 0.30,  # $0.30 USD / 1M completion tokens
        "sla_limite_ms": 5000
    }
}

SLA_MAXIMO_GLOBAL_MS = 5000  # 5 segundos SLA contractual extremo a extremo


# =============================================================================
# 2. MODELOS DE DATOS CONFORMES CON LANGFUSE OPENAPI V2
# =============================================================================
@dataclass
class LangfuseScore:
    """Representa un puntaje de evaluación vinculado a una traza en Langfuse."""
    name: str
    value: Union[float, int, bool]
    dataType: str  # "NUMERIC" o "BOOLEAN"
    comment: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LangfuseGeneration:
    """Representa una observación de inferencia LLM en Langfuse."""
    id: str
    name: str
    model: str
    promptTokens: int
    completionTokens: int
    totalTokens: int
    calculatedCostUsd: float
    latencyMs: int
    input: str
    output: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LangfuseTracePayload:
    """Estructura canónica de una Traza completa exportable a Langfuse."""
    id: str
    name: str
    timestamp: str
    sessionId: str
    userId: str
    input: str
    output: str
    tags: List[str]
    metadata: Dict[str, Any]
    generations: List[LangfuseGeneration] = field(default_factory=list)
    scores: List[LangfuseScore] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["generations"] = [g.to_dict() if hasattr(g, 'to_dict') else g for g in self.generations]
        d["scores"] = [s.to_dict() if hasattr(s, 'to_dict') else s for s in self.scores]
        return d


# =============================================================================
# 3. MOTOR AUDITOR Y SERIALIZADOR DE OBSERVABILIDAD LANGFUSE
# =============================================================================
class AuditorLangfuse:
    """
    Audita y serializa eventos de inferencia para el dashboard de Langfuse.
    """

    def __init__(self, evaluador: Optional[EvaluadorCalidadIA] = None):
        self.evaluador = evaluador or EvaluadorCalidadIA()
        self.catalogo_precios = CATALOGO_PRECIOS_TOKENS

    def calcular_costo_tokens(
        self,
        modelo: str,
        tokens_totales: int,
        ratio_input: float = 0.65
    ) -> float:
        """
        Calcula el costo monetario en USD para una llamada a LLM.
        Por estándar en sistemas NLQ, aproximadamente 65% son tokens de prompt
        (contexto RAG + system prompt) y 35% son tokens de completion (respuesta).
        """
        precios = self.catalogo_precios.get(modelo, self.catalogo_precios["groq-llama-3.3-70b"])
        prompt_tokens = int(tokens_totales * ratio_input)
        completion_tokens = max(0, tokens_totales - prompt_tokens)

        costo_in = (prompt_tokens / 1_000_000) * precios["costo_input_por_millon"]
        costo_out = (completion_tokens / 1_000_000) * precios["costo_output_por_millon"]
        return round(costo_in + costo_out, 8)

    def construir_payload_traza(
        self,
        traza_raw: Dict[str, Any],
        juicio: Optional[ResultadoJuicio] = None
    ) -> LangfuseTracePayload:
        """
        Transforma una traza de producción y su juicio evaluador en un
        payload válido para la Ingestion API de Langfuse.
        """
        if juicio is None:
            juicio = self.evaluador.juzgar_traza(traza_raw)

        traza_id = traza_raw.get("id", f"TR-GEN-{int(datetime.now().timestamp())}")
        modelo = traza_raw.get("modelo_ejecutado", "groq-llama-3.3-70b")
        latencia = int(traza_raw.get("latencia_ms", 1200))
        tokens_tot = int(traza_raw.get("tokens_totales", 150))
        es_fallback = bool(traza_raw.get("es_fallback", False))

        # Estimar prompt y completion tokens
        p_tokens = int(tokens_tot * 0.65)
        c_tokens = max(0, tokens_tot - p_tokens)
        costo_usd = self.calcular_costo_tokens(modelo, tokens_tot)

        # 1. Tags taxonómicos de Langfuse
        tags = ["ecopredict", "nlq", "sprint-3", "flujo-b", "qa-audited"]
        if es_fallback:
            tags.append("fallback-failover")
            tags.append(f"provider-google")
        else:
            tags.append(f"provider-groq")

        if juicio.alucinacion_detectada:
            tags.append("alerta-alucinacion")
        if not juicio.seguridad_aprobada:
            tags.append("alerta-seguridad")

        # 2. Generación asociada (Observation LLM)
        generation = LangfuseGeneration(
            id=f"gen-{traza_id}",
            name=f"generacion_nlq_{modelo}",
            model=modelo,
            promptTokens=p_tokens,
            completionTokens=c_tokens,
            totalTokens=tokens_tot,
            calculatedCostUsd=costo_usd,
            latencyMs=latencia,
            input=traza_raw.get("pregunta", ""),
            output=traza_raw.get("respuesta", "")
        )

        # 3. Scores de evaluación
        # Groundedness normalizado a escala 0.0 - 1.0 (5.0 -> 1.0, 1.0 -> 0.2)
        score_groundedness = round(juicio.puntaje_fidelidad / 5.0, 4)

        scores = [
            LangfuseScore(
                name="groundedness",
                value=score_groundedness,
                dataType="NUMERIC",
                comment=f"Fidelidad factual con la base de datos (Calificación: {juicio.puntaje_fidelidad}/5.0)"
            ),
            LangfuseScore(
                name="hallucination_detected",
                value=juicio.alucinacion_detectada,
                dataType="BOOLEAN",
                comment=f"Tipo: {juicio.tipo_alucinacion} | Detalle: {juicio.justificacion}"
            ),
            LangfuseScore(
                name="latency_sla_breach",
                value=(latencia > SLA_MAXIMO_GLOBAL_MS),
                dataType="BOOLEAN",
                comment=f"Latencia: {latencia}ms vs SLA máximo ({SLA_MAXIMO_GLOBAL_MS}ms)"
            ),
            LangfuseScore(
                name="user_relevance",
                value=juicio.puntaje_relevancia,
                dataType="NUMERIC",
                comment="Pertinencia semántica respecto a la consulta del usuario"
            ),
            LangfuseScore(
                name="tone_quality",
                value=juicio.puntaje_tono_ciudadano,
                dataType="NUMERIC",
                comment="Claridad y empatía ciudadana en la comunicación ambiental"
            ),
            LangfuseScore(
                name="security_guardrail_passed",
                value=juicio.seguridad_aprobada,
                dataType="BOOLEAN",
                comment="Verificación de no fuga de secretos y guardrails de seguridad"
            )
        ]

        # 4. Metadata enriquecida
        metadata = {
            "intencion_esperada": traza_raw.get("intencion_esperada", "consulta_general"),
            "es_fallback": es_fallback,
            "sla_cumplido": latencia <= SLA_MAXIMO_GLOBAL_MS,
            "entorno": "production",
            "evaluador_version": "LLM-as-a-Judge-v1.2",
            "tipo_alucinacion": juicio.tipo_alucinacion
        }
        if "contexto_bd" in traza_raw:
            metadata["contexto_bd"] = traza_raw["contexto_bd"]

        # Timestamp en formato ISO 8601 UTC
        now_iso = datetime.now(timezone.utc).isoformat()

        return LangfuseTracePayload(
            id=traza_id,
            name="nlq_consulta_ambiental",
            timestamp=now_iso,
            sessionId=f"sess-{traza_raw.get('contexto_bd', {}).get('estacion_id', 'general')}",
            userId=f"citizen-{traza_id.split('-')[-1]}",
            input=traza_raw.get("pregunta", ""),
            output=traza_raw.get("respuesta", ""),
            tags=tags,
            metadata=metadata,
            generations=[generation],
            scores=scores
        )

    def validar_contrato_langfuse(self, payload: LangfuseTracePayload) -> bool:
        """
        Valida que el payload cumpla estrictamente los campos obligatorios
        y las restricciones de esquema requeridas por Langfuse.
        """
        if not payload.id or not isinstance(payload.id, str):
            return False
        if not payload.name or not isinstance(payload.name, str):
            return False
        if not payload.timestamp or not isinstance(payload.timestamp, str):
            return False
        if not isinstance(payload.tags, list) or len(payload.tags) == 0:
            return False
        if not isinstance(payload.generations, list) or len(payload.generations) == 0:
            return False
        if not isinstance(payload.scores, list) or len(payload.scores) == 0:
            return False

        # Validar generación
        gen = payload.generations[0]
        if gen.totalTokens < 0 or gen.calculatedCostUsd < 0 or gen.latencyMs < 0:
            return False

        # Validar scores obligatorios
        nombres_scores = {s.name for s in payload.scores}
        scores_requeridos = {"groundedness", "hallucination_detected", "latency_sla_breach"}
        if not scores_requeridos.issubset(nombres_scores):
            return False

        return True

    def auditar_y_exportar_dataset(
        self,
        ruta_trazas: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Procesa el dataset completo de trazas de producción, las evalúa con el Juez,
        las serializa al formato Langfuse y emite un reporte consolidado con estadísticas
        de telemetría y costos totales acumulados.
        """
        if ruta_trazas is None:
            ruta_trazas = os.path.join(
                os.path.dirname(__file__), "..", "prompts", "production_eval_traces.json"
            )

        with open(ruta_trazas, "r", encoding="utf-8") as f:
            datos_trazas = json.load(f)

        trazas = datos_trazas.get("trazas", [])
        payloads_langfuse: List[Dict[str, Any]] = []
        costo_total_usd = 0.0
        tokens_totales = 0
        alucinaciones_total = 0
        fallbacks_total = 0
        incumplimientos_sla = 0

        for t in trazas:
            juicio = self.evaluador.juzgar_traza(t)
            payload = self.construir_payload_traza(t, juicio)
            payload_dict = payload.to_dict()
            payloads_langfuse.append(payload_dict)

            # Acumular telemetría
            gen = payload.generations[0]
            costo_total_usd += gen.calculatedCostUsd
            tokens_totales += gen.totalTokens
            if juicio.alucinacion_detectada:
                alucinaciones_total += 1
            if t.get("es_fallback", False):
                fallbacks_total += 1
            if gen.latencyMs > SLA_MAXIMO_GLOBAL_MS:
                incumplimientos_sla += 1

        total = len(trazas)
        promedio_tokens = round(tokens_totales / total, 1) if total > 0 else 0
        costo_promedio_traza = round(costo_total_usd / total, 6) if total > 0 else 0

        return {
            "plataforma": "Langfuse Observability & Telemetry API v2",
            "total_trazas_procesadas": total,
            "resumen_costos": {
                "costo_total_acumulado_usd": round(costo_total_usd, 6),
                "costo_promedio_por_traza_usd": costo_promedio_traza,
                "tokens_totales_consumidos": tokens_totales,
                "promedio_tokens_por_consulta": promedio_tokens
            },
            "metricas_calidad_observadas": {
                "tasa_alucinacion_porcentaje": round((alucinaciones_total / total) * 100, 2) if total > 0 else 0,
                "tasa_fallback_porcentaje": round((fallbacks_total / total) * 100, 2) if total > 0 else 0,
                "tasa_cumplimiento_sla_porcentaje": round(((total - incumplimientos_sla) / total) * 100, 2) if total > 0 else 100,
            },
            "trazas_exportadas": payloads_langfuse
        }
