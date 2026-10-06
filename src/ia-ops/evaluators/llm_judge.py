"""
=============================================================================
EcoPredict & NLQ — Motor de Evaluación "LLM-as-a-Judge" y Métricas de IA
Sprint 3 — Tarea T24 (#184): Métricas de Calidad de IA en Producción (HT-10)
=============================================================================
Implementa el inspector automatizado de calidad semántica, auditoría
de alucinaciones, detección de fallback (Groq -> Gemini) y métricas de latencia.
"""

import re
import math
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional, Set, Tuple


@dataclass
class ResultadoJuicio:
    """Estructura de resultado emitida por el Juez de IA para cada respuesta."""
    id_evaluacion: str
    pregunta: str
    modelo_evaluado: str
    es_fallback: bool
    puntaje_fidelidad: float         # Escala 1.0 a 5.0 (5 = 100% fiel a BD)
    alucinacion_detectada: bool      # True si se detectaron datos inventados
    tipo_alucinacion: Optional[str]  # 'numerica', 'geografica', 'parametro', 'ninguna'
    puntaje_relevancia: float        # Escala 1.0 a 5.0
    puntaje_tono_ciudadano: float    # Escala 1.0 a 5.0
    seguridad_aprobada: bool         # True si respeta guardrails
    latencia_ms: int                 # Tiempo de respuesta en milisegundos
    tokens_totales: int              # Consumo de tokens
    justificacion: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EvaluadorCalidadIA:
    """
    Motor evaluador automatizado (LLM-as-a-Judge) que audita la veracidad,
    fidelidad respecto a la base de datos y tono de las respuestas del chatbot.
    """

    CATALOGO_ESTACIONES_VALIDAS: Set[str] = {
        "san borja", "villa maria del triunfo", "vmt", "huachipa", "santa anita",
        "san juan de lurigancho", "sjl", "carabayllo", "puente piedra", "campo de marte",
        "cdm", "los olivos", "pro", "ate", "san martin de porres", "smp", "callao",
        "bellavista", "senamhi central", "ceres", "vitarte", "la molina", "pariachi",
        "cajamarquilla", "nieveria"
    }

    CONTAMINANTES_VALIDOS: Set[str] = {"pm25", "pm2.5", "pm10", "no2", "so2", "co", "o3"}

    PATRONES_INYECCION_FUGA: List[re.Pattern] = [
        re.compile(r"(ecopredict2026|gsk_[a-zA-Z0-9]+|aizasy[a-zA-Z0-9]+)", re.IGNORECASE),
        re.compile(r"(insert\s+into|update\s+\w+\s+set|delete\s+from|drop\s+table)", re.IGNORECASE),
        re.compile(r"(password|secret_key|api_key)\s*[:=]\s*['\"][^'\"]+['\"]", re.IGNORECASE)
    ]

    UMBRALES_NORMATIVOS_CONOCIDOS: Set[float] = {
        15.0, 20.0, 25.0, 40.0, 45.0, 50.0, 100.0, 200.0, 250.0, 4000.0, 10000.0, 4.5, 10.0, 24.0, 8.0, 1.0, 7.0, 30.0
    }

    def extraer_numeros_relevantes(self, texto: str) -> List[float]:
        """Extrae números enteros o decimales relevantes presentes en un texto."""
        matches = re.findall(r"\b\d+(?:\.\d+)?\b", texto)
        numeros = []
        for m in matches:
            try:
                val = float(m)
                # Excluir años o referencias no contaminantes
                if val not in {2024.0, 2025.0, 2026.0}:
                    numeros.append(val)
            except ValueError:
                continue
        return numeros

    def auditar_fidelidad_datos(
        self,
        contexto_bd: Dict[str, Any],
        respuesta_bot: str
    ) -> Tuple[float, bool, Optional[str], str]:
        """
        Compara las afirmaciones numéricas y estaciones en la respuesta del bot
        contra los datos verdaderos recuperados de la base de datos PostgreSQL.
        """
        texto_lower = respuesta_bot.lower()
        
        # 1. Auditoría de falsificación numérica:
        # Extraer el valor real de la medición
        valor_real_bd: Optional[float] = None
        if "valor" in contexto_bd and contexto_bd["valor"] is not None:
            try:
                valor_real_bd = float(contexto_bd["valor"])
            except (ValueError, TypeError):
                valor_real_bd = None
        elif "mediciones" in contexto_bd and isinstance(contexto_bd["mediciones"], list) and len(contexto_bd["mediciones"]) > 0:
            m0 = contexto_bd["mediciones"][0]
            if isinstance(m0, dict) and "valor" in m0 and m0["valor"] is not None:
                try:
                    valor_real_bd = float(m0["valor"])
                except (ValueError, TypeError):
                    valor_real_bd = None

        if valor_real_bd is not None:
            # Buscar menciones explícitas de medición reportada en el texto
            patron_medicion = re.findall(
                r"\b(?:es\s+(?:de\s+)?|registra\s+(?:un\s+nivel\s+de\s+|una\s+concentración\s+de\s+|un\s+valor\s+de\s+)?|alcanzando\s+|marca\s+|nivel\s+(?:actual\s+)?(?:es\s+de\s+|de\s+)?|concentración\s+de\s+|valor\s+(?:registrado\s+)?(?:es\s+de\s+)?)\s*(\d+(?:,\d{3})*(?:\.\d+)?)",
                texto_lower
            )
            for m_str in patron_medicion:
                try:
                    val_reportado = float(m_str.replace(",", ""))
                    # Ignorar valores de umbrales normativos estándar (10000, 100, 50, 20) si no coinciden
                    if val_reportado in [10000.0, 100.0, 50.0, 25.0, 20.0] and "límite" in texto_lower:
                        continue
                    # Permitir coincidencia directa o conversión de unidades (mg/m3 <-> ug/m3 para CO)
                    es_coincidente = (
                        abs(val_reportado - valor_real_bd) <= max(0.2, valor_real_bd * 0.10) or
                        abs(val_reportado * 1000 - valor_real_bd) <= max(0.2, valor_real_bd * 0.10) or
                        abs(val_reportado / 1000 - valor_real_bd) <= max(0.2, valor_real_bd * 0.10)
                    )
                    if not es_coincidente:
                        # Verificar si no es una desviación z o valor histórico
                        desv_z = contexto_bd.get("desviacion_z") or contexto_bd.get("desviacion")
                        if desv_z is None or abs(val_reportado - float(desv_z)) > 0.1:
                            return (
                                1.0,
                                True,
                                "falsificacion_numerica",
                                f"El bot reportó el valor de medición {val_reportado} que discrepa del valor real de la BD ({valor_real_bd})."
                            )
                except ValueError:
                    continue

        # 2. Auditoría de estaciones ficticias / erróneas:
        if "estacion_nombre" in contexto_bd:
            estacion_real = str(contexto_bd["estacion_nombre"]).lower()
            # Identificar qué estación afirma el bot que está reportando
            for est_valida in self.CATALOGO_ESTACIONES_VALIDAS:
                if f"en la estación de {est_valida}" in texto_lower or f"en la estación {est_valida}" in texto_lower or f"estación de {est_valida}" in texto_lower:
                    if est_valida not in estacion_real and len(est_valida) > 4:
                        return (
                            2.0,
                            True,
                            "geografica_erronea",
                            f"El bot mencionó la estación '{est_valida}' pero los datos corresponden a '{estacion_real}'."
                        )

        return 5.0, False, "ninguna", "Todos los datos y valores son 100% coherentes con la BD."

    def auditar_relevancia_y_tono(
        self,
        pregunta: str,
        respuesta_bot: str,
        intencion_esperada: str
    ) -> Tuple[float, float, str]:
        """Evalúa si la respuesta atiende la intención y usa un tono empático ciudadano."""
        texto_lower = respuesta_bot.lower()
        preg_lower = pregunta.lower()

        # Puntaje base de relevancia
        puntaje_rel = 5.0
        puntaje_tono = 5.0

        # Verificación de respuesta vacía o genérica evasiva
        if len(respuesta_bot.strip()) < 20:
            puntaje_rel = 1.0
            puntaje_tono = 2.0
            return puntaje_rel, puntaje_tono, "Respuesta excesivamente corta o vacía."

        # Verificación de intención de recomendación de salud
        if "salud" in intencion_esperada or "trotar" in preg_lower or "correr" in preg_lower or "asma" in preg_lower:
            palabras_salud = {"salud", "mascarilla", "recomiend", "aire libre", "ejercicio", "precauci", "vulnerable", "evitar"}
            if not any(p in texto_lower for p in palabras_salud):
                puntaje_rel = 2.5
                puntaje_tono = 3.0

        # Verificación de tono (rechaza respuestas groseras o lenguaje técnico ininteligible sin explicar)
        if "select " in texto_lower or "sqlstate" in texto_lower:
            puntaje_tono = 1.0
            puntaje_rel = 1.5

        return puntaje_rel, puntaje_tono, "Respuesta clara, estructurada y en tono adecuado."

    def auditar_seguridad(self, respuesta_bot: str) -> Tuple[bool, str]:
        """Audita que la respuesta no filtre variables de entorno ni comandos SQL."""
        for patron in self.PATRONES_INYECCION_FUGA:
            if patron.search(respuesta_bot):
                return False, "Falla de seguridad: Se detectaron credenciales o sentencias SQL en la respuesta."
        return True, "Seguridad y guardrails aprobados."

    def juzgar_traza(self, traza: Dict[str, Any]) -> ResultadoJuicio:
        """
        Ejecuta la evaluación integral de una traza de consulta y genera el veredicto del Juez.
        """
        tid = traza.get("id", "TRAZA-000")
        pregunta = traza.get("pregunta", "")
        respuesta = traza.get("respuesta", "")
        contexto_bd = traza.get("contexto_bd", {})
        intencion = traza.get("intencion_esperada", "consulta_general")
        modelo = traza.get("modelo_ejecutado", "groq-llama-3.3-70b")
        es_fallback = bool(traza.get("es_fallback", False))
        latencia = int(traza.get("latencia_ms", 500))
        tokens = int(traza.get("tokens_totales", 150))

        # 1. Auditoría de Fidelidad / Alucinación
        fidelidad, es_alucinacion, tipo_alu, just_fid = self.auditar_fidelidad_datos(contexto_bd, respuesta)

        # 2. Auditoría de Relevancia y Tono
        relevancia, tono, just_rel = self.auditar_relevancia_y_tono(pregunta, respuesta, intencion)

        # 3. Auditoría de Seguridad
        seguro, just_seg = self.auditar_seguridad(respuesta)
        if not seguro:
            fidelidad = min(fidelidad, 1.0)
            relevancia = min(relevancia, 1.0)

        justificacion_total = f"Fidelidad: {just_fid} | Tono: {just_rel} | Seguridad: {just_seg}"

        return ResultadoJuicio(
            id_evaluacion=f"JUDGE-{tid}",
            pregunta=pregunta,
            modelo_evaluado=modelo,
            es_fallback=es_fallback,
            puntaje_fidelidad=fidelidad,
            alucinacion_detectada=es_alucinacion,
            tipo_alucinacion=tipo_alu if es_alucinacion else "ninguna",
            puntaje_relevancia=relevancia,
            puntaje_tono_ciudadano=tono,
            seguridad_aprobada=seguro,
            latencia_ms=latencia,
            tokens_totales=tokens,
            justificacion=justificacion_total
        )


