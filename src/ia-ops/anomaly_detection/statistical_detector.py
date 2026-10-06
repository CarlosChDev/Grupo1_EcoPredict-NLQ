"""
Motor Matemático Determinista de Detección Estadística de Anomalías
Proyecto EcoPredict & NLQ - Sprint 2 (HU-16 / Tarea T14)

Implementa algoritmos estadísticos puros (Z-Score sobre ventana móvil y
evaluación de umbrales normativos ECA-Aire / OMS 2021) sin dependencia de LLMs.
"""

from typing import Dict, Any, List, Optional, Tuple
import math


# =============================================================================
# CONSTANTES NORMATIVAS OFICIALES
# =============================================================================

# Estándares de Calidad Ambiental (ECA) para Aire - D.S. N° 003-2017-MINAM (Perú)
UMBRALES_ECA_MINAM = {
    "pm25": 25.0,     # µg/m³ (24 horas)
    "pm10": 100.0,    # µg/m³ (24 horas)
    "no2": 200.0,     # µg/m³ (1 hora)
    "so2": 20.0,      # µg/m³ (24 horas)
    "o3": 100.0,      # µg/m³ (8 horas)
    "co": 10000.0     # µg/m³ (8 horas) = 10 mg/m³
}

# Directrices Mundiales de la OMS sobre la Calidad del Aire (2021)
UMBRALES_OMS_2021 = {
    "pm25": 15.0,     # µg/m³ (24 horas)
    "pm10": 45.0,     # µg/m³ (24 horas)
    "no2": 25.0,      # µg/m³ (24 horas)
    "so2": 40.0,      # µg/m³ (24 horas)
    "o3": 100.0,      # µg/m³ (8 horas)
    "co": 4000.0      # µg/m³ (24 horas) = 4 mg/m³
}

# Unidades estándar por contaminante
UNIDADES_CONTAMINANTES = {
    "pm25": "µg/m³",
    "pm10": "µg/m³",
    "no2": "µg/m³",
    "so2": "µg/m³",
    "o3": "µg/m³",
    "co": "µg/m³"
}


# =============================================================================
# FUNCIONES DE CÁLCULO ESTADÍSTICO
# =============================================================================

def calcular_media_y_desviacion(valores: List[float]) -> Tuple[float, float]:
    """
    Calcula la media aritmética y la desviación estándar poblacional/muestral.
    Filtra automáticamente valores negativos y nulos.
    """
    validos = [float(v) for v in valores if v is not None and v >= 0.0]
    if not validos:
        return 0.0, 0.0
    
    n = len(validos)
    if n == 1:
        return validos[0], 0.0
    
    media = sum(validos) / n
    varianza = sum((x - media) ** 2 for x in validos) / (n - 1)
    desviacion = math.sqrt(varianza)
    return round(media, 4), round(desviacion, 4)


def calcular_z_score(valor: float, media: float, desviacion_std: float) -> float:
    """
    Calcula el Z-score estadístico: Z = (X - μ) / σ
    Si la desviación estándar es 0, retorna 0.0 para evitar división entre cero.
    """
    if valor < 0:
        raise ValueError("El valor de concentración contaminante no puede ser negativo.")
    if desviacion_std <= 0.0:
        return 0.0
    
    z = (valor - media) / desviacion_std
    return round(z, 4)


def clasificar_severidad(z_score: float, ratio_eca: float) -> str:
    """
    Determina el nivel de severidad de forma determinista y jerárquica.
    
    Niveles:
    - 'critica' : Z >= 3.5 o Ratio ECA >= 2.0 (Superación extrema)
    - 'alta'    : Z >= 2.5 o Ratio ECA >= 1.5 (Superación severa)
    - 'moderada': Z >= 2.0 o Ratio ECA >= 1.0 (Superación de norma base)
    - 'baja'    : Z < 2.0 y Ratio ECA < 1.0 (Comportamiento normal/leve)
    """
    if z_score >= 3.5 or ratio_eca >= 2.0:
        return "critica"
    elif z_score >= 2.5 or ratio_eca >= 1.5:
        return "alta"
    elif z_score >= 2.0 or ratio_eca >= 1.0:
        return "moderada"
    else:
        return "baja"


def generar_mensaje_plantilla_fija(
    estacion_nombre: str,
    parametro: str,
    valor_registrado: float,
    umbral_eca: float,
    z_score: float,
    severidad: str
) -> str:
    """
    Genera un mensaje determinista sin uso de LLM para la tabla alertas_anomalias.
    """
    param_upper = parametro.upper()
    unidad = UNIDADES_CONTAMINANTES.get(parametro.lower(), "µg/m³")
    
    if severidad == "baja":
        return f"Medición normal de {param_upper} ({valor_registrado} {unidad}) en {estacion_nombre}."
    
    return (
        f"ALERTA AMBIENTAL [{severidad.upper()}]: Se detectó un valor de {valor_registrado} {unidad} "
        f"para {param_upper} en la estación {estacion_nombre}. Supera el umbral normativo ECA-MINAM "
        f"({umbral_eca} {unidad}) con una desviación estadística Z-Score de {z_score:+.2f}σ."
    )


# =============================================================================
# EVALUADOR INTEGRAL DE ANOMALÍAS
# =============================================================================

class DetectorEstadisticoAnomalias:
    """
    Evaluador determinista de anomalías ambientales para la tabla alertas_anomalias.
    """

    def __init__(self, umbrales_norma: Optional[Dict[str, float]] = None):
        self.umbrales = umbrales_norma or UMBRALES_ECA_MINAM

    def evaluar_medicion(
        self,
        estacion_id: int,
        estacion_nombre: str,
        parametro: str,
        valor_actual: float,
        historial_30_dias: List[float],
        timestamp_medicion: str
    ) -> Dict[str, Any]:
        """
        Evalúa una medición individual contra su historial móvil de 30 días y umbrales normativos.
        """
        param_norm = parametro.lower()
        if param_norm not in self.umbrales:
            raise ValueError(f"Parámetro contaminante no reconocido: '{parametro}'")
        
        if valor_actual < 0.0:
            raise ValueError(f"Valor de medición no válido (negativo): {valor_actual}")

        umbral_base = self.umbrales[param_norm]
        media, std = calcular_media_y_desviacion(historial_30_dias)
        
        z_score = calcular_z_score(valor_actual, media, std) if len(historial_30_dias) >= 5 else 0.0
        ratio_eca = round(valor_actual / umbral_base, 4) if umbral_base > 0 else 0.0
        
        severidad = clasificar_severidad(z_score, ratio_eca)
        es_anomalia = severidad in ["moderada", "alta", "critica"]
        
        mensaje = generar_mensaje_plantilla_fija(
            estacion_nombre=estacion_nombre,
            parametro=param_norm,
            valor_registrado=valor_actual,
            umbral_eca=umbral_base,
            z_score=z_score,
            severidad=severidad
        )

        return {
            "es_anomalia": es_anomalia,
            "alerta_db_payload": {
                "estacion_id": estacion_id,
                "parametro": param_norm,
                "valor_registrado": round(valor_actual, 2),
                "umbral_base": umbral_base,
                "desviacion": z_score,
                "severidad": severidad,
                "analisis_llm": mensaje,
                "notificado_telegram": False,
                "notificado_correo": False,
                "detectado_en": timestamp_medicion
            },
            "metricas_estadisticas": {
                "media_historica": media,
                "desviacion_std": std,
                "z_score": z_score,
                "ratio_eca": ratio_eca,
                "muestras_historial": len(historial_30_dias)
            }
        }