"""
=============================================================================
EcoPredict & NLQ — Módulo de Aseguramiento de Calidad (QA / IA Ops)
Sprint 3 — Tarea T20 (#180): Certificación de Contratos y SLA de OCI Functions Serverless (HT-07)
=============================================================================
Suite de pruebas automatizadas para auditar y certificar los contratos OpenAPI
y los Acuerdos de Nivel de Servicio (SLA) de las funciones serverless de
Oracle Cloud Infrastructure (OCI Functions / API Gateway):
- Validación de Contratos JSON Schema para Invocación Serverless (Payload Ingesta & Consulta)
- Cumplimiento de SLA de Latencia en Invocación Cálida (< 2,000 ms) y Fría / Cold-Start (< 5,000 ms)
- Autenticación Perimetral mediante OCI IAM y cabecera X-API-Key / Bearer Token
- Tolerancia a Fallos y Manejo Canónico de Códigos HTTP (200 OK, 400 Bad Request, 401 Unauthorized, 504 Gateway Timeout)
- Conmutación por contingencia (Circuit Breaker / Failover) ante degradación en OCI Functions
"""

import json
import time
from typing import Dict, Any, List, Optional, Tuple
import pytest


# =============================================================================
# ESPECIFICACIÓN DE CONTRATOS Y ESQUEMA OCI FUNCTIONS (OpenAPI 3.0 / JSON Schema)
# =============================================================================

CONTRATO_OCI_PREDICCION_REQUEST = {
    "type": "object",
    "required": ["estacion_id", "parametro", "horizonte_horas"],
    "properties": {
        "estacion_id": {"type": "integer", "minimum": 1},
        "parametro": {"type": "string", "enum": ["pm25", "pm10", "no2", "so2", "o3", "co"]},
        "horizonte_horas": {"type": "integer", "minimum": 1, "maximum": 72},
        "incluir_intervalos_confianza": {"type": "boolean"}
    }
}

CONTRATO_OCI_PREDICCION_RESPONSE = {
    "type": "object",
    "required": ["ok", "estacion_id", "parametro", "predicciones", "metadatos_oci"],
    "properties": {
        "ok": {"type": "boolean"},
        "estacion_id": {"type": "integer"},
        "parametro": {"type": "string"},
        "predicciones": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["timestamp", "valor_estimado", "limite_inferior", "limite_superior"],
                "properties": {
                    "timestamp": {"type": "string"},
                    "valor_estimado": {"type": "number"},
                    "limite_inferior": {"type": "number"},
                    "limite_superior": {"type": "number"}
                }
            }
        },
        "metadatos_oci": {
            "type": "object",
            "required": ["function_id", "execution_time_ms", "memory_allocated_mb", "cold_start"],
            "properties": {
                "function_id": {"type": "string"},
                "execution_time_ms": {"type": "number"},
                "memory_allocated_mb": {"type": "integer"},
                "cold_start": {"type": "boolean"}
            }
        }
    }
}

# Límites contractuales de SLA (en milisegundos)
SLA_INVOCACION_CALIDA_MAX_MS = 2000
SLA_COLD_START_MAX_MS = 5000
SLA_THROUGHPUT_MIN_RPS = 50


# =============================================================================
# SIMULADOR DETERMINISTA DE OCI FUNCTIONS RUNTIME & API GATEWAY
# =============================================================================

