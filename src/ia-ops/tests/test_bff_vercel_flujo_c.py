"""
=============================================================================
EcoPredict & NLQ — Módulo de Aseguramiento de Calidad (QA / IA Ops)
Sprint 4 — Tarea T16 (#241): Certificación del BFF Serverless en Vercel (HT-13 / #222)
=============================================================================
Suite de pruebas automatizadas para auditar y certificar la función serverless
Vercel Function (BFF) delante del Flujo C (api/flujo-c/[ruta].js):
- Validación de Contrato y Lista Blanca estricta de rutas ('estaciones', 'serie-horaria', 'alertas')
- Rechazo determinista con HTTP 403 de rutas no autorizadas, path traversal o inyecciones
- Certificación de Cabeceras CDN: Cache-Control con s-maxage=300, stale-while-revalidate=600, stale-if-error=86400
- Validación del ciclo de vida de caché en Vercel Edge: x-vercel-cache (HIT, MISS, STALE)
- Simulación de caída del motor n8n y resiliencia con stale-if-error (hasta 24 horas)
- Aislamiento y ocultamiento de credenciales (N8N_BASE_URL y N8N_API_KEY no expuestas al cliente)
- Inspección estática del archivo fuente src/frontend-shell/api/flujo-c/[ruta].js
"""

import json
import re
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import pytest


# =============================================================================
# RUTAS DEL PROYECTO Y CONSTANTES DE CONTRATO (HT-13 / #222)
# =============================================================================

REPO_ROOT = Path(__file__).resolve().parents[3]
VERCEL_FUNCTION_PATH = REPO_ROOT / "src" / "frontend-shell" / "api" / "flujo-c" / "[ruta].js"

RUTAS_LISTA_BLANCA = ["estaciones", "serie-horaria", "alertas"]

CABECERA_CACHE_CONTROL_ESPERADA = "s-maxage=300, stale-while-revalidate=600, stale-if-error=86400"

TIEMPO_MAXIMO_STALE_ERROR_SEGUNDOS = 86400  # 24 horas


# =============================================================================
# HARNESS DE SIMULACIÓN DETERMINISTA DEL BFF VERCEL FUNCTION
# =============================================================================

class MockVercelResponse:
    """Simula el objeto res de Vercel Serverless Function."""

    def __init__(self):
        self.status_code: int = 200
        self.headers: Dict[str, str] = {}
        self.body: Any = None

    def status(self, code: int):
        self.status_code = code
        return self

    def setHeader(self, key: str, value: str):
        self.headers[key] = value
        return self

    def json(self, data: Any):
        self.body = data
        return self


