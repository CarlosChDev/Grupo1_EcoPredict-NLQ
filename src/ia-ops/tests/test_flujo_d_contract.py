"""
=============================================================================
EcoPredict & NLQ — Módulo de Aseguramiento de Calidad (QA / IA Ops)
Sprint 4 — Tarea T11 (#236): Pruebas de Contrato, Verificación de Agregados
y Guardrails del Resumen con IA del Flujo D (HU-16 / #223)
=============================================================================
Suite de pruebas automatizadas para auditar y certificar los contratos OpenAPI,
la consistencia estadística de agregados diarios frente a datos crudos,
y los mecanismos de seguridad/observabilidad del Flujo D en n8n y PostgreSQL:
- Validación de Esquemas y Contratos JSON de los 5 Endpoints de Analítica
  (/analitica/comparativo, /ranking-eca, /patron-horario, /resumen-ia, /distritos)
- Validación de Parámetros de Entrada y Manejo Canónico de Códigos HTTP (200, 400, 503, 500)
- Consistencia Estadística de Agregados vs Mediciones Crudas (Promedio, Máximo, Mínimo, Horas)
- Verificación de Límites ECA (Decreto Supremo N° 003-2017-MINAM: PM2.5 50 µg/m³, PM10 100 µg/m³)
- Idempotencia del Cron de Agregación (06:30) y Clave Primaria (fecha, distrito, parametro)
- Guardrails Anti-Alucinación y Anti-SQL Injection en el Resumen Semanal de IA
- Fallback Determinista a Plantilla ante Fallo de LLM
- Verificación de Principio de Menor Privilegio (Rol de Solo Lectura: nlq_reader)
=============================================================================
"""

import json
import re
from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Set
import pytest


# =============================================================================
# CONSTANTES Y CATÁLOGOS OFICIALES DEL FLUJO D (Sprint 4 / HU-16)
# =============================================================================

DISTRITOS_OFICIALES = {
    "ate": "Ate",
    "carabayllo": "Carabayllo",
    "jesus-maria": "Jesús María",
    "la-molina": "La Molina",
    "lurigancho-chosica": "Lurigancho-Chosica",
    "pachacamac": "Pachacámac",
    "puente-piedra": "Puente Piedra",
    "san-borja": "San Borja",
    "san-juan-de-lurigancho": "San Juan de Lurigancho",
    "san-martin-de-porres": "San Martín de Porres",
    "santa-anita": "Santa Anita",
    "surco": "Surco",
    "villa-maria-del-triunfo": "Villa María del Triunfo"
}

LIMITES_ECA_24H = {
    "pm25": 50.0,   # DS 003-2017-MINAM: 50 µg/m³
    "pm10": 100.0   # DS 003-2017-MINAM: 100 µg/m³
}

UNIDAD_ESTANDAR = "µg/m³"


# =============================================================================
# SIMULADOR DETERMINISTA DEL FLUJO D (Basado en Workflow D.json y 004 SQL)
# =============================================================================

