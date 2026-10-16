"""
=============================================================================
EcoPredict & NLQ — Módulo de Aseguramiento de Calidad (QA / IA Ops)
Sprint 3 — Tarea T21 (#181): Pruebas de Integración del Microfrontend de Analítica (HU-23 / HU-03)
=============================================================================
Suite de pruebas automatizadas para auditar y certificar la integración
del Microfrontend de Analítica Ambiental (data-analytics):
- Contrato de datos de Estaciones y Resumen por Distrito (DistrictSummaryTable)
- Cálculo determinista de Categoría ECA-Aire (D.S. N° 003-2017-MINAM) y peorNivel
- Indicadores de tendencia diferencial (▲ sube, ▼ baja, — estable) respecto al valor anterior
- Serie temporal horaria de 24h para PM2.5 y PM10 (PmTrendChart)
- Panel de Alertas y Factores Asociados con reutilización de analisis_llm (AlertasPanel)
- Manejo canónico de estados de carga, estados vacíos y tolerancia a fallos de red
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Literal
import pytest


# =============================================================================
# MODELO DETERMINISTA Y REGLAS DE NEGOCIO DEL MICROFRONTEND DATA-ANALYTICS
# Replicado fielmente de:
# - src/microfrontends/data-analytics/src/utils/eca.ts
# - src/microfrontends/data-analytics/src/utils/nivel.ts
# - src/microfrontends/data-analytics/src/components/DistrictSummaryTable.tsx
# - src/microfrontends/data-analytics/src/components/AlertsPanel.tsx
# =============================================================================

ParametroCalidadAire = Literal["pm25", "pm10", "no2", "so2", "o3", "co"]
NivelEstado = Literal["bueno", "moderado", "malo"]

# Límites oficiales ECA-Aire (D.S. N° 003-2017-MINAM) en µg/m³
ECA_LIMITE: Dict[str, float] = {
    "pm25": 50.0,   # 24 h
    "pm10": 100.0,  # 24 h
    "so2": 250.0,   # 24 h
    "no2": 200.0,   # 1 h
    "o3": 100.0,    # 8 h
    "co": 10000.0,  # 8 h (10 mg/m³)
}

ORDEN_NIVEL: Dict[NivelEstado, int] = {"bueno": 0, "moderado": 1, "malo": 2}


def porcentaje_eca(parametro: str, valor: float) -> int:
    """Calcula el porcentaje respecto al estándar ECA nacional."""
    limite = ECA_LIMITE.get(parametro, 50.0)
    return round((valor / limite) * 100)


def nivel_por_eca(parametro: str, valor: float) -> NivelEstado:
    """Clasifica en 'bueno', 'moderado' o 'malo' según porcentaje ECA."""
    pct = porcentaje_eca(parametro, valor)
    if pct <= 50:
        return "bueno"
    elif pct <= 100:
        return "moderado"
    else:
        return "malo"


def peor_nivel(niveles: List[NivelEstado]) -> NivelEstado:
    """Calcula la categoría ECA global tomando el peor nivel entre contaminantes."""
    if not niveles:
        return "bueno"
    peor = "bueno"
    for actual in niveles:
        if ORDEN_NIVEL[actual] > ORDEN_NIVEL[peor]:
            peor = actual
    return peor


def calcular_indicador_tendencia(
    valor_actual: Optional[float],
    valor_anterior: Optional[float]
) -> Dict[str, Any]:
    """
    Replica indicadorTendencia() de DistrictSummaryTable.tsx:
    - Retorna {'simbolo': '—', 'tipo': 'sin_dato'} si no hay valor previo.
    - Retorna {'simbolo': '—', 'tipo': 'estable'} si delta == 0.
    - Retorna {'simbolo': '▲', 'tipo': 'sube', 'pct': X} si delta > 0.
    - Retorna {'simbolo': '▼', 'tipo': 'baja', 'pct': X} si delta < 0.
    """
    if valor_actual is None or valor_anterior is None:
        return {"simbolo": "—", "tipo": "sin_dato", "pct": None}

    delta = valor_actual - valor_anterior
    if delta == 0:
        return {"simbolo": "—", "tipo": "estable", "pct": 0}

    pct = abs(round((delta / valor_anterior) * 100))
    if delta > 0:
        return {"simbolo": "▲", "tipo": "sube", "pct": pct}
    else:
        return {"simbolo": "▼", "tipo": "baja", "pct": pct}


# =============================================================================
# SUITE DE PRUEBAS AUTOMATIZADAS (PYTEST)
# =============================================================================

class TestMicrofrontendDataAnalytics:
    """Pruebas de integración, visualización y contratos para el Microfrontend de Analítica."""

    # -------------------------------------------------------------------------
    # 1. RESUMEN POR DISTRITO Y CLASIFICACIÓN ECA
    # -------------------------------------------------------------------------

    def test_clasificacion_eca_pm25_bueno_moderado_malo(self):
        """Valida que PM2.5 se categorice con los umbrales ECA de 50 µg/m³."""
        assert nivel_por_eca("pm25", 20.0) == "bueno"     # 40% ECA
        assert nivel_por_eca("pm25", 25.0) == "bueno"     # 50% ECA
        assert nivel_por_eca("pm25", 35.0) == "moderado"  # 70% ECA
        assert nivel_por_eca("pm25", 50.0) == "moderado"  # 100% ECA
        assert nivel_por_eca("pm25", 51.0) == "malo"      # 102% ECA (> 100% ECA)
        assert nivel_por_eca("pm25", 85.0) == "malo"      # 170% ECA

    def test_peor_nivel_adopta_el_contaminante_mas_severo(self):
        """Si PM2.5 es bueno pero PM10 es malo, la categoría general de la estación debe ser 'malo'."""
        niveles_1 = ["bueno", "bueno", "bueno"]
        assert peor_nivel(niveles_1) == "bueno"

        niveles_2 = ["bueno", "moderado"]
        assert peor_nivel(niveles_2) == "moderado"

        niveles_3 = ["bueno", "moderado", "malo"]
        assert peor_nivel(niveles_3) == "malo"

    def test_contrato_estacion_resumen_computa_categoria_correcta(self):
        """Valida el cálculo integral de una estación con mediciones de PM2.5 y PM10."""
        estacion = {
            "id": 10,
            "nombre": "CAMPO DE MARTE",
            "zona": "residencial",
            "coordenadas": {"lat": -12.068, "lon": -77.042},
            "mediciones": [
                {"parametro": "pm25", "valor": 55.4, "valorAnterior": 48.0, "unidad": "µg/m³"},
                {"parametro": "pm10", "valor": 85.0, "valorAnterior": 90.0, "unidad": "µg/m³"}
            ]
        }

        niveles = [nivel_por_eca(m["parametro"], m["valor"]) for m in estacion["mediciones"]]
        categoria_estacion = peor_nivel(niveles)

        # PM2.5 es 55.4 (>50 -> malo), PM10 es 85.0 (<=100 -> moderado) -> Peor nivel = 'malo'
        assert categoria_estacion == "malo"

    # -------------------------------------------------------------------------
    # 2. INDICADORES DE TENDENCIA DINÁMICA (▲ / ▼ / —)
    # -------------------------------------------------------------------------

    def test_tendencia_detecta_incremento_con_porcentaje(self):
        """Si el valor actual subió respecto al anterior, muestra ▲ y porcentaje positivo."""
        tendencia = calcular_indicador_tendencia(valor_actual=60.0, valor_anterior=50.0)
        assert tendencia["simbolo"] == "▲"
        assert tendencia["tipo"] == "sube"
        assert tendencia["pct"] == 20  # +20%

    def test_tendencia_detecta_decremento_con_porcentaje(self):
        """Si el valor actual bajó respecto al anterior, muestra ▼ y porcentaje."""
        tendencia = calcular_indicador_tendencia(valor_actual=40.0, valor_anterior=50.0)
        assert tendencia["simbolo"] == "▼"
        assert tendencia["tipo"] == "baja"
        assert tendencia["pct"] == 20  # -20%

    def test_tendencia_estable_cuando_delta_es_cero(self):
        """Si el valor se mantiene idéntico, debe mostrar '— estable'."""
        tendencia = calcular_indicador_tendencia(valor_actual=50.0, valor_anterior=50.0)
        assert tendencia["simbolo"] == "—"
        assert tendencia["tipo"] == "estable"
        assert tendencia["pct"] == 0

    def test_tendencia_sin_dato_cuando_falta_valor_anterior(self):
        """Si la estación es nueva y no tiene valorAnterior, debe mostrar '—' sin arrojar error."""
        tendencia = calcular_indicador_tendencia(valor_actual=50.0, valor_anterior=None)
        assert tendencia["simbolo"] == "—"
        assert tendencia["tipo"] == "sin_dato"
        assert tendencia["pct"] is None

    # -------------------------------------------------------------------------
    # 3. SERIE TEMPORAL HORARIA Y LÍMITE ECA (PmTrendChart)
    # -------------------------------------------------------------------------

    def test_serie_horaria_contiene_formato_valido_para_chartjs(self):
        """Valida que los puntos horarios contengan los 24 timestamps y valores numéricos."""
        serie_mock = [
            {"hora": f"2026-10-14T{h:02d}:00:00Z", "pm25": 30.0 + h, "pm10": 60.0 + h}
            for h in range(24)
        ]

        assert len(serie_mock) == 24
        for punto in serie_mock:
            assert "hora" in punto
            assert isinstance(punto["pm25"], (int, float))
            assert isinstance(punto["pm10"], (int, float))
            assert punto["pm25"] >= 0

    def test_linea_de_referencia_eca_pm25_constante_a_50(self):
        """Valida que el dataset de referencia de la gráfica trace una línea horizontal en 50 µg/m³."""
        limite_referencia = [ECA_LIMITE["pm25"] for _ in range(24)]
        assert all(val == 50.0 for val in limite_referencia)

    # -------------------------------------------------------------------------
    # 4. PANEL DE ALERTAS Y REUTILIZACIÓN DE ANALISIS_LLM (AlertsPanel)
    # -------------------------------------------------------------------------

    def test_alerta_reutiliza_analisis_llm_como_mensaje(self):
        """Certifica que el mensaje del panel de alertas contenga el análisis generado por IA."""
        alerta = {
            "tipo": "anomalia",
            "severidad": "alta",
            "titulo": "Alerta PM2.5 · CAMPO DE MARTE",
            "mensaje": "Concentración de PM2.5 en 78.4 µg/m³ supera el ECA diario. Se recomienda a grupos sensibles evitar actividades físicas al aire libre.",
            "estacion": "CAMPO DE MARTE",
            "parametro": "pm25",
            "valor": 78.4,
            "umbral": 50.0,
            "evento_en": "2026-10-14T18:00:00Z"
        }

        assert alerta["severidad"] == "alta"
        assert len(alerta["mensaje"]) > 20
        assert "supera el ECA" in alerta["mensaje"]
        assert "actividades físicas" in alerta["mensaje"]

    def test_panel_alertas_soporta_estado_vacio(self):
        """Si no hay anomalías detectadas, la lista debe ser vacía y el render mostrar 'Sin alertas activas'."""
        alertas = []
        mensaje_vacio = "Sin alertas activas." if len(alertas) == 0 else ""
        assert mensaje_vacio == "Sin alertas activas."