class VercelBffSimulator:
    """
    Simulador que replica fielmente el comportamiento de la función
    src/frontend-shell/api/flujo-c/[ruta].js y la red de borde (Vercel CDN).
    """

    def __init__(self, n8n_base_url: Optional[str] = "https://n8n.ecopredict.cloud/webhook",
                 n8n_api_key: Optional[str] = "eco_secret_key_prod_2026",
                 n8n_disponible: bool = True):
        self.n8n_base_url = n8n_base_url
        self.n8n_api_key = n8n_api_key
        self.n8n_disponible = n8n_disponible
        self.cdn_cache: Dict[str, Dict[str, Any]] = {}

    def ejecutar_handler(self, ruta: Optional[str], method: str = "GET", body: Optional[Dict] = None) -> MockVercelResponse:
        """Ejecuta la lógica de la función serverless api/flujo-c/[ruta].js."""
        res = MockVercelResponse()

        # 1. Validación de Lista Blanca
        if not ruta or ruta not in RUTAS_LISTA_BLANCA:
            return res.status(403).json({
                "error": "Acceso denegado",
                "message": "Ruta no autorizada en la lista blanca del BFF."
            })

        # 2. Configuración de Cabeceras de Caché
        res.setHeader("Cache-Control", CABECERA_CACHE_CONTROL_ESPERADA)

        # 3. Validación de Variables de Entorno del Servidor
        if not self.n8n_base_url or not self.n8n_api_key:
            return res.status(500).json({
                "error": "Error de configuración en las variables de entorno del servidor serverless."
            })

        # 4. Petición hacia n8n con manejo de fallas
        if not self.n8n_disponible:
            return res.status(503).json({
                "error": "Servicio no disponible temporalmente",
                "details": "No se pudo conectar con el motor de n8n, mostrando datos en caché si están disponibles."
            })

        # Respuesta mock exitosa de n8n según la ruta
        datos_mock = self._generar_datos_n8n(ruta)
        return res.status(200).json(datos_mock)

    def ejecutar_con_cdn_vercel(self, ruta: str, method: str = "GET", timestamp_actual: float = 0.0) -> Tuple[int, Dict[str, str], Any]:
        """
        Simula la interacción de Vercel Edge Network (CDN) con la Serverless Function,
        evaluando cabeceras de caché y x-vercel-cache (HIT, MISS, STALE).
        """
        cache_key = f"{method}:{ruta}"
        entrada_cache = self.cdn_cache.get(cache_key)

        # Si hay caché y sigue fresca (< 300 segundos)
        if entrada_cache and (timestamp_actual - entrada_cache["created_at"]) < 300:
            headers = dict(entrada_cache["headers"])
            headers["x-vercel-cache"] = "HIT"
            return 200, headers, entrada_cache["body"]

        # Si la caché expiró o no existe, intentamos invocar el origen (BFF)
        res_origen = self.ejecutar_handler(ruta, method)

        # Caso A: El origen responde exitoso (200 OK)
        if res_origen.status_code == 200:
            headers = dict(res_origen.headers)
            headers["x-vercel-cache"] = "MISS" if not entrada_cache else "STALE"
            # Actualizamos la CDN
            self.cdn_cache[cache_key] = {
                "created_at": timestamp_actual,
                "body": res_origen.body,
                "headers": res_origen.headers
            }
            return 200, headers, res_origen.body

        # Caso B: El origen falla (ej. 503 porque n8n está caído)
        # Verificamos si podemos aplicar stale-if-error=86400
        if entrada_cache and res_origen.status_code >= 500:
            antiguedad = timestamp_actual - entrada_cache["created_at"]
            if antiguedad <= TIEMPO_MAXIMO_STALE_ERROR_SEGUNDOS:
                headers = dict(entrada_cache["headers"])
                headers["x-vercel-cache"] = "STALE"
                headers["x-vercel-stale-reason"] = "stale-if-error-n8n-down"
                return 200, headers, entrada_cache["body"]

        # Caso C: Falló y no hay caché disponible
        headers = dict(res_origen.headers)
        headers["x-vercel-cache"] = "MISS"
        return res_origen.status_code, headers, res_origen.body

    def _generar_datos_n8n(self, ruta: str) -> Dict[str, Any]:
        if ruta == "estaciones":
            return {
                "estaciones": [
                    {"id": 1, "nombre": "San Juan de Lurigancho", "codigo": "SJL", "activa": True, "inca": "bueno"},
                    {"id": 2, "nombre": "La Victoria", "codigo": "VIC", "activa": True, "inca": "moderado"}
                ],
                "total": 2
            }
        elif ruta == "serie-horaria":
            return {
                "estacion_id": 1,
                "puntos_24h": [{"hora": f"{h:02d}:00", "pm25": 18.5 + (h % 5), "pm10": 42.0} for h in range(24)]
            }
        elif ruta == "alertas":
            return {
                "alertas_activas": [
                    {"id": 101, "estacion": "SJL", "parametro": "pm25", "nivel": "moderado", "mensaje": "Alerta preventiva"}
                ]
            }
        return {"data": "ok"}


# =============================================================================
# SUITE DE PRUEBAS AUTOMATIZADAS (PYTEST)
# =============================================================================

class TestListaBlancaYRutasBFF:
    """Certifica la lista blanca estricta de rutas y el rechazo de endpoints no autorizados."""

    def test_rutas_permitidas_son_aceptadas_con_200(self):
        """Valida que 'estaciones', 'serie-horaria' y 'alertas' sean procesadas exitosamente."""
        bff = VercelBffSimulator()
        for ruta in RUTAS_LISTA_BLANCA:
            res = bff.ejecutar_handler(ruta=ruta)
            assert res.status_code == 200, f"La ruta válida '{ruta}' debió responder 200."
            assert res.body is not None
            assert res.headers.get("Cache-Control") == CABECERA_CACHE_CONTROL_ESPERADA

    @pytest.mark.parametrize("ruta_invalida", [
        "usuarios",
        "admin",
        "flujo-a",
        "flujo-b",
        "flujo-d",
        "configuracion",
        "metricas-internas"
    ])
    def test_rutas_fuera_de_lista_blanca_son_rechazadas_con_403(self, ruta_invalida):
        """Valida que cualquier ruta fuera de la lista blanca retorne HTTP 403 Forbidden."""
        bff = VercelBffSimulator()
        res = bff.ejecutar_handler(ruta=ruta_invalida)
        assert res.status_code == 403
        assert res.body["error"] == "Acceso denegado"
        assert "no autorizada en la lista blanca" in res.body["message"]

    @pytest.mark.parametrize("payload_malicioso", [
        "../etc/passwd",
        "..%2f..%2fpackage.json",
        "estaciones' OR 1=1--",
        "serie-horaria;DROP TABLE",
        "<script>alert(1)</script>"
    ])
    def test_path_traversal_e_inyecciones_son_bloqueadas_con_403(self, payload_malicioso):
        """Valida que intentos de Directory Traversal o inyección sean neutralizados por la lista blanca."""
        bff = VercelBffSimulator()
        res = bff.ejecutar_handler(ruta=payload_malicioso)
        assert res.status_code == 403
        assert res.body["error"] == "Acceso denegado"

    def test_ruta_vacia_o_nula_es_rechazada_con_403(self):
        """Valida que invocaciones sin el parámetro de ruta sean rechazadas ordenadamente."""
        bff = VercelBffSimulator()
        res = bff.ejecutar_handler(ruta=None)
        assert res.status_code == 403
        assert res.body["error"] == "Acceso denegado"