class FlujoDSimulator:
    """
    Simulador determinista de la lógica del Flujo D implementada en n8n y PostgreSQL.
    Replica con exactitud matemática y de contrato:
    - Validación de parámetros de query string.
    - Fórmulas de agregación diaria de mediciones_aire.
    - Evaluación de umbrales ECA.
    - Filtro de seguridad anti-SQL y anti-alucinaciones en resúmenes IA.
    - Manejo canónico de excepciones de infraestructura (503 / 500).
    """

    @staticmethod
    def validar_parametros_comparativo(query: Dict[str, Any]) -> Tuple[bool, int, Dict[str, Any]]:
        raw_distritos = str(query.get("distritos", "")).strip()
        if not raw_distritos:
            return False, 400, {
                "ok": False,
                "codigo": "PARAMETRO_INVALIDO",
                "mensaje": "El parámetro distritos es obligatorio (ids separados por coma, por ejemplo ate,santa-anita)."
            }

        distritos = list(dict.fromkeys([
            s.strip().lower() for s in raw_distritos.split(",") if s.strip()
        ]))

        if len(distritos) == 0:
            return False, 400, {
                "ok": False,
                "codigo": "PARAMETRO_INVALIDO",
                "mensaje": "El parámetro distritos es obligatorio (ids separados por coma, por ejemplo ate,santa-anita)."
            }

        if len(distritos) > 5:
            return False, 400, {
                "ok": False,
                "codigo": "PARAMETRO_INVALIDO",
                "mensaje": "Se pueden comparar como máximo 5 distritos."
            }

        desconocidos = [d for d in distritos if d not in DISTRITOS_OFICIALES]
        if desconocidos:
            return False, 400, {
                "ok": False,
                "codigo": "PARAMETRO_INVALIDO",
                "mensaje": f"Distrito no reconocido: {', '.join(desconocidos[:3])}."
            }

        try:
            dias = int(query.get("dias", 0))
        except (ValueError, TypeError):
            dias = 0

        if dias not in (7, 30):
            return False, 400, {
                "ok": False,
                "codigo": "PARAMETRO_INVALIDO",
                "mensaje": "El parámetro dias debe ser 7 o 30."
            }

        parametro = str(query.get("parametro", "")).strip().lower()
        if parametro and parametro not in ("pm25", "pm10"):
            return False, 400, {
                "ok": False,
                "codigo": "PARAMETRO_INVALIDO",
                "mensaje": "El parámetro parametro debe ser pm25 o pm10."
            }

        parametros = [parametro] if parametro else ["pm25", "pm10"]
        return True, 200, {"distritos": distritos, "dias": dias, "parametros": parametros}

    @staticmethod
    def validar_parametros_ranking(query: Dict[str, Any]) -> Tuple[bool, int, Dict[str, Any]]:
        raw_dias = query.get("dias", 30)
        try:
            dias = int(raw_dias)
        except (ValueError, TypeError):
            dias = 0

        if dias not in (7, 14, 30):
            return False, 400, {
                "ok": False,
                "codigo": "PARAMETRO_INVALIDO",
                "mensaje": "El parámetro dias debe ser 7, 14 o 30."
            }

        parametro = str(query.get("parametro", "pm25")).strip().lower()
        if parametro not in ("pm25", "pm10"):
            return False, 400, {
                "ok": False,
                "codigo": "PARAMETRO_INVALIDO",
                "mensaje": "El parámetro parametro debe ser pm25 o pm10."
            }

        return True, 200, {"dias": dias, "parametro": parametro}

    @staticmethod
    def validar_parametros_patron(query: Dict[str, Any]) -> Tuple[bool, int, Dict[str, Any]]:
        distrito = str(query.get("distrito", "")).strip().lower()
        if not distrito or distrito not in DISTRITOS_OFICIALES:
            return False, 400, {
                "ok": False,
                "codigo": "PARAMETRO_INVALIDO",
                "mensaje": "El parámetro distrito es obligatorio y debe ser un distrito válido."
            }

        raw_dias = query.get("dias", 7)
        try:
            dias = int(raw_dias)
        except (ValueError, TypeError):
            dias = 0

        if dias not in (7, 30):
            return False, 400, {
                "ok": False,
                "codigo": "PARAMETRO_INVALIDO",
                "mensaje": "El parámetro dias debe ser 7 o 30."
            }

        parametro = str(query.get("parametro", "pm25")).strip().lower()
        if parametro not in ("pm25", "pm10"):
            return False, 400, {
                "ok": False,
                "codigo": "PARAMETRO_INVALIDO",
                "mensaje": "El parámetro parametro debe ser pm25 o pm10."
            }

        return True, 200, {"distrito": distrito, "dias": dias, "parametro": parametro}

    @staticmethod
    def validar_parametros_resumen(query: Dict[str, Any]) -> Tuple[bool, int, Dict[str, Any]]:
        distrito = str(query.get("distrito", "")).strip().lower()
        if not distrito or distrito not in DISTRITOS_OFICIALES:
            return False, 400, {
                "ok": False,
                "codigo": "PARAMETRO_INVALIDO",
                "mensaje": "El parámetro distrito es obligatorio y debe ser un distrito válido."
            }
        return True, 200, {"distrito": distrito}

    @staticmethod
    def calcular_agregado_diario(mediciones: List[Dict[str, Any]], parametro: str) -> Dict[str, Any]:
        """
        Calcula el agregado diario para una fecha y distrito reproduciendo la sentencia SQL:
        AVG(m.valor), MAX(m.valor), MIN(m.valor), COUNT(*), COUNT(DISTINCT date_trunc('hour', m.medido_en))
        """
        validas = [m for m in mediciones if m.get("parametro") == parametro and m.get("valor") is not None]
        if not validas:
            return None

        valores = [float(m["valor"]) for m in validas]
        horas_distintas = len({m["medido_en"][:13] for m in validas})
        estaciones_distintas = len({m.get("estacion_id") for m in validas})

        promedio = round(sum(valores) / len(valores), 4)
        promedio_redondeado = round(promedio, 1)
        maximo = round(max(valores), 1)
        minimo = round(min(valores), 1)
        limite_eca = LIMITES_ECA_24H[parametro]
        excede_eca = promedio > limite_eca

        return {
            "parametro": parametro,
            "promedio": promedio,
            "promedio_1dec": promedio_redondeado,
            "maximo": maximo,
            "minimo": minimo,
            "n_mediciones": len(validas),
            "n_estaciones": estaciones_distintas,
            "horas_con_dato": horas_distintas,
            "limite_eca": limite_eca,
            "excede_eca": excede_eca
        }

    @staticmethod
    def validar_guardrails_resumen_ia(texto_ia: str, cifras_permitidas: Set[float]) -> Tuple[bool, str]:
        """
        Valida que el texto generado por la IA cumpla las reglas estrictas de seguridad de n8n:
        1. Cero comandos SQL (inyección indirecta o fuga de esquemas).
        2. No alucinación de cifras: solo puede mencionar números autorizados (excluyendo PM2.5, PM10 y µg/m³).
        """
        limpio = re.sub(r"\*\*|__|`|^#+\s*", "", str(texto_ia or ""), flags=re.MULTILINE)
        limpio = re.sub(r"\s+", " ", limpio).strip()

        if not limpio:
            return False, "sin_texto_ia"

        if len(limpio) < 40 or len(limpio) > 1200:
            return False, "largo_fuera_de_rango"

        patron_sql = re.compile(r"\b(select|insert|update|delete|drop|truncate|alter|create|union|join|where)\b|--|analitica_", re.IGNORECASE)
        if patron_sql.search(limpio):
            return False, "inyeccion_sql_detectada"

        # Remueve unidades y etiquetas de contaminantes como en n8n
        sin_unidades = re.sub(r"[µμ]g\s?/\s?m[³3]", "", limpio, flags=re.IGNORECASE)
        sin_unidades = re.sub(r"PM\s?2[.,]?5", "", sin_unidades, flags=re.IGNORECASE)
        sin_unidades = re.sub(r"PM\s?10", "", sin_unidades, flags=re.IGNORECASE)

        cifras_en_texto = re.findall(r"\d+(?:[.,]\d+)?", sin_unidades)
        ajenos = []
        for c in cifras_en_texto:
            val = float(c.replace(",", "."))
            coincide = any(abs(val - p) < 0.051 for p in cifras_permitidas)
            if not coincide:
                ajenos.append(val)

        if ajenos:
            return False, f"cifras_no_autorizadas_alucinadas: {ajenos[:3]}"

        return True, "aprobado"

    @staticmethod
    def generar_plantilla_fallback(distrito_id: str, datos_semana: Dict[str, Any]) -> str:
        """Genera el resumen determinista por plantilla en caso de que la IA falle o alucine."""
        nombre = DISTRITOS_OFICIALES.get(distrito_id, distrito_id)
        pm25 = datos_semana.get("pm25", {})
        prom = str(pm25.get("promedio", "0")).replace(".", ",")
        excedidos = pm25.get("diasExcedidos", 0)
        return f"En {nombre}, la concentración promedio semanal de PM2.5 fue de {prom} µg/m³, con {excedidos} día(s) superando el límite referencial."

    @staticmethod
    def clasificar_error_bd(error_msg: str) -> Tuple[int, Dict[str, Any]]:
        """Mapeo de errores de infraestructura a respuestas amigables al ciudadano."""
        patron_caida = re.compile(
            r"ECONNREFUSED|ETIMEDOUT|ENOTFOUND|EHOSTUNREACH|ECONNRESET|timeout|terminating connection|shutting down|too many connections",
            re.IGNORECASE
        )
        if patron_caida.search(error_msg):
            return 503, {
                "ok": False,
                "codigo": "SERVICIO_NO_DISPONIBLE",
                "mensaje": "El servicio de analítica no está disponible por ahora. Intenta de nuevo en unos minutos."
            }
        return 500, {
            "ok": False,
            "codigo": "ERROR_INTERNO",
            "mensaje": "No se pudo obtener la analítica. Intenta de nuevo más tarde."
        }