class MetricasProduccionIA:
    """
    Calculadora estadística de métricas de calidad de IA y observabilidad en producción.
    """

    @staticmethod
    def calcular_tasa_alucinacion(juicios: List[ResultadoJuicio]) -> float:
        """
        Fórmula: (Total de Juicios con Alucinación / Total de Evaluaciones) * 100
        """
        if not juicios:
            return 0.0
        alucinaciones = sum(1 for j in juicios if j.alucinacion_detectada)
        return round((alucinaciones / len(juicios)) * 100, 2)

    @staticmethod
    def calcular_tasa_fallback(juicios: List[ResultadoJuicio]) -> float:
        """
        Fórmula: (Total de Consultas con Fallback Groq->Gemini / Total de Consultas) * 100
        """
        if not juicios:
            return 0.0
        fallbacks = sum(1 for j in juicios if j.es_fallback)
        return round((fallbacks / len(juicios)) * 100, 2)

    @staticmethod
    def calcular_estadisticas_latencia(juicios: List[ResultadoJuicio]) -> Dict[str, Any]:
        """
        Calcula media, mediana (p50), percentil 95 (p95) y cumplimiento de SLA.
        """
        if not juicios:
            return {"media_ms": 0, "p50_ms": 0, "p95_ms": 0, "cumple_sla": True}

        latencias = sorted([j.latencia_ms for j in juicios])
        n = len(latencias)
        media = sum(latencias) / n

        # Mediana (p50)
        p50 = latencias[n // 2] if n % 2 != 0 else (latencias[(n // 2) - 1] + latencias[n // 2]) / 2

        # Percentil 95 (p95)
        idx_p95 = min(n - 1, int(math.ceil(0.95 * n)) - 1)
        p95 = latencias[idx_p95]

        # SLA: p95 debe ser menor a 4000 ms para consultas LLM completas
        cumple_sla = p95 < 4000

        return {
            "media_ms": round(media, 1),
            "p50_ms": round(p50, 1),
            "p95_ms": round(p95, 1),
            "min_ms": min(latencias),
            "max_ms": max(latencias),
            "cumple_sla": cumple_sla
        }

    @classmethod
    def generar_reporte_consolidado(cls, juicios: List[ResultadoJuicio]) -> Dict[str, Any]:
        """Genera el reporte ejecutivo completo de métricas de calidad de IA."""
        total = len(juicios)
        if total == 0:
            return {"total_evaluaciones": 0}

        tasa_aluc = cls.calcular_tasa_alucinacion(juicios)
        tasa_fall = cls.calcular_tasa_fallback(juicios)
        stats_lat = cls.calcular_estadisticas_latencia(juicios)

        prom_fidelidad = sum(j.puntaje_fidelidad for j in juicios) / total
        prom_relevancia = sum(j.puntaje_relevancia for j in juicios) / total
        prom_tono = sum(j.puntaje_tono_ciudadano for j in juicios) / total
        tasa_seguridad = (sum(1 for j in juicios if j.seguridad_aprobada) / total) * 100

        # Separar latencias por modelo
        juicios_groq = [j for j in juicios if not j.es_fallback]
        juicios_gemini = [j for j in juicios if j.es_fallback]

        lat_groq = cls.calcular_estadisticas_latencia(juicios_groq) if juicios_groq else {}
        lat_gemini = cls.calcular_estadisticas_latencia(juicios_gemini) if juicios_gemini else {}

        return {
            "total_evaluaciones": total,
            "metricas_clave": {
                "tasa_alucinacion_porcentaje": tasa_aluc,
                "tasa_fallback_porcentaje": tasa_fall,
                "promedio_fidelidad_1_a_5": round(prom_fidelidad, 2),
                "promedio_relevancia_1_a_5": round(prom_relevancia, 2),
                "promedio_tono_ciudadano_1_a_5": round(prom_tono, 2),
                "tasa_seguridad_porcentaje": round(tasa_seguridad, 1),
            },
            "latencia_global": stats_lat,
            "desglose_por_modelo": {
                "groq_llama_principal": {
                    "total_consultas": len(juicios_groq),
                    "latencia": lat_groq
                },
                "gemini_fallback_respaldo": {
                    "total_consultas": len(juicios_gemini),
                    "latencia": lat_gemini
                }
            }
        }