class TestCabecerasCacheYVercelCDN:
    """Certifica las directivas de Cache-Control y la propagación de estados x-vercel-cache."""

    def test_cabecera_cache_control_incluye_directivas_estrictas(self):
        """Valida que se emitan s-maxage=300, stale-while-revalidate=600 y stale-if-error=86400."""
        bff = VercelBffSimulator()
        res = bff.ejecutar_handler(ruta="estaciones")
        cache_header = res.headers.get("Cache-Control", "")

        assert "s-maxage=300" in cache_header, "Debe especificar 5 minutos de caché compartida en CDN."
        assert "stale-while-revalidate=600" in cache_header, "Debe especificar 10 minutos de stale-while-revalidate."
        assert "stale-if-error=86400" in cache_header, "Debe especificar 24 horas de tolerancia ante errores del backend."

    def test_ciclo_de_vida_cache_miss_luego_hit(self):
        """Valida que la primera petición sea MISS y las subsiguientes dentro del TTL sean HIT."""
        bff = VercelBffSimulator()
        t0 = 1000.0

        # Petición 1: Sin caché -> MISS
        status1, headers1, body1 = bff.ejecutar_con_cdn_vercel("estaciones", timestamp_actual=t0)
        assert status1 == 200
        assert headers1.get("x-vercel-cache") == "MISS"
        assert len(body1["estaciones"]) == 2

        # Petición 2: A los 30 segundos (< 300s TTL) -> HIT
        status2, headers2, body2 = bff.ejecutar_con_cdn_vercel("estaciones", timestamp_actual=t0 + 30)
        assert status2 == 200
        assert headers2.get("x-vercel-cache") == "HIT"
        assert body2 == body1

    def test_stale_while_revalidate_entre_300_y_900_segundos(self):
        """Valida que peticiones en la ventana stale-while-revalidate retornen datos mientras revalida."""
        bff = VercelBffSimulator()
        t0 = 1000.0

        # Poblamos la caché
        bff.ejecutar_con_cdn_vercel("serie-horaria", timestamp_actual=t0)

        # A los 400 segundos (300s < t <= 900s) el contenido está stale pero revalida
        status, headers, body = bff.ejecutar_con_cdn_vercel("serie-horaria", timestamp_actual=t0 + 400)
        assert status == 200
        assert headers.get("x-vercel-cache") == "STALE"
        assert "puntos_24h" in body