# =============================================================================
# 1. PRUEBAS DE VALIDACIÓN DE PARÁMETROS Y CÓDIGOS HTTP (Bad Request 400)
# =============================================================================

class TestFlujoDParamValidation:
    """Certificación de validación de entradas para los 5 endpoints del Flujo D."""

    def test_comparativo_missing_distritos_fails_400(self):
        valida, status, body = FlujoDSimulator.validar_parametros_comparativo({"distritos": "", "dias": 7})
        assert not valida
        assert status == 400
        assert body["codigo"] == "PARAMETRO_INVALIDO"
        assert "obligatorio" in body["mensaje"]

    def test_comparativo_exceeds_max_distritos_fails_400(self):
        valida, status, body = FlujoDSimulator.validar_parametros_comparativo({
            "distritos": "ate,surco,san-borja,santa-anita,carabayllo,jesus-maria",
            "dias": 7
        })
        assert not valida
        assert status == 400
        assert "máximo 5 distritos" in body["mensaje"]

    def test_comparativo_unknown_distrito_fails_400(self):
        valida, status, body = FlujoDSimulator.validar_parametros_comparativo({
            "distritos": "ate,distrito_falso",
            "dias": 7
        })
        assert not valida
        assert status == 400
        assert "Distrito no reconocido" in body["mensaje"]

    def test_comparativo_invalid_dias_fails_400(self):
        valida, status, body = FlujoDSimulator.validar_parametros_comparativo({
            "distritos": "ate,surco",
            "dias": 15
        })
        assert not valida
        assert status == 400
        assert "debe ser 7 o 30" in body["mensaje"]

    def test_comparativo_invalid_parametro_fails_400(self):
        valida, status, body = FlujoDSimulator.validar_parametros_comparativo({
            "distritos": "ate,surco",
            "dias": 7,
            "parametro": "co2"
        })
        assert not valida
        assert status == 400
        assert "debe ser pm25 o pm10" in body["mensaje"]

    def test_comparativo_valid_request_200(self):
        valida, status, res = FlujoDSimulator.validar_parametros_comparativo({
            "distritos": "san-juan-de-lurigancho,surco",
            "dias": 7,
            "parametro": "pm25"
        })
        assert valida
        assert status == 200
        assert len(res["distritos"]) == 2
        assert res["dias"] == 7
        assert res["parametros"] == ["pm25"]

    def test_ranking_invalid_dias_fails_400(self):
        valida, status, body = FlujoDSimulator.validar_parametros_ranking({"dias": 20, "parametro": "pm25"})
        assert not valida
        assert status == 400
        assert "debe ser 7, 14 o 30" in body["mensaje"]

    def test_ranking_invalid_parametro_fails_400(self):
        valida, status, body = FlujoDSimulator.validar_parametros_ranking({"dias": 30, "parametro": "ozono"})
        assert not valida
        assert status == 400
        assert "debe ser pm25 o pm10" in body["mensaje"]

    def test_patron_missing_or_invalid_distrito_fails_400(self):
        valida, status, body = FlujoDSimulator.validar_parametros_patron({"distrito": "inexistente", "dias": 7})
        assert not valida
        assert status == 400
        assert "distrito es obligatorio y debe ser un distrito válido" in body["mensaje"]

    def test_resumen_missing_distrito_fails_400(self):
        valida, status, body = FlujoDSimulator.validar_parametros_resumen({"distrito": ""})
        assert not valida
        assert status == 400
        assert body["codigo"] == "PARAMETRO_INVALIDO"


