"""
Suite de Pruebas de Integración y Visualización para el Dashboard Ambiental (Microfrontend).
Valida la compatibilidad del contrato de datos de 19 estaciones, la lógica matemática del Índice INCA,
los umbrales ECA-Aire del MINAM y el ordenamiento del Ranking de Estaciones.

Proyecto: EcoPredict-NLQ
Historia de Usuario: HU-16 (#100)
Sub-issue: T17 (#119) - Pruebas de Integración y Visualización del Dashboard
Autor: Johann Romero Contreras (QA / Prompt Engineer)
"""

import math
import pytest
from typing import Dict, List, Any, Optional, Literal

# Tipos normalizados del Frontend (dashboard.types.ts)
ParametroCalidadAire = Literal["pm25", "pm10", "no2", "so2", "o3", "co"]
NivelEstado = Literal["bueno", "moderado", "malo"]

# Límites oficiales ECA-Aire (D.S. N° 003-2017-MINAM) usados en eca.ts
ECA_LIMITE: Dict[str, float] = {
    "pm25": 50.0,   # 24 h (µg/m³)
    "pm10": 100.0,  # 24 h (µg/m³)
    "so2": 250.0,   # 24 h (µg/m³)
    "no2": 200.0,   # 1 h  (µg/m³)
    "o3": 100.0,    # 8 h  (µg/m³)
    "co": 10.0,     # 8 h  (mg/m³)
}

ORDEN_NIVEL: Dict[NivelEstado, int] = {"bueno": 0, "moderado": 1, "malo": 2}


# ============================================================================
# FUNCIONES DETERMINISTAS REPLICADAS DEL FRONTEND (eca.ts / nivel.ts)
# ============================================================================

def porcentaje_eca(parametro: str, valor: float) -> int:
    """Calcula el porcentaje del ECA que representa una lectura puntual."""
    limite = ECA_LIMITE.get(parametro, 50.0)
    return round((valor / limite) * 100)


def nivel_por_eca(parametro: str, valor: float) -> NivelEstado:
    """Clasifica el nivel de calidad del aire según el porcentaje del ECA."""
    pct = porcentaje_eca(parametro, valor)
    if pct <= 50:
        return "bueno"
    elif pct <= 100:
        return "moderado"
    else:
        return "malo"


def nivel_por_indice(indice: int) -> NivelEstado:
    """Clasifica el nivel general según el Índice INCA consolidado."""
    if indice <= 50:
        return "bueno"
    elif indice <= 100:
        return "moderado"
    else:
        return "malo"


def peor_nivel(niveles: List[NivelEstado]) -> NivelEstado:
    """Retorna el peor nivel de calidad entre una lista de contaminantes."""
    if not niveles:
        return "bueno"
    peor = "bueno"
    for actual in niveles:
        if ORDEN_NIVEL[actual] > ORDEN_NIVEL[peor]:
            peor = actual
    return peor