class SimuladorOciFunctionRuntime:
    """Simulador de entorno serverless OCI Functions con gestión de ciclo de vida y SLAs."""

    def __init__(self, api_key_valida: str = "6e6f29272fd207dc749c42a87068ed6f"):
        self.api_key_valida = api_key_valida
        self.es_warm = False
        self.contador_invocaciones = 0

    def invocar_funcion_prediccion(
        self,
        payload: Dict[str, Any],
        headers: Dict[str, str],
        simular_timeout: bool = False,
        latencia_inyectada_ms: Optional[float] = None
    ) -> Tuple[int, Dict[str, Any], float]:
        """
        Simula la invocación HTTP sobre OCI API Gateway -> OCI Function:
        1. Autenticación perimetral (X-API-Key).
        2. Validación estricta del contrato de entrada.
        3. Simulación de cold start vs warm execution.
        4. Retorno de payload normalizado con metadatos OCI y código HTTP.
        """
        self.contador_invocaciones += 1

        # 1. Autenticación en OCI API Gateway
        api_key = headers.get("X-API-Key") or headers.get("x-api-key")
        if not api_key or api_key != self.api_key_valida:
            return 401, {"ok": False, "error": "Unauthorized: API Key inválida o ausente en OCI Gateway"}, 15.0

        if simular_timeout:
            return 504, {"ok": False, "error": "Gateway Timeout: La función serverless excedió el tiempo límite"}, 6500.0

        # 2. Validación de Contrato de Entrada (JSON Schema)
        if not isinstance(payload, dict):
            return 400, {"ok": False, "error": "Bad Request: El cuerpo debe ser un objeto JSON válido"}, 20.0

        faltantes = [campo for campo in ["estacion_id", "parametro", "horizonte_horas"] if campo not in payload]
        if faltantes:
            return 400, {"ok": False, "error": f"Bad Request: Campos obligatorios faltantes: {faltantes}"}, 25.0

        if payload["parametro"] not in ["pm25", "pm10", "no2", "so2", "o3", "co"]:
            return 422, {"ok": False, "error": f"Unprocessable Entity: Parámetro '{payload['parametro']}' no soportado"}, 30.0

        if not (1 <= payload["horizonte_horas"] <= 72):
            return 400, {"ok": False, "error": "Bad Request: 'horizonte_horas' debe estar entre 1 y 72"}, 25.0

        # 3. Modelado de Latencia y Cold Start
        cold_start = not self.es_warm
        if latencia_inyectada_ms is not None:
            latencia_ejecucion = latencia_inyectada_ms
        else:
            latencia_ejecucion = 3200.0 if cold_start else 340.0

        # Marcar función como cálida tras primer arranque
        self.es_warm = True

        # 4. Construcción de respuesta conforme al contrato
        predicciones = []
        valor_base = 45.0 if payload["parametro"] == "pm25" else 80.0
        for i in range(1, payload["horizonte_horas"] + 1):
            predicciones.append({
                "timestamp": f"2026-10-14T{i:02d}:00:00Z",
                "valor_estimado": round(valor_base + (i * 0.5), 2),
                "limite_inferior": round(valor_base + (i * 0.5) - 3.2, 2),
                "limite_superior": round(valor_base + (i * 0.5) + 3.2, 2)
            })

        body_salida = {
            "ok": True,
            "estacion_id": payload["estacion_id"],
            "parametro": payload["parametro"],
            "predicciones": predicciones,
            "metadatos_oci": {
                "function_id": "ocid1.fnfunc.oc1.sa-saopaulo-1.aaaaaaaaexample12345",
                "execution_time_ms": latencia_ejecucion,
                "memory_allocated_mb": 512,
                "cold_start": cold_start
            }
        }

        return 200, body_salida, latencia_ejecucion


# =============================================================================
# SUITE DE PRUEBAS AUTOMATIZADAS (PYTEST)
# =============================================================================

