"""
Suite de Pruebas Unitarias y de Integración para el Mecanismo de Rate Limiting por IP Real (Nginx / n8n / BD).
Valida la extracción de IP, aislamiento de contadores por cliente, ventana móvil de 1 minuto (10 req/min)
y respuesta HTTP 429 estructurada.

Proyecto: EcoPredict-NLQ
Historia de Usuario: HU-16 (#100)
Sub-issue: T16 (#118) - Pruebas de Rate Limiting por IP Real en Nginx
Autor: Johann Romero Contreras (QA / Prompt Engineer)
"""

import time
import pytest
from typing import Dict, Any, Tuple, Optional


class RateLimiterSimulator:
    """
    Simulador determinista de la lógica de Rate Limiting implementada en n8n y PostgreSQL.
    Replica exactamente la consulta SQL de la tabla 'rate_limit':
    - Ventana: 1 minuto (60 segundos).
    - Límite: 10 peticiones por ventana.
    - Manejo de IP Real desde cabeceras Nginx ('x-forwarded-for', 'x-real-ip').
    """

    def __init__(self, limite_maximo: int = 10, duracion_ventana_segundos: float = 60.0):
        self.limite_maximo = limite_maximo
        self.duracion_ventana = duracion_ventana_segundos
        # Almacenamiento en memoria: {ip: {'conteo': int, 'ventana_inicio': float}}
        self.registros: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def extraer_ip_real(headers: Dict[str, str]) -> str:
        """
        Extrae la IP del cliente con la misma precedencia que el nodo 'Extraer IP' de n8n.
        Maneja cabeceras en minúsculas o mayúsculas y cadenas con múltiples proxies (X-Forwarded-For).
        """
        headers_norm = {k.lower(): v for k, v in headers.items()}
        
        # 1. X-Forwarded-For (si contiene varias IPs separadas por coma, la primera es la del cliente real)
        xff = headers_norm.get("x-forwarded-for")
        if xff:
            primer_ip = xff.split(",")[0].strip()
            if primer_ip:
                return primer_ip
                
        # 2. X-Real-IP
        x_real = headers_norm.get("x-real-ip")
        if x_real and x_real.strip():
            return x_real.strip()
            
        # 3. Fallback
        return "desconocida"

    def registrar_peticion(self, ip: str, timestamp_actual: Optional[float] = None) -> Tuple[bool, int, Dict[str, Any]]:
        """
        Simula el INSERT ... ON CONFLICT DO UPDATE de PostgreSQL:
        Retorna: (permitido: bool, conteo_actual: int, payload_respuesta: dict)
        """
        ahora = timestamp_actual if timestamp_actual is not None else time.time()
        
        if ip not in self.registros:
            # Primer registro para esta IP
            self.registros[ip] = {
                "conteo": 1,
                "ventana_inicio": ahora
            }
            conteo = 1
        else:
            registro = self.registros[ip]
            tiempo_transcurrido = ahora - registro["ventana_inicio"]
            
            if tiempo_transcurrido >= self.duracion_ventana:
                # La ventana de 1 minuto expiró: reiniciar contador
                registro["conteo"] = 1
                registro["ventana_inicio"] = ahora
                conteo = 1
            else:
                # Dentro de la ventana: incrementar contador
                registro["conteo"] += 1
                conteo = registro["conteo"]

        # Evaluación de la regla: conteo > 10 genera 429
        if conteo > self.limite_maximo:
            return False, conteo, {
                "ok": False,
                "codigo_http": 429,
                "mensaje": "Demasiadas solicitudes, intenta en un minuto"
            }
        else:
            return True, conteo, {
                "ok": True,
                "codigo_http": 200,
                "conteo_actual": conteo
            }


# ============================================================================
# TESTS DE EXTRACCIÓN DE IP REAL DESDE CABECERAS NGINX
# ============================================================================

class TestExtraccionIPRealNginx:
    """Verifica que el sistema identifique la IP real enviada por Nginx Reverse Proxy."""

    def test_extraccion_desde_x_forwarded_for_simple(self):
        headers = {"X-Forwarded-For": "190.235.10.99"}
        ip = RateLimiterSimulator.extraer_ip_real(headers)
        assert ip == "190.235.10.99"

    def test_extraccion_desde_x_forwarded_for_multiples_proxies(self):
        headers = {"X-Forwarded-For": "200.48.50.14, 172.18.0.1, 10.0.0.5"}
        ip = RateLimiterSimulator.extraer_ip_real(headers)
        assert ip == "200.48.50.14", "Debe seleccionar la primera IP que corresponde al cliente real"

    def test_extraccion_desde_x_real_ip(self):
        headers = {"X-Real-IP": "181.176.40.22"}
        ip = RateLimiterSimulator.extraer_ip_real(headers)
        assert ip == "181.176.40.22"

    def test_precedencia_x_forwarded_for_sobre_x_real_ip(self):
        headers = {
            "X-Forwarded-For": "190.119.80.1",
            "X-Real-IP": "190.119.80.2"
        }
        ip = RateLimiterSimulator.extraer_ip_real(headers)
        assert ip == "190.119.80.1"

    def test_fallback_cuando_no_hay_cabeceras_de_ip(self):
        headers = {"User-Agent": "PostmanRuntime/7.40.0"}
        ip = RateLimiterSimulator.extraer_ip_real(headers)
        assert ip == "desconocida"

    def test_insensibilidad_a_mayusculas_y_espacios(self):
        headers = {"x-forwarded-for": "  181.65.120.30  "}
        ip = RateLimiterSimulator.extraer_ip_real(headers)
        assert ip == "181.65.120.30"


# ============================================================================
# TESTS DE LÍMITES POR VENTANA (10 PETICIONES / MINUTO)
# ============================================================================