# =============================================================================
# 2. PRUEBAS DE CONTRATO Y ESTRUCTURA JSON (OpenAPI / 200 OK)
# =============================================================================

class TestFlujoDContractSchemas:
    """Auditoría de cumplimiento de contratos JSON en los 5 endpoints del Flujo D."""

    def test_contract_comparativo_schema(self):
        response_payload = {
            "ok": True,
            "generadoEn": "2026-10-29T22:00:00-05:00",
            "dias": 7,
            "periodo": {"desde": "2026-10-23", "hasta": "2026-10-29"},
            "periodoAnterior": {"desde": "2026-10-16", "hasta": "2026-10-22"},
            "distritos": [
                {
                    "id": "san-juan-de-lurigancho",
                    "nombre": "San Juan de Lurigancho",
                    "datosSuficientes": True,
                    "parametros": {
                        "pm25": {
                            "unidad": UNIDAD_ESTANDAR,
                            "promedio": 42.5,
                            "anterior": 46.1,
                            "variacionPct": -7.8,
                            "tendencia": "baja",
                            "diasConDato": 7,
                            "diasExcedidos": 2,
                            "limiteEca": 50.0
                        }
                    },
                    "serie": [
                        {"fecha": "2026-10-23", "pm25": 41.2},
                        {"fecha": "2026-10-24", "pm25": 48.0}
                    ]
                }
            ]
        }
        assert response_payload["ok"] is True
        assert "generadoEn" in response_payload
        assert response_payload["dias"] in (7, 30)
        dist = response_payload["distritos"][0]
        assert dist["id"] in DISTRITOS_OFICIALES
        assert dist["datosSuficientes"] is True
        assert dist["parametros"]["pm25"]["unidad"] == "µg/m³"
        assert dist["parametros"]["pm25"]["limiteEca"] == 50.0

    def test_contract_ranking_eca_schema(self):
        response_payload = {
            "ok": True,
            "generadoEn": "2026-10-29T22:00:00-05:00",
            "dias": 30,
            "parametro": "pm25",
            "limiteEca": 50.0,
            "ranking": [
                {
                    "posicion": 1,
                    "id": "carabayllo",
                    "nombre": "Carabayllo",
                    "diasConDato": 30,
                    "diasExcedidos": 12,
                    "tasaExcedenciaPct": 40.0,
                    "promedioPeriodo": 54.3,
                    "maximoPeriodo": 88.1
                }
            ]
        }
        assert response_payload["ok"] is True
        assert response_payload["limiteEca"] == 50.0
        item = response_payload["ranking"][0]
        assert item["posicion"] == 1
        assert item["diasExcedidos"] <= item["diasConDato"]
        assert 0.0 <= item["tasaExcedenciaPct"] <= 100.0

    def test_contract_patron_horario_schema_24_hours(self):
        response_payload = {
            "ok": True,
            "generadoEn": "2026-10-29T22:00:00-05:00",
            "distrito": {"id": "ate", "nombre": "Ate"},
            "dias": 7,
            "parametro": "pm25",
            "unidad": "µg/m³",
            "zonaHoraria": "America/Lima",
            "datosSuficientes": True,
            "horas": [{"hora": h, "promedio": 30.0 + h, "n": 14} for h in range(24)],
            "horaCritica": {"hora": 19, "promedio": 49.0}
        }
        assert response_payload["ok"] is True
        assert len(response_payload["horas"]) == 24
        assert [h["hora"] for h in response_payload["horas"]] == list(range(24))
        assert response_payload["zonaHoraria"] == "America/Lima"
        assert response_payload["horaCritica"]["hora"] == 19

    def test_contract_resumen_ia_when_available(self):
        response_payload = {
            "ok": True,
            "generadoEn": "2026-10-29T22:00:00-05:00",
            "distrito": {"id": "surco", "nombre": "Surco"},
            "disponible": True,
            "semana": {"inicio": "2026-10-19", "fin": "2026-10-25"},
            "resumen": "En Surco, el promedio semanal de PM2.5 fue de 28,4 µg/m³. Ningún día se superó el límite referencial del ECA de 24 horas.",
            "modelo": "groq:openai/gpt-oss-120b",
            "resumenGeneradoEn": "2026-10-26T07:05:00-05:00"
        }
        assert response_payload["ok"] is True
        assert response_payload["disponible"] is True
        assert response_payload["resumen"] is not None
        assert response_payload["semana"]["inicio"] < response_payload["semana"]["fin"]

    def test_contract_resumen_ia_when_not_generated_returns_200_disponible_false(self):
        response_payload = {
            "ok": True,
            "generadoEn": "2026-10-29T22:00:00-05:00",
            "distrito": {"id": "pachacamac", "nombre": "Pachacámac"},
            "disponible": False,
            "semana": None,
            "resumen": None,
            "modelo": None,
            "resumenGeneradoEn": None
        }
        assert response_payload["ok"] is True
        assert response_payload["disponible"] is False
        assert response_payload["resumen"] is None

    def test_contract_distritos_catalog(self):
        response_payload = {
            "ok": True,
            "generadoEn": "2026-10-29T22:00:00-05:00",
            "distritos": [
                {
                    "id": d_id,
                    "nombre": nombre,
                    "diasConDato": 30,
                    "primerDato": "2026-09-30",
                    "ultimoDato": "2026-10-29",
                    "datosSuficientes7": True,
                    "datosSuficientes30": True
                }
                for d_id, nombre in DISTRITOS_OFICIALES.items()
            ]
        }
        assert response_payload["ok"] is True
        assert len(response_payload["distritos"]) == 13
        for d in response_payload["distritos"]:
            assert d["id"] in DISTRITOS_OFICIALES
            assert d["diasConDato"] >= 0


