"""
Suite de Pruebas Automatizadas de Detección Estadística de Anomalías
Proyecto EcoPredict & NLQ - Sprint 2 (HU-16 / Tarea T14)

Valida el cálculo matemático determinista de Z-Score, cumplimiento de umbrales
normativos del MINAM (D.S. 003-2017-MINAM) y OMS 2021, y la estructura de
inserción de alertas en la tabla 'alertas_anomalias'.
"""

import sys
from pathlib import Path

# Agregar directorio de anomaly_detection al path de python
RUTA_MODULO = Path(__file__).resolve().parent.parent / "anomaly_detection"
if str(RUTA_MODULO) not in sys.path:
    sys.path.insert(0, str(RUTA_MODULO))

import pytest
import time
import math
from statistical_detector import (
    DetectorEstadisticoAnomalias,
    calcular_media_y_desviacion,
    calcular_z_score,
    clasificar_severidad,
    generar_mensaje_plantilla_fija,
    UMBRALES_ECA_MINAM,
    UMBRALES_OMS_2021,
    UNIDADES_CONTAMINANTES
)


# =============================================================================
# 1. PRUEBAS DE CÁLCULO MATEMÁTICO DE Z-SCORE
# =============================================================================

class TestCalculoZScore:
    """Valida el cálculo determinista del Z-Score y media/desviación estándar."""

    def test_z_score_calculo_exacto(self):
        """Valida la fórmula Z = (X - μ) / σ con valores conocidos."""
        # X = 35.0, μ = 20.0, σ = 5.0 -> Z = (35 - 20) / 5 = 3.0
        z = calcular_z_score(35.0, 20.0, 5.0)
        assert z == 3.0, f"Se esperaba Z=3.0 pero se obtuvo {z}"

    def test_z_score_valor_igual_a_media_retorna_cero(self):
        """Si el valor es igual a la media histórica, Z debe ser exactamente 0.0."""
        z = calcular_z_score(24.5, 24.5, 6.2)
        assert z == 0.0

    def test_z_score_desviacion_cero_retorna_cero_sin_division_error(self):
        """Si σ = 0 (todas las mediciones fueron idénticas), debe retornar 0.0 sin crashear."""
        z = calcular_z_score(30.0, 30.0, 0.0)
        assert z == 0.0

    def test_z_score_valor_menor_a_media_retorna_negativo(self):
        """Si el valor está por debajo de la media, Z debe ser negativo."""
        z = calcular_z_score(10.0, 20.0, 5.0)
        assert z == -2.0

    def test_z_score_rechaza_concentracion_negativa(self):
        """Valores de concentración negativos deben lanzar ValueError."""
        with pytest.raises(ValueError, match="no puede ser negativo"):
            calcular_z_score(-5.0, 20.0, 5.0)

    def test_media_y_desviacion_calculo_correcto(self):
        """Verifica el cálculo de media y desviación sobre una serie numérica."""
        datos = [10.0, 20.0, 30.0, 40.0, 50.0]
        media, std = calcular_media_y_desviacion(datos)
        assert media == 30.0
        assert math.isclose(std, 15.8114, abs_tol=1e-3)


# =============================================================================
# 2. PRUEBAS DE UMBRALES NORMATIVOS (ECA MINAM Y OMS 2021)
# =============================================================================

class TestUmbralesNormativosECAyOMS:
    """Valida los límites normativos oficiales por contaminante."""

    @pytest.mark.parametrize("parametro,umbral_esperado", [
        ("pm25", 25.0),
        ("pm10", 100.0),
        ("no2", 200.0),
        ("so2", 20.0),
        ("o3", 100.0),
        ("co", 10000.0),
    ])
    def test_umbrales_oficiales_eca_minam(self, parametro, umbral_esperado):
        """Valida que los umbrales ECA MINAM (D.S. 003-2017-MINAM) sean exactos."""
        assert parametro in UMBRALES_ECA_MINAM
        assert UMBRALES_ECA_MINAM[parametro] == umbral_esperado

    @pytest.mark.parametrize("parametro,umbral_oms", [
        ("pm25", 15.0),
        ("pm10", 45.0),
        ("no2", 25.0),
        ("so2", 40.0),
        ("o3", 100.0),
        ("co", 4000.0),
    ])
    def test_umbrales_oficiales_oms_2021(self, parametro, umbral_oms):
        """Valida que los umbrales de la OMS 2021 coincidan con las directrices internacionales."""
        assert parametro in UMBRALES_OMS_2021
        assert UMBRALES_OMS_2021[parametro] == umbral_oms

    def test_todas_las_unidades_son_validas(self):
        """Valida que todos los 6 contaminantes tengan unidades normativas asignadas."""
        assert len(UNIDADES_CONTAMINANTES) == 6
        for param, unidad in UNIDADES_CONTAMINANTES.items():
            assert unidad == "µg/m³", f"Unidad inesperada para {param}: {unidad}"