class TestVentanaRateLimiting:
    """Verifica el cumplimiento de la regla de 10 peticiones por minuto."""

    def test_diez_primeras_peticiones_son_permitidas_200_ok(self):
        limiter = RateLimiterSimulator(limite_maximo=10, duracion_ventana_segundos=60.0)
        ip = "190.235.10.99"
        t0 = 1000.0

        for i in range(1, 11):
            permitido, conteo, payload = limiter.registrar_peticion(ip, timestamp_actual=t0 + i)
            assert permitido is True, f"La petición {i} debe estar permitida"
            assert conteo == i
            assert payload["ok"] is True
            assert payload["codigo_http"] == 200

    def test_peticion_once_es_bloqueada_con_429(self):
        limiter = RateLimiterSimulator(limite_maximo=10, duracion_ventana_segundos=60.0)
        ip = "190.235.10.99"
        t0 = 1000.0

        # Enviar 10 peticiones válidas
        for i in range(1, 11):
            limiter.registrar_peticion(ip, timestamp_actual=t0 + i)

        # La 11ª petición dentro del mismo minuto
        permitido, conteo, payload = limiter.registrar_peticion(ip, timestamp_actual=t0 + 15.0)
        assert permitido is False, "La petición 11 debe ser rechazada"
        assert conteo == 11
        assert payload["ok"] is False
        assert payload["codigo_http"] == 429
        assert "Demasiadas solicitudes" in payload["mensaje"]

    def test_reinicio_de_contador_tras_cumplirse_un_minuto(self):
        limiter = RateLimiterSimulator(limite_maximo=10, duracion_ventana_segundos=60.0)
        ip = "190.235.10.99"
        t0 = 1000.0

        # Agotar la cuota de 10 peticiones
        for i in range(1, 11):
            limiter.registrar_peticion(ip, timestamp_actual=t0 + i)

        # La petición 11 a los 30s es bloqueada
        bloqueado, _, _ = limiter.registrar_peticion(ip, timestamp_actual=t0 + 30.0)
        assert bloqueado is False

        # Petición a los 61s (nueva ventana de tiempo)
        permitido, conteo, payload = limiter.registrar_peticion(ip, timestamp_actual=t0 + 61.0)
        assert permitido is True, "Tras 60s, la nueva ventana debe permitir la petición"
        assert conteo == 1, "El contador debe haberse reiniciado a 1"
        assert payload["ok"] is True
        assert payload["codigo_http"] == 200


# ============================================================================
# TESTS DE AISLAMIENTO DE CONTADORES POR IP (MULTI-USUARIO)
# ============================================================================

class TestAislamientoContadoresPorIP:
    """Valida que cada IP mantenga un contador independiente y aislado."""

    def test_bloqueo_de_ip_a_no_afecta_a_ip_b(self):
        limiter = RateLimiterSimulator(limite_maximo=10, duracion_ventana_segundos=60.0)
        ip_a = "190.235.10.99"
        ip_b = "200.48.50.88"
        t0 = 1000.0

        # IP A agota sus 10 peticiones y es bloqueada en la 11ª
        for i in range(1, 12):
            limiter.registrar_peticion(ip_a, timestamp_actual=t0 + i)

        # Verificar que IP A está bloqueada
        permitido_a, conteo_a, _ = limiter.registrar_peticion(ip_a, timestamp_actual=t0 + 12.0)
        assert permitido_a is False
        assert conteo_a == 12

        # IP B realiza su primera petición simultáneamente
        permitido_b, conteo_b, payload_b = limiter.registrar_peticion(ip_b, timestamp_actual=t0 + 12.0)
        assert permitido_b is True, "La IP B no debe ser afectada por el bloqueo de la IP A"
        assert conteo_b == 1
        assert payload_b["ok"] is True
        assert payload_b["codigo_http"] == 200

    def test_multiples_ips_concurrentes_mantienen_contadores_exactos(self):
        limiter = RateLimiterSimulator(limite_maximo=10, duracion_ventana_segundos=60.0)
        ips = [f"192.168.1.{i}" for i in range(1, 6)]
        t0 = 2000.0

        # Cada IP envía distinto número de peticiones
        peticiones_por_ip = {
            "192.168.1.1": 3,
            "192.168.1.2": 7,
            "192.168.1.3": 10,
            "192.168.1.4": 12,  # Bloqueada
            "192.168.1.5": 1
        }

        for ip, num_reqs in peticiones_por_ip.items():
            for req_idx in range(1, num_reqs + 1):
                limiter.registrar_peticion(ip, timestamp_actual=t0 + req_idx)

        # Validar estados finales de cada IP
        assert limiter.registros["192.168.1.1"]["conteo"] == 3
        assert limiter.registros["192.168.1.2"]["conteo"] == 7
        assert limiter.registros["192.168.1.3"]["conteo"] == 10
        assert limiter.registros["192.168.1.4"]["conteo"] == 12
        assert limiter.registros["192.168.1.5"]["conteo"] == 1


# ============================================================================
# TESTS DE FORMATO Y CONTRATO DE ERROR HTTP 429
# ============================================================================

class TestContratoRespuesta429:
    """Verifica que el payload de error 429 cumpla estrictamente el contrato del sistema."""

    def test_estructura_json_payload_429(self):
        limiter = RateLimiterSimulator(limite_maximo=10)
        ip = "181.65.120.55"
        
        # Generar bloqueo
        for _ in range(11):
            permitido, conteo, payload = limiter.registrar_peticion(ip)

        assert permitido is False
        assert "ok" in payload and payload["ok"] is False
        assert "codigo_http" in payload and payload["codigo_http"] == 429
        assert "mensaje" in payload and isinstance(payload["mensaje"], str)
        assert len(payload["mensaje"]) > 10