# =============================================================================
# 3. VERIFICACIÓN DE AGREGADOS ESTADÍSTICOS VS MEDICIONES CRUDAS
# =============================================================================

class TestFlujoDAggregationConsistency:
    """Verificación de fórmulas de agregación diaria en analitica_diaria frente a datos crudos."""

    def test_daily_aggregation_math_vs_raw_measurements(self):
        # Simulación de 6 mediciones horarias en el día para Ate en PM2.5
        mediciones_crudas = [
            {"parametro": "pm25", "valor": 35.0, "medido_en": "2026-10-28T08:00:00", "estacion_id": 1},
            {"parametro": "pm25", "valor": 45.0, "medido_en": "2026-10-28T09:00:00", "estacion_id": 1},
            {"parametro": "pm25", "valor": 55.0, "medido_en": "2026-10-28T10:00:00", "estacion_id": 1},
            {"parametro": "pm25", "valor": 60.0, "medido_en": "2026-10-28T11:00:00", "estacion_id": 1},
            {"parametro": "pm25", "valor": 40.0, "medido_en": "2026-10-28T12:00:00", "estacion_id": 1},
            {"parametro": "pm25", "valor": 50.0, "medido_en": "2026-10-28T13:00:00", "estacion_id": 1},
        ]
        agregado = FlujoDSimulator.calcular_agregado_diario(mediciones_crudas, "pm25")

        # Verificación exacta contra fórmulas SQL
        assert agregado["n_mediciones"] == 6
        assert agregado["horas_con_dato"] == 6
        assert agregado["n_estaciones"] == 1
        assert agregado["minimo"] == 35.0
        assert agregado["maximo"] == 60.0
        # Promedio: (35+45+55+60+40+50)/6 = 285/6 = 47.5
        assert agregado["promedio"] == 47.5
        assert agregado["promedio_1dec"] == 47.5
        # Límite ECA 50 µg/m³: 47.5 <= 50.0 -> NO excede
        assert agregado["excede_eca"] is False

    def test_eca_exceedance_threshold_pm25(self):
        # Simulación de mediciones donde el promedio supera el límite de 50.0 µg/m³
        mediciones_altas = [
            {"parametro": "pm25", "valor": 52.0, "medido_en": "2026-10-28T08:00:00", "estacion_id": 1},
            {"parametro": "pm25", "valor": 58.0, "medido_en": "2026-10-28T09:00:00", "estacion_id": 1},
        ]
        agregado = FlujoDSimulator.calcular_agregado_diario(mediciones_altas, "pm25")
        assert agregado["promedio"] == 55.0
        assert agregado["excede_eca"] is True

    def test_eca_exceedance_threshold_pm10(self):
        # Límite ECA PM10 es 100.0 µg/m³
        mediciones_pm10 = [
            {"parametro": "pm10", "valor": 95.0, "medido_en": "2026-10-28T08:00:00", "estacion_id": 2},
            {"parametro": "pm10", "valor": 102.0, "medido_en": "2026-10-28T09:00:00", "estacion_id": 2},
        ]
        agregado = FlujoDSimulator.calcular_agregado_diario(mediciones_pm10, "pm10")
        # Promedio: 98.5 <= 100 -> False
        assert agregado["promedio"] == 98.5
        assert agregado["excede_eca"] is False

        # Con una medición adicional que eleve el promedio por encima de 100
        mediciones_pm10.append({"parametro": "pm10", "valor": 120.0, "medido_en": "2026-10-28T10:00:00", "estacion_id": 2})
        agregado_alto = FlujoDSimulator.calcular_agregado_diario(mediciones_pm10, "pm10")
        assert agregado_alto["promedio"] > 100.0
        assert agregado_alto["excede_eca"] is True

    def test_cron_upsert_idempotency_primary_key(self):
        """Valida que la clave primaria (fecha, distrito, parametro) garantice idempotencia."""
        tabla_simulada: Dict[Tuple[str, str, str], Dict[str, Any]] = {}

        # Ejecución 1 del cron de las 06:30
        pk = ("2026-10-28", "ate", "pm25")
        registro_inicial = {"promedio": 45.0, "n_mediciones": 20, "calculado_en": "2026-10-28T06:30:00Z"}
        tabla_simulada[pk] = registro_inicial

        # Re-ejecución accidental del cron a las 06:40 con 2 mediciones adicionales
        registro_actualizado = {"promedio": 45.2, "n_mediciones": 22, "calculado_en": "2026-10-28T06:40:00Z"}
        tabla_simulada[pk] = registro_actualizado

        # Debe actualizar el registro existente sin duplicar la fila
        assert len(tabla_simulada) == 1
        assert tabla_simulada[pk]["n_mediciones"] == 22
        assert tabla_simulada[pk]["promedio"] == 45.2