# =============================================================================
# 3. PRUEBAS DE CLASIFICACIÓN DETERMINISTA DE SEVERIDAD
# =============================================================================

class TestClasificacionSeveridad:
    """Valida las transiciones de severidad: baja, moderada, alta, critica."""

    def test_severidad_critica_por_z_score_extremo(self):
        """Z >= 3.5 debe ser clasificado como 'critica'."""
        assert clasificar_severidad(z_score=3.8, ratio_eca=0.9) == "critica"

    def test_severidad_critica_por_ratio_eca_duplicado(self):
        """Ratio ECA >= 2.0 (doble de la norma) debe ser clasificado como 'critica'."""
        assert clasificar_severidad(z_score=1.2, ratio_eca=2.2) == "critica"

    def test_severidad_alta_por_z_score(self):
        """Z en rango [2.5, 3.5) debe ser 'alta'."""
        assert clasificar_severidad(z_score=2.8, ratio_eca=0.8) == "alta"

    def test_severidad_alta_por_ratio_eca(self):
        """Ratio ECA en rango [1.5, 2.0) debe ser 'alta'."""
        assert clasificar_severidad(z_score=1.5, ratio_eca=1.6) == "alta"

    def test_severidad_moderada_por_superacion_base_eca(self):
        """Superar el ECA (Ratio >= 1.0) o Z >= 2.0 clasifica como 'moderada'."""
        assert clasificar_severidad(z_score=2.1, ratio_eca=0.9) == "moderada"
        assert clasificar_severidad(z_score=1.1, ratio_eca=1.05) == "moderada"

    def test_severidad_baja_comportamiento_dentro_de_norma(self):
        """Valores dentro del rango habitual y bajo el ECA son 'baja'."""
        assert clasificar_severidad(z_score=1.2, ratio_eca=0.6) == "baja"


# =============================================================================
# 4. PRUEBAS DE ESTRUCTURA Y SCHEMA DE ALERTAS (alertas_anomalias)
# =============================================================================

class TestEstructuraAlertaPayload:
    """Valida la conformidad con el esquema relacional de la tabla alertas_anomalias."""

    @pytest.fixture
    def detector(self):
        return DetectorEstadisticoAnomalias()

    @pytest.fixture
    def historial_sano(self):
        return [12.0, 14.5, 13.2, 15.0, 14.0, 13.8, 12.9, 14.1, 15.2, 13.5]

    def test_deteccion_anomalia_pm25_extrema(self, detector, historial_sano):
        """Evalúa un pico extremo de PM2.5 (78 µg/m³) sobre un historial promedio de 14 µg/m³."""
        resultado = detector.evaluar_medicion(
            estacion_id=1,
            estacion_nombre="CAMPO DE MARTE",
            parametro="pm25",
            valor_actual=78.5,
            historial_30_dias=historial_sano,
            timestamp_medicion="2026-09-07T12:00:00Z"
        )
        assert resultado["es_anomalia"] is True
        payload = resultado["alerta_db_payload"]
        assert payload["estacion_id"] == 1
        assert payload["parametro"] == "pm25"
        assert payload["valor_registrado"] == 78.5
        assert payload["umbral_base"] == 25.0
        assert payload["desviacion"] > 3.5
        assert payload["severidad"] == "critica"
        assert "ALERTA AMBIENTAL [CRITICA]" in payload["analisis_llm"]

    def test_campos_obligatorios_payload_db(self, detector, historial_sano):
        """Verifica que todos los campos requeridos por el esquema SQL estén presentes."""
        res = detector.evaluar_medicion(
            estacion_id=2,
            estacion_nombre="SAN BORJA",
            parametro="so2",
            valor_actual=45.0,
            historial_30_dias=historial_sano,
            timestamp_medicion="2026-09-07T15:00:00Z"
        )
        payload = res["alerta_db_payload"]
        campos_esperados = [
            "estacion_id", "parametro", "valor_registrado", "umbral_base",
            "desviacion", "severidad", "analisis_llm", "notificado_telegram",
            "notificado_correo", "detectado_en"
        ]
        for campo in campos_esperados:
            assert campo in payload, f"Campo faltante en payload: {campo}"

    def test_plantilla_fija_no_depende_de_llm(self):
        """Verifica que el mensaje se genere con plantilla fija sin llamadas externas."""
        msg = generar_mensaje_plantilla_fija(
            estacion_nombre="ATE",
            parametro="pm10",
            valor_registrado=185.0,
            umbral_eca=100.0,
            z_score=3.25,
            severidad="alta"
        )
        assert "ATE" in msg
        assert "PM10" in msg
        assert "185.0" in msg
        assert "100.0" in msg
        assert "+3.25σ" in msg