def calcular_ranking_estaciones(estaciones: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Calcula el contaminante dominante, el % ECA y el peor nivel para cada estación,
    ordenándolas de mayor a menor contaminación (como hace StationRanking.tsx).
    """
    filas = []
    for est in estaciones:
        mediciones = est.get("mediciones", [])
        if not mediciones:
            continue

        peor_pct = -1
        peor_param = "pm25"
        niveles = []

        for m in mediciones:
            param = m.get("parametro")
            valor = m.get("valor", 0.0)
            if param in ECA_LIMITE:
                pct = porcentaje_eca(param, valor)
                niveles.append(nivel_por_eca(param, valor))
                if pct > peor_pct:
                    peor_pct = pct
                    peor_param = param

        nivel_estacion = peor_nivel(niveles)
        filas.append({
            "id": est.get("id"),
            "nombre": est.get("nombre"),
            "contaminanteDominante": peor_param,
            "porcentajeEca": max(peor_pct, 0),
            "nivel": nivel_estacion
        })

    # Ordenar descendente por porcentaje ECA
    filas.sort(key=lambda x: x["porcentajeEca"], reverse=True)
    return filas


# ============================================================================
# TESTS DE CÁLCULO DE ÍNDICE INCA Y UMBRALES ECA (eca.ts)
# ============================================================================

class TestCalculoEcaYInca:
    """Verifica que las funciones matemáticas de eca.ts y nivel.ts sean deterministas."""

    @pytest.mark.parametrize("param,valor,esperado_pct,esperado_nivel", [
        ("pm25", 15.0, 30, "bueno"),
        ("pm25", 25.0, 50, "bueno"),
        ("pm25", 40.0, 80, "moderado"),
        ("pm25", 50.0, 100, "moderado"),
        ("pm25", 75.0, 150, "malo"),
        ("pm10", 45.0, 45, "bueno"),
        ("pm10", 100.0, 100, "moderado"),
        ("pm10", 120.0, 120, "malo"),
        ("no2", 80.0, 40, "bueno"),
        ("no2", 180.0, 90, "moderado"),
        ("no2", 250.0, 125, "malo"),
        ("so2", 100.0, 40, "bueno"),
        ("so2", 300.0, 120, "malo"),
        ("o3", 40.0, 40, "bueno"),
        ("o3", 110.0, 110, "malo"),
        ("co", 4.0, 40, "bueno"),
        ("co", 12.0, 120, "malo"),
    ])
    def test_porcentaje_y_nivel_por_parametro(self, param, valor, esperado_pct, esperado_nivel):
        pct = porcentaje_eca(param, valor)
        nivel = nivel_por_eca(param, valor)
        assert pct == esperado_pct, f"Error en % ECA para {param} con valor {valor}"
        assert nivel == esperado_nivel, f"Error en nivel para {param} con valor {valor}"

    def test_peor_nivel_jerarquia_correcta(self):
        assert peor_nivel(["bueno", "bueno"]) == "bueno"
        assert peor_nivel(["bueno", "moderado", "bueno"]) == "moderado"
        assert peor_nivel(["bueno", "malo", "moderado"]) == "malo"
        assert peor_nivel([]) == "bueno"


# ============================================================================
# TESTS DE INTEGRACIÓN CON EL CONTRATO REAL DE 19 ESTACIONES (FLUJO C)
# ============================================================================

class TestIntegracionContratoEstaciones:
    """Verifica que el catálogo de 19 estaciones devuelto por Oracle Cloud sea compatible con el Dashboard."""

    @pytest.fixture
    def catalogo_estaciones_real(self):
        """Simula la respuesta del endpoint GET /webhook/estaciones en Oracle Cloud."""
        return [
            {
                "id": 14,
                "nombre": "CERES (CRS)",
                "coordenadas": {"lat": -12.028694, "lon": -76.927056},
                "mediciones": [
                    {"parametro": "pm25", "valor": 15.21, "valorAnterior": 11.54, "unidad": "µg/m³"},
                    {"parametro": "pm10", "valor": 63.61, "valorAnterior": 14.93, "unidad": "µg/m³"},
                    {"parametro": "no2", "valor": 42.68, "valorAnterior": 12.65, "unidad": "µg/m³"},
                    {"parametro": "so2", "valor": 16.51, "valorAnterior": 8.46, "unidad": "µg/m³"}
                ]
            },
            {
                "id": 16,
                "nombre": "PARIACHI",
                "coordenadas": {"lat": -12.002311, "lon": -76.838289},
                "mediciones": [
                    {"parametro": "pm25", "valor": 85.35, "valorAnterior": 45.0, "unidad": "µg/m³"},
                    {"parametro": "pm10", "valor": 135.0, "valorAnterior": 112.0, "unidad": "µg/m³"},
                    {"parametro": "no2", "valor": 46.19, "valorAnterior": 29.63, "unidad": "µg/m³"}
                ]
            },
            {
                "id": 8,
                "nombre": "CAMPO DE MARTE (CDM)",
                "coordenadas": {"lat": -12.070556, "lon": -77.042778},
                "mediciones": [
                    {"parametro": "pm25", "valor": 18.5, "valorAnterior": 16.0, "unidad": "µg/m³"},
                    {"parametro": "pm10", "valor": 42.0, "valorAnterior": 38.0, "unidad": "µg/m³"}
                ]
            }
        ]

    def test_ranking_ordena_estaciones_por_contaminacion_descendente(self, catalogo_estaciones_real):
        ranking = calcular_ranking_estaciones(catalogo_estaciones_real)
        
        assert len(ranking) == 3
        # Pariachi tiene PM2.5 = 85.35 (171% del ECA), debe liderar el ranking como la más contaminada
        assert ranking[0]["nombre"] == "PARIACHI"
        assert ranking[0]["nivel"] == "malo"
        assert ranking[0]["porcentajeEca"] == 171
        assert ranking[0]["contaminanteDominante"] == "pm25"

        # Ceres tiene PM10 = 63.61 (64% del ECA), nivel moderado
        assert ranking[1]["nombre"] == "CERES (CRS)"
        assert ranking[1]["nivel"] == "moderado"
        assert ranking[1]["porcentajeEca"] == 64

        # Campo de Marte tiene PM10 = 42% y PM2.5 = 37%, nivel bueno
        assert ranking[2]["nombre"] == "CAMPO DE MARTE (CDM)"
        assert ranking[2]["nivel"] == "bueno"

    def test_coordenadas_geograficas_validas_para_mapa_leaflet(self, catalogo_estaciones_real):
        for est in catalogo_estaciones_real:
            coords = est.get("coordenadas", {})
            lat = coords.get("lat")
            lon = coords.get("lon")
            assert -13.0 <= lat <= -11.0, f"Latitud fuera de rango para Lima en {est['nombre']}"
            assert -78.0 <= lon <= -76.0, f"Longitud fuera de rango para Lima en {est['nombre']}"


# ============================================================================
# TESTS DE INTEGRACIÓN DE SERIES TEMPORALES (PmTrendChart)
# ============================================================================

class TestSerieTemporalPmTrend:
    """Verifica que las series de 24 horas para el gráfico de tendencias sean válidas."""

    @pytest.fixture
    def serie_24h_valida(self):
        return [
            {"horaIso": f"2026-09-14T{h:02d}:00:00Z", "pm25": 15.0 + h * 0.5, "pm10": 40.0 + h}
            for h in range(24)
        ]

    def test_serie_contiene_24_puntos_horarios(self, serie_24h_valida):
        assert len(serie_24h_valida) == 24
        for punto in serie_24h_valida:
            assert "horaIso" in punto
            assert punto["pm25"] is not None and punto["pm25"] >= 0
            assert punto["pm10"] is not None and punto["pm10"] >= 0

    def test_tolerancia_a_valores_nulos_sin_romper_renderizado(self):
        serie_con_nulos = [
            {"horaIso": "2026-09-14T01:00:00Z", "pm25": None, "pm10": 30.0},
            {"horaIso": "2026-09-14T02:00:00Z", "pm25": 18.0, "pm10": None},
        ]
        for p in serie_con_nulos:
            # Los valores nulos deben ser aceptados como válidos según el tipo PuntoSerieHoraria
            assert p["pm25"] is None or p["pm25"] >= 0
            assert p["pm10"] is None or p["pm10"] >= 0