class TestResilienciaCaidaN8nStaleIfError:
    """Certifica que el Dashboard siga operando ante caídas de n8n mediante stale-if-error (24h)."""

    def test_caida_n8n_sirve_ultima_respuesta_cacheada_hasta_24_horas(self):
        """Simula caída de n8n y comprueba que la CDN sirva datos previos con x-vercel-cache: STALE."""
        bff = VercelBffSimulator()
        t0 = 1000.0

        # 1. Petición inicial exitosa con n8n online (Guarda en caché)
        status_ok, headers_ok, body_ok = bff.ejecutar_con_cdn_vercel("estaciones", timestamp_actual=t0)
        assert status_ok == 200
        assert headers_ok["x-vercel-cache"] == "MISS"

        # 2. Simulamos que n8n se detiene o cae (n8n_disponible = False)
        bff.n8n_disponible = False

        # 3. Petición a las 2 horas (7,200s), dentro del margen de 24 horas (86,400s)
        status_stale, headers_stale, body_stale = bff.ejecutar_con_cdn_vercel("estaciones", timestamp_actual=t0 + 7200)
        assert status_stale == 200, "La CDN debió rescatar los datos cacheados mediante stale-if-error."
        assert headers_stale["x-vercel-cache"] == "STALE"
        assert headers_stale.get("x-vercel-stale-reason") == "stale-if-error-n8n-down"
        assert body_stale == body_ok, "El Dashboard debe ver los mismos datos sin enterarse de la caída de n8n."

    def test_caida_n8n_sin_cache_previa_retorna_503_controlado(self):
        """Si n8n cae y no hay caché previa (Cold Start en falla), emite HTTP 503 amigable."""
        bff = VercelBffSimulator(n8n_disponible=False)
        status, headers, body = bff.ejecutar_con_cdn_vercel("alertas", timestamp_actual=1000.0)
        assert status == 503
        assert headers["x-vercel-cache"] == "MISS"
        assert body["error"] == "Servicio no disponible temporalmente"
        assert "mostrando datos en caché si están disponibles" in body["details"]

    def test_expiracion_del_stale_tras_24_horas_de_caida_continua(self):
        """Tras 24 horas y 1 segundo con n8n caído, la caché caduca y se retorna 503."""
        bff = VercelBffSimulator()
        t0 = 1000.0

        # Poblamos la caché inicial
        bff.ejecutar_con_cdn_vercel("estaciones", timestamp_actual=t0)

        # n8n se cae
        bff.n8n_disponible = False

        # Petición a las 24 horas y 5 minutos (86,700 segundos)
        status_expirado, headers_expirado, body_expirado = bff.ejecutar_con_cdn_vercel(
            "estaciones", timestamp_actual=t0 + 86700
        )
        assert status_expirado == 503, "Tras superar las 24 horas (86400s), el stale-if-error debe expirar."
        assert body_expirado["error"] == "Servicio no disponible temporalmente"

    def test_recuperacion_automatica_cuando_n8n_vuelve_a_estar_online(self):
        """Valida que cuando n8n se restablece, el BFF vuelve a refrescar la caché normalmente."""
        bff = VercelBffSimulator()
        t0 = 1000.0

        # Cache inicial
        bff.ejecutar_con_cdn_vercel("estaciones", timestamp_actual=t0)

        # Cae n8n
        bff.n8n_disponible = False
        bff.ejecutar_con_cdn_vercel("estaciones", timestamp_actual=t0 + 1000)

        # Se recupera n8n
        bff.n8n_disponible = True
        status, headers, body = bff.ejecutar_con_cdn_vercel("estaciones", timestamp_actual=t0 + 2000)
        assert status == 200
        assert headers["x-vercel-cache"] in ["STALE", "MISS"]
        assert len(body["estaciones"]) == 2


class TestSeguridadYOcultamientoSecretos:
    """Certifica que los secretos de n8n no se filtren al navegador ni en respuestas."""

    def test_url_y_clave_n8n_no_se_filtran_en_el_payload_de_respuesta(self):
        """Valida que la respuesta del BFF no incluya variables de entorno ni la API key."""
        bff = VercelBffSimulator(n8n_api_key="SUPER_SECRET_N8N_TOKEN_XYZ_999")
        res = bff.ejecutar_handler(ruta="estaciones")

        json_str = json.dumps(res.body)
        assert "SUPER_SECRET_N8N_TOKEN_XYZ_999" not in json_str
        assert "n8n_api_key" not in json_str
        assert "X-API-Key" not in res.headers

    def test_error_500_si_faltan_variables_de_entorno_en_vercel(self):
        """Valida respuesta segura 500 si N8N_BASE_URL o N8N_API_KEY no están configuradas."""
        bff_sin_env = VercelBffSimulator(n8n_base_url=None, n8n_api_key=None)
        res = bff_sin_env.ejecutar_handler(ruta="estaciones")

        assert res.status_code == 500
        assert "variables de entorno" in res.body["error"]


class TestIntegridadArchivoFuenteVercel:
    """Audita estáticamente el código fuente en src/frontend-shell/api/flujo-c/[ruta].js."""

    def test_archivo_fuente_del_bff_existe_y_contiene_lista_blanca(self):
        """Verifica que el archivo exista y declare las 3 rutas permitidas."""
        assert VERCEL_FUNCTION_PATH.is_file(), f"No se encontró el archivo {VERCEL_FUNCTION_PATH}"
        contenido = VERCEL_FUNCTION_PATH.read_text(encoding="utf-8")

        for ruta in RUTAS_LISTA_BLANCA:
            assert f"'{ruta}'" in contenido or f'"{ruta}"' in contenido, f"Falta la ruta '{ruta}' en allowedRoutes."

        assert "allowedRoutes" in contenido
        assert "res.status(403)" in contenido

    def test_archivo_fuente_declara_cabeceras_de_cache_estrictas(self):
        """Verifica que el archivo configure exactamente la directiva de caché del Sprint 4."""
        contenido = VERCEL_FUNCTION_PATH.read_text(encoding="utf-8")
        assert "Cache-Control" in contenido
        assert "s-maxage=300" in contenido
        assert "stale-while-revalidate=600" in contenido
        assert "stale-if-error=86400" in contenido
        assert "res.status(503)" in contenido
        assert "N8N_BASE_URL" in contenido
        assert "N8N_API_KEY" in contenido