# =============================================================================
# 5. PRUEBAS DE CASOS BORDE Y LIMPIEZA DE DATOS
# =============================================================================

class TestCasosBordeYLimpiezaDatos:
    """Valida la tolerancia ante datos sucios, nulos o muestras insuficientes."""

    def test_historial_filtra_valores_negativos_y_nulos(self):
        """Valores corruptos como -99.9 o None deben ser descartados automáticamente."""
        datos_corruptos = [15.0, -99.9, None, 20.0, -1.0, 25.0]
        media, std = calcular_media_y_desviacion(datos_corruptos)
        assert media == 20.0  # (15 + 20 + 25) / 3 = 20.0

    def test_historial_insuficiente_no_calcula_z_score_falso(self):
        """Si hay menos de 5 muestras históricas, no calcula Z-Score espurio."""
        detector = DetectorEstadisticoAnomalias()
        res = detector.evaluar_medicion(
            estacion_id=1,
            estacion_nombre="CAMPO DE MARTE",
            parametro="pm25",
            valor_actual=30.0,
            historial_30_dias=[20.0, 22.0],
            timestamp_medicion="2026-09-07T12:00:00Z"
        )
        assert res["metricas_estadisticas"]["z_score"] == 0.0

    def test_parametro_desconocido_lanza_error(self):
        """Parámetros no reconocidos como 'plomo' o 'ruido' deben ser rechazados."""
        detector = DetectorEstadisticoAnomalias()
        with pytest.raises(ValueError, match="no reconocido"):
            detector.evaluar_medicion(
                estacion_id=1,
                estacion_nombre="CAMPO DE MARTE",
                parametro="parametro_invalido",
                valor_actual=10.0,
                historial_30_dias=[10.0, 12.0, 11.0, 10.5, 11.5],
                timestamp_medicion="2026-09-07T12:00:00Z"
            )


# =============================================================================
# 6. PRUEBAS DE DETERMINISMO Y TIEMPO DE RESPUESTA (SLA)
# =============================================================================

class TestDeterminismoYPerformance:
    """Valida que la evaluación sea bit a bit idéntica y de alta velocidad (< 5ms)."""

    def test_determinismo_bit_a_bit(self):
        """100 ejecuciones consecutivas con los mismos datos deben dar exactamente el mismo resultado."""
        detector = DetectorEstadisticoAnomalias()
        historial = [10.0, 12.0, 14.0, 16.0, 18.0, 20.0]
        
        primer_resultado = detector.evaluar_medicion(1, "ATE", "pm25", 45.0, historial, "2026-09-07T12:00:00Z")
        for _ in range(100):
            res = detector.evaluar_medicion(1, "ATE", "pm25", 45.0, historial, "2026-09-07T12:00:00Z")
            assert res == primer_resultado

    def test_tiempo_de_ejecucion_menor_a_5ms(self):
        """El cálculo matemático puro debe resolverse en menos de 5 milisegundos."""
        detector = DetectorEstadisticoAnomalias()
        historial = [10.0 + (i * 0.5) for i in range(30)]
        
        t0 = time.perf_counter()
        detector.evaluar_medicion(1, "CAMPO DE MARTE", "pm25", 85.0, historial, "2026-09-07T12:00:00Z")
        duracion_ms = (time.perf_counter() - t0) * 1000
        
        assert duracion_ms < 5.0, f"Evaluación tomó {duracion_ms:.2f} ms (SLA < 5ms)"