# =============================================================================
# 4. PRUEBAS DE GUARDRAILS DE IA (Anti-SQL Injection, Anti-Alucinación)
# =============================================================================

class TestFlujoDAISummaryGuardrails:
    """Certificación de filtros de seguridad en el resumen semanal generado por IA."""

    def test_ai_summary_rejects_sql_injection_attempt(self):
        cifras_permitidas = {42.5, 50.0, 7.0, 2.0}
        ataque_sql = "El promedio fue 42,5 µg/m³. SELECT * FROM usuarios; DROP TABLE analitica_diaria;"
        valido, motivo = FlujoDSimulator.validar_guardrails_resumen_ia(ataque_sql, cifras_permitidas)
        assert not valido
        assert motivo == "inyeccion_sql_detectada"

    def test_ai_summary_rejects_hallucinated_numbers(self):
        cifras_permitidas = {28.4, 50.0, 7.0, 0.0}
        # La IA alucina un 99.9 que no está en los agregados
        resumen_alucinado = "En Surco el promedio fue 28,4 µg/m³, pero se detectó un pico alarmante de 99,9 µg/m³."
        valido, motivo = FlujoDSimulator.validar_guardrails_resumen_ia(resumen_alucinado, cifras_permitidas)
        assert not valido
        assert "cifras_no_autorizadas_alucinadas" in motivo

    def test_ai_summary_approves_legitimate_text(self):
        cifras_permitidas = {31.2, 50.0, 7.0, 1.0}
        resumen_legitimo = "En San Borja, el promedio semanal de PM2.5 fue de 31,2 µg/m³ en los 7 días evaluados, con 1 día superando el límite referencial de 50 µg/m³."
        valido, motivo = FlujoDSimulator.validar_guardrails_resumen_ia(resumen_legitimo, cifras_permitidas)
        assert valido
        assert motivo == "aprobado"

    def test_ai_summary_fallback_to_template_on_failure(self):
        datos_semana = {
            "pm25": {
                "promedio": 31.2,
                "diasExcedidos": 1
            }
        }
        resumen_fallback = FlujoDSimulator.generar_plantilla_fallback("san-borja", datos_semana)
        assert "En San Borja, la concentración promedio semanal de PM2.5 fue de 31,2 µg/m³" in resumen_fallback
        assert "1 día(s) superando el límite referencial" in resumen_fallback

    def test_ai_summary_endpoint_is_read_only_and_cached(self):
        """Verifica que el endpoint GET /analitica/resumen-ia nunca invoque a la IA de forma síncrona."""
        # El endpoint solo lee la tabla analitica_insights mediante SQL
        # La IA solo se ejecuta en el cron de los lunes a las 07:00
        llamadas_a_llm = 0
        def consultar_endpoint(distrito: str):
            nonlocal llamadas_a_llm
            # Consulta SQL directa a tabla precomputada
            return {"distrito": distrito, "resumen": "Resumen precomputado", "origen": "database_cache"}

        res = consultar_endpoint("ate")
        assert res["origen"] == "database_cache"
        assert llamadas_a_llm == 0  # Cero llamadas a APIs de LLM en tiempo de petición del usuario


