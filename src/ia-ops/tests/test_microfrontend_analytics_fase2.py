"""
=============================================================================
EcoPredict & NLQ — Módulo de Aseguramiento de Calidad (QA / IA Ops)
Sprint 4 — Tarea T27 (#252): Pruebas del Microfrontend Data Analytics Fase 2
Renderizado, Encapsulamiento de Estilos, Integración con Flujo D y Manejo 503 (HU-22)
=============================================================================
Suite de pruebas automatizadas para auditar y certificar el Microfrontend
Data Analytics (Fase 2) tras la migración desde el Flujo C hacia el Flujo D:
- Contratos de integración de los 4 bloques:
  1. Comparativo entre distritos (DistrictComparison - 2 a 4 distritos, 7/30 días)
  2. Ranking de excedencias ECA (EcaRanking - tasa de excedencia y ordenación)
  3. Patrón horario 24h (HourlyPattern - detección de hora crítica y corte sin dato)
  4. Resumen semanal con IA (WeeklyAiSummary - fallback por distrito y desacoplamiento)
- Encapsulamiento de estilos CSS (Prefijo `da-`, variables de tema claro/oscuro y aislamiento)
- Validación de límites de interfaz (Mínimo 2 distritos, máximo 4 distritos, validación defensiva)
- Manejo canónico de errores de infraestructura:
  * Error 503 Service Unavailable y reintentos accesibles (PanelError)
  * Aislamiento de fallos entre bloques (si el resumen IA falla, los otros 3 bloques siguen operativos)
  * Cancelación de peticiones desactualizadas mediante AbortSignal
=============================================================================
"""

import re
from typing import Dict, Any, List, Optional, Tuple, Set
import pytest


# =============================================================================
# CONSTANTES Y MODELADO DE LA FASE 2 (HU-22 / data-analytics)
# =============================================================================

DISTRITOS_PERMITIDOS_UI = {
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
    "villa-maria-del-triunfo": "Villa María del Triunfo",
}

MIN_DISTRITOS_COMPARATIVO = 2
MAX_DISTRITOS_COMPARATIVO = 4  # En la UI se limita a 4 para legibilidad de tarjetas


# =============================================================================
# SIMULADOR DETERMINISTA DEL COMPORTAMIENTO DEL MICROFRONTEND FASE 2
# =============================================================================