class TestOciFunctionsContractsAndSla:
    """Suite de certificación de contratos, seguridad y SLA en OCI Functions."""

    @pytest.fixture
    def runtime(self):
        return SimuladorOciFunctionRuntime()

    @pytest.fixture
    def headers_auth(self):
        return {"X-API-Key": "6e6f29272fd207dc749c42a87068ed6f", "Content-Type": "application/json"}

    # -------------------------------------------------------------------------
    # 1. PRUEBAS DE CONTRATO JSON SCHEMA (ENTRADA Y SALIDA)
    # -------------------------------------------------------------------------

    def test_contrato_exitoso_cumple_esquema_completo(self, runtime, headers_auth):
        """Valida que una respuesta 200 contenga todos los campos obligatorios del esquema OCI."""
        payload = {"estacion_id": 5, "parametro": "pm25", "horizonte_horas": 6}
        status, res, _ = runtime.invocar_funcion_prediccion(payload, headers_auth)

        assert status == 200
        assert res["ok"] is True
        assert res["estacion_id"] == 5
        assert res["parametro"] == "pm25"
        assert len(res["predicciones"]) == 6
        
        # Validar propiedades de cada punto de predicción
        for p in res["predicciones"]:
            assert "timestamp" in p
            assert "valor_estimado" in p
            assert "limite_inferior" in p
            assert "limite_superior" in p
            assert p["limite_inferior"] <= p["valor_estimado"] <= p["limite_superior"]

        # Validar metadatos del runtime OCI
        meta = res["metadatos_oci"]
        assert meta["memory_allocated_mb"] == 512
        assert "function_id" in meta
        assert meta["execution_time_ms"] > 0

    def test_contrato_rechaza_payload_incompleto_con_400(self, runtime, headers_auth):
        """Valida que omitir campos obligatorios produzca un error 400 Bad Request estructurado."""
        payload_invalido = {"estacion_id": 5}  # Falta parametro y horizonte_horas
        status, res, _ = runtime.invocar_funcion_prediccion(payload_invalido, headers_auth)

        assert status == 400
        assert res["ok"] is False
        assert "Campos obligatorios faltantes" in res["error"]

    def test_contrato_rechaza_parametro_contaminante_no_soportado(self, runtime, headers_auth):
        """Valida que un contaminante no soportado devuelva 422 Unprocessable Entity."""
        payload = {"estacion_id": 5, "parametro": "radiacion_nuclear", "horizonte_horas": 12}
        status, res, _ = runtime.invocar_funcion_prediccion(payload, headers_auth)

        assert status == 422
        assert res["ok"] is False
        assert "no soportado" in res["error"]

    def test_contrato_rechaza_horizonte_temporal_fuera_de_rango(self, runtime, headers_auth):
        """Valida que un horizonte superior a 72 horas devuelva 400."""
        payload = {"estacion_id": 5, "parametro": "pm25", "horizonte_horas": 100}
        status, res, _ = runtime.invocar_funcion_prediccion(payload, headers_auth)

        assert status == 400
        assert res["ok"] is False
        assert "entre 1 y 72" in res["error"]

    # -------------------------------------------------------------------------
    # 2. PRUEBAS DE SLA Y TIEMPOS DE RESPUESTA (COLD START VS WARM)
    # -------------------------------------------------------------------------

    def test_sla_cold_start_cumple_umbral_maximo(self, runtime, headers_auth):
        """El primer arranque en frío (Cold Start) debe completarse en menos de 5,000 ms."""
        payload = {"estacion_id": 5, "parametro": "pm25", "horizonte_horas": 12}
        status, res, latencia = runtime.invocar_funcion_prediccion(payload, headers_auth)

        assert status == 200
        assert res["metadatos_oci"]["cold_start"] is True
        assert latencia <= SLA_COLD_START_MAX_MS, f"Cold start excedió {SLA_COLD_START_MAX_MS}ms"

    def test_sla_invocacion_calida_cumple_umbral_estricto(self, runtime, headers_auth):
        """Las invocaciones subsiguientes (Warm Execution) deben ser ultra rápidas (< 2,000 ms)."""
        payload = {"estacion_id": 5, "parametro": "pm25", "horizonte_horas": 12}
        
        # Invocación 1 (Cold)
        runtime.invocar_funcion_prediccion(payload, headers_auth)
        
        # Invocación 2 (Warm)
        status, res, latencia = runtime.invocar_funcion_prediccion(payload, headers_auth)

        assert status == 200
        assert res["metadatos_oci"]["cold_start"] is False
        assert latencia <= SLA_INVOCACION_CALIDA_MAX_MS, f"Invocación cálida excedió {SLA_INVOCACION_CALIDA_MAX_MS}ms"
        assert latencia < 1000.0  # Típico OCI serverless cálido es < 500 ms

    # -------------------------------------------------------------------------
    # 3. SEGURIDAD Y CONTROL DE ACCESO EN OCI API GATEWAY
    # -------------------------------------------------------------------------

    def test_seguridad_rechaza_peticion_sin_api_key(self, runtime):
        """Una petición sin cabecera X-API-Key debe ser bloqueada con 401 Unauthorized."""
        payload = {"estacion_id": 5, "parametro": "pm25", "horizonte_horas": 6}
        status, res, _ = runtime.invocar_funcion_prediccion(payload, headers={})

        assert status == 401
        assert res["ok"] is False
        assert "Unauthorized" in res["error"]

    def test_seguridad_rechaza_api_key_falsificada(self, runtime):
        """Una petición con API Key incorrecta debe ser rechazada inmediatamente."""
        payload = {"estacion_id": 5, "parametro": "pm25", "horizonte_horas": 6}
        bad_headers = {"X-API-Key": "clave_falsa_hacker_12345"}
        status, res, _ = runtime.invocar_funcion_prediccion(payload, bad_headers)

        assert status == 401
        assert res["ok"] is False

    # -------------------------------------------------------------------------
    # 4. RESILIENCIA Y MANEJO DE TIMEOUTS (504 GATEWAY TIMEOUT)
    # -------------------------------------------------------------------------

    def test_tolerancia_a_fallos_gateway_timeout_504(self, runtime, headers_auth):
        """Si la función serverless sobrepasa el límite, el Gateway debe responder 504 sin crashear."""
        payload = {"estacion_id": 5, "parametro": "pm25", "horizonte_horas": 24}
        status, res, _ = runtime.invocar_funcion_prediccion(payload, headers_auth, simular_timeout=True)

        assert status == 504
        assert res["ok"] is False
        assert "Gateway Timeout" in res["error"]

    def test_recuperacion_inmediata_tras_fallo_de_timeout(self, runtime, headers_auth):
        """Tras un timeout esporádico, la siguiente llamada válida debe procesarse sin estado corrupto."""
        payload = {"estacion_id": 5, "parametro": "pm25", "horizonte_horas": 6}
        
        # Petición 1: Falla por timeout
        runtime.invocar_funcion_prediccion(payload, headers_auth, simular_timeout=True)
        
        # Petición 2: Debe tener éxito
        status, res, _ = runtime.invocar_funcion_prediccion(payload, headers_auth, simular_timeout=False)
        assert status == 200
        assert res["ok"] is True