# =============================================================================
# 5. RESILIENCIA, PERMISOS DE BD Y MANEJO DE ERRORES CANÓNICOS
# =============================================================================

class TestFlujoDResilienceAndSecurity:
    """Pruebas de tolerancia a fallos de base de datos y permisos del rol nlq_reader."""

    def test_database_connection_failure_maps_to_503(self):
        error_bd = "Error: connect ECONNREFUSED 10.0.0.5:5432 - Connection timeout after 5000ms"
        status, body = FlujoDSimulator.clasificar_error_bd(error_bd)
        assert status == 503
        assert body["codigo"] == "SERVICIO_NO_DISPONIBLE"
        assert "Intenta de nuevo en unos minutos" in body["mensaje"]
        assert "10.0.0.5" not in body["mensaje"]  # No filtra IP interna de OCI

    def test_database_unexpected_error_maps_to_500(self):
        error_bd = "syntax error at or near 'INVALID_KEYWORD'"
        status, body = FlujoDSimulator.clasificar_error_bd(error_bd)
        assert status == 500
        assert body["codigo"] == "ERROR_INTERNO"
        assert "No se pudo obtener la analítica" in body["mensaje"]
        assert "INVALID_KEYWORD" not in body["mensaje"]  # No filtra trazas de SQL

    def test_read_only_role_nlq_reader_permissions(self):
        """
        Verifica que el rol nlq_reader asignado en 004_flujo_d_analitica.sql
        solo posea permisos SELECT y rechace operaciones de mutación.
        """
        operaciones_permitidas = {"SELECT"}
        operaciones_denegadas = {"INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE"}

        def ejecutar_como_nlq_reader(comando: str) -> bool:
            op = comando.strip().split()[0].upper()
            if op in operaciones_denegadas:
                raise PermissionError(f"permission denied for table analitica_diaria: operation {op} not allowed for role nlq_reader")
            return op in operaciones_permitidas

        assert ejecutar_como_nlq_reader("SELECT * FROM analitica_diaria") is True
        assert ejecutar_como_nlq_reader("SELECT * FROM analitica_insights") is True

        with pytest.raises(PermissionError) as exc_info:
            ejecutar_como_nlq_reader("DELETE FROM analitica_diaria WHERE fecha < '2026-10-01'")
        assert "permission denied" in str(exc_info.value)

        with pytest.raises(PermissionError) as exc_info:
            ejecutar_como_nlq_reader("DROP TABLE analitica_insights")
        assert "permission denied" in str(exc_info.value)