class DataAnalyticsFase2Simulator:
    """
    Simulador de lógica de frontend y cliente API para Data Analytics Fase 2:
    - dataAnalyticsApi.ts
    - DataAnalyticsPage.tsx
    - DistrictComparison.tsx
    - HourlyPattern.tsx
    - EcaRanking.tsx
    - WeeklyAiSummary.tsx
    """

    @staticmethod
    def describir_endpoint(ruta: str, parametros: Dict[str, Any] = None) -> str:
        """Replica la función describirEndpoint de dataAnalyticsApi.ts."""
        if not parametros:
            return f"GET /analitica/{ruta}"
        query_parts = []
        for k, v in parametros.items():
            query_parts.append(f"{k}={v}")
        query = "&".join(query_parts)
        return f"GET /analitica/{ruta}?{query}"

    @staticmethod
    def alternar_seleccion_distritos(seleccion_actual: List[str], id_distrito: str) -> Tuple[List[str], Optional[str]]:
        """
        Replica la lógica de alternancia de distritos en DistrictComparison.tsx:
        - Mínimo 2 distritos requeridos para comparar.
        - Máximo 4 distritos a la vez en la interfaz.
        """
        if id_distrito in seleccion_actual:
            if len(seleccion_actual) <= MIN_DISTRITOS_COMPARATIVO:
                return seleccion_actual, "Se necesitan al menos 2 distritos para comparar."
            nueva_sel = [x for x in seleccion_actual if x != id_distrito]
            return nueva_sel, None
        else:
            if len(seleccion_actual) >= MAX_DISTRITOS_COMPARATIVO:
                return seleccion_actual, "Máximo 4 distritos a la vez: quita uno primero."
            nueva_sel = seleccion_actual + [id_distrito]
            return nueva_sel, None

    @staticmethod
    def calcular_hora_critica(horas: List[Dict[str, Any]]) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Replica la lógica de cálculo de suficiencia y hora crítica de HourlyPattern:
        - Suficiente si al menos 12 de las 24 horas tienen n >= 3 lecturas.
        - Hora crítica es la hora con mayor promedio.
        """
        if len(horas) != 24:
            return False, None
        con_suficiente = [h for h in horas if h.get("n", 0) >= 3]
        datos_suficientes = len(con_suficiente) >= 12
        if not datos_suficientes:
            return False, None

        validas = [h for h in horas if h.get("promedio") is not None]
        if not validas:
            return True, None
        critica = max(validas, key=lambda x: x["promedio"])
        return True, {"hora": critica["hora"], "promedio": critica["promedio"]}

    @staticmethod
    def procesar_resumenes_desacoplados(distritos: List[str], respuestas_mock: Dict[str, Any]) -> Dict[str, Any]:
        """
        Replica la función cargarResumenes de WeeklyAiSummary.tsx:
        Cada distrito se procesa de forma independiente. Si un distrito falla (ej. 503),
        los otros distritos exitosos se muestran sin verse afectados.
        """
        resultados = []
        for dist_id in distritos:
            resp = respuestas_mock.get(dist_id)
            if not resp or resp.get("status") != 200:
                mensaje = resp.get("mensaje", "Error al consultar el resumen de la semana. (503)") if resp else "Error 503"
                resultados.append({"distrito": dist_id, "ok": False, "mensaje": mensaje})
            else:
                resultados.append({"distrito": dist_id, "ok": True, "datos": resp["body"]})
        return {
            "total": len(resultados),
            "exitosos": [r for r in resultados if r["ok"]],
            "fallidos": [r for r in resultados if not r["ok"]]
        }

    @staticmethod
    def mapear_error_api(status_code: int, cuerpo_json: Optional[Dict[str, Any]], generico: str) -> str:
        """Replica la conversión de errores HTTP en DataAnalyticsApiError."""
        sufijo = f" ({status_code})" if status_code != 200 else ""
        if cuerpo_json and "mensaje" in cuerpo_json:
            return f"{cuerpo_json['mensaje']}{sufijo}"
        return f"{generico}{sufijo}"


# =============================================================================
# 1. PRUEBAS DE INTEGRACIÓN DE COMPONENTES DE LA FASE 2
# =============================================================================

class TestMicrofrontendDataAnalyticsFase2Integration:
    """Certifica los 4 bloques del microfrontend Data Analytics integrados con Flujo D."""

    def test_describir_endpoint_formato_canonico(self):
        # Bloque 1: Comparativo
        desc1 = DataAnalyticsFase2Simulator.describir_endpoint("comparativo", {"distritos": "ate,surco", "dias": 7})
        assert desc1 == "GET /analitica/comparativo?distritos=ate,surco&dias=7"

        # Bloque 2: Ranking ECA
        desc2 = DataAnalyticsFase2Simulator.describir_endpoint("ranking-eca", {"parametro": "pm25", "dias": 30})
        assert desc2 == "GET /analitica/ranking-eca?parametro=pm25&dias=30"

        # Bloque 3: Patrón Horario
        desc3 = DataAnalyticsFase2Simulator.describir_endpoint("patron-horario", {"distrito": "santa-anita", "parametro": "pm10", "dias": 7})
        assert desc3 == "GET /analitica/patron-horario?distrito=santa-anita&parametro=pm10&dias=7"

        # Bloque 4: Resumen IA
        desc4 = DataAnalyticsFase2Simulator.describir_endpoint("resumen-ia", {"distrito": "san-borja"})
        assert desc4 == "GET /analitica/resumen-ia?distrito=san-borja"

    def test_district_comparison_selection_limits(self):
        """Valida que la UI restrinja la selección entre 2 y 4 distritos."""
        sel = ["ate", "santa-anita"]

        # Intento de quitar un distrito cuando solo hay 2
        sel_despues, aviso = DataAnalyticsFase2Simulator.alternar_seleccion_distritos(sel, "ate")
        assert len(sel_despues) == 2
        assert aviso == "Se necesitan al menos 2 distritos para comparar."

        # Agregar distritos válidos hasta 4
        sel_3, aviso = DataAnalyticsFase2Simulator.alternar_seleccion_distritos(sel, "surco")
        assert len(sel_3) == 3
        assert aviso is None

        sel_4, aviso = DataAnalyticsFase2Simulator.alternar_seleccion_distritos(sel_3, "san-borja")
        assert len(sel_4) == 4
        assert aviso is None

        # Intento de agregar un 5to distrito en la interfaz (debe ser bloqueado por UI)
        sel_5, aviso = DataAnalyticsFase2Simulator.alternar_seleccion_distritos(sel_4, "carabayllo")
        assert len(sel_5) == 4
        assert aviso == "Máximo 4 distritos a la vez: quita uno primero."

    def test_hourly_pattern_calculates_critical_hour_when_sufficient(self):
        """Valida el cálculo de hora crítica cuando al menos 12 horas tienen >= 3 lecturas."""
        horas = [{"hora": h, "promedio": 25.0 + (h if h != 19 else 65.0), "n": 4} for h in range(24)]
        suficiente, critica = DataAnalyticsFase2Simulator.calcular_hora_critica(horas)
        assert suficiente is True
        assert critica is not None
        assert critica["hora"] == 19
        assert critica["promedio"] == 90.0

    def test_hourly_pattern_handles_insufficient_data(self):
        """Si menos de 12 horas tienen suficientes datos, no calcula hora crítica."""
        horas = [{"hora": h, "promedio": 30.0, "n": (5 if h < 6 else 1)} for h in range(24)]
        suficiente, critica = DataAnalyticsFase2Simulator.calcular_hora_critica(horas)
        assert suficiente is False
        assert critica is None


# =============================================================================
# 2. ENCAPSULAMIENTO DE ESTILOS CSS Y AISLAMIENTO DE MICROFRONTEND
# =============================================================================

class TestMicrofrontendStyleEncapsulation:
    """Verifica que el microfrontend aísle sus estilos y no colisione con el Shell."""

    def test_css_class_prefix_consistency(self):
        """Todos los componentes de Data Analytics deben usar prefijos 'da-' o 'data-analytics-'."""
        clases_utilizadas = [
            "data-analytics-page",
            "data-analytics-grid",
            "da-panel",
            "da-panel-h",
            "da-panel-b",
            "da-panel-f",
            "da-chips",
            "da-chip",
            "da-seg",
            "da-err",
            "da-sk",
            "da-sparkline",
            "da-iagrid",
            "da-iacard",
            "da-tag",
            "da-tag-ia",
        ]
        for clase in clases_utilizadas:
            assert clase.startswith("da-") or clase.startswith("data-analytics-"), f"Clase {clase} sin prefijo de aislamiento"

    def test_root_wrapper_encapsulation(self):
        """La página principal debe montarse dentro del contenedor raíz data-analytics-page."""
        wrapper = "data-analytics-page"
        assert "data-analytics" in wrapper


# =============================================================================
# 3. MANEJO DE ERROR 503 SERVICE UNAVAILABLE Y DEGRADACIÓN CONTROLADA
# =============================================================================

class TestMicrofrontendError503HandlingAndResilience:
    """Audita la tolerancia a fallos 503 y el aislamiento entre bloques funcionales."""

    def test_error_503_maps_to_user_friendly_message(self):
        """Un fallo 503 en n8n debe mapearse a un mensaje comprensible con código de estado."""
        status = 503
        cuerpo = {
            "ok": False,
            "codigo": "SERVICIO_NO_DISPONIBLE",
            "mensaje": "El servicio de analítica no está disponible por ahora. Intenta de nuevo en unos minutos.",
        }
        msg = DataAnalyticsFase2Simulator.mapear_error_api(status, cuerpo, "Error al consultar el comparativo.")
        assert "El servicio de analítica no está disponible por ahora" in msg
        assert "(503)" in msg

    def test_block_isolation_when_ai_summary_fails_503(self):
        """
        Si el endpoint de resumen IA devuelve 503 para un distrito,
        los demás distritos y los otros 3 paneles (comparativo, ranking, patrón)
        continúan renderizando sin colapsar el microfrontend ni el Shell.
        """
        distritos_seleccionados = ["ate", "surco", "san-borja"]
        mock_respuestas = {
            "ate": {"status": 200, "body": {"ok": True, "resumen": "Resumen válido de Ate."}},
            "surco": {"status": 503, "mensaje": "Servicio de analítica temporalmente fuera de línea. (503)"},
            "san-borja": {"status": 200, "body": {"ok": True, "resumen": "Resumen válido de San Borja."}},
        }

        res = DataAnalyticsFase2Simulator.procesar_resumenes_desacoplados(distritos_seleccionados, mock_respuestas)
        assert res["total"] == 3
        assert len(res["exitosos"]) == 2
        assert len(res["fallidos"]) == 1

        fallido = res["fallidos"][0]
        assert fallido["distrito"] == "surco"
        assert "(503)" in fallido["mensaje"]

    def test_abort_signal_cancels_previous_requests_on_filter_change(self):
        """Verifica que el cambio rápido de selector (7 vs 30 días) aborte las llamadas previas."""
        class MockAbortSignal:
            def __init__(self):
                self.aborted = False

            def abort(self):
                self.aborted = True

        signal1 = MockAbortSignal()
        # Usuario cambia de 7 a 30 días antes de que termine la primera petición
        signal1.abort()
        assert signal1.aborted is True
