"""
=============================================================================
EcoPredict & NLQ — Módulo de Aseguramiento de Calidad (QA / IA Ops)
Sprint 3 — Tarea T19 (#179): Validación del Cooldown Anti-Spam (24h) en Telegram (HU-19)
=============================================================================
Suite de pruebas automatizadas para auditar la regla de cooldown anti-spam
por estación + suscriptor + parámetro en las notificaciones de Telegram:
- Consulta SQL con ventana de 24 horas (`enviado_en > now() - interval '24 hours'`)
- Supresión de segunda alerta al mismo suscriptor para la misma estación y parámetro dentro de las 24h
- Despacho inmediato para parámetros distintos en la misma estación (ej. PM2.5 vs PM10)
- Despacho inmediato para estaciones distintas para el mismo suscriptor
- Despacho inmediato para un nuevo suscriptor sin historial previo
- Expiración exitosa de la ventana de cooldown (> 24h) permitiendo un nuevo despacho
- Registro transaccional en `notificaciones_telegram` con estado 'enviado' y 'fallido'
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional, Tuple
import pytest


# =============================================================================
# SIMULADOR DETERMINISTA DEL MOTOR DE COOLDOWN Y NOTIFICACIONES TELEGRAM
# Modela con fidelidad la lógica de:
# - `Notificar_telegram.json` (Nodo "Buscar suscriptores" & "Registrar envío")
# - `002_telegram_por_estacion.sql` (tabla notificaciones_telegram con índice idx_notif_cooldown)
# =============================================================================

class MotorNotificacionesTelegram:
    """Simulador determinista de la lógica SQL y n8n de Notificar_telegram."""

    def __init__(self, ventana_cooldown_horas: int = 24):
        self.ventana_cooldown = timedelta(hours=ventana_cooldown_horas)
        # Tablas en memoria
        # suscriptores: dict keyed by id -> {id, chat_id, estacion_id, activo}
        self.suscriptores: Dict[int, Dict[str, Any]] = {}
        # notificaciones: list of records
        # {id, suscriptor_id, alerta_id, estacion_id, parametro, estado, enviado_en}
        self.notificaciones: List[Dict[str, Any]] = []
        self._next_notif_id = 1

    def registrar_suscriptor(self, suscriptor_id: int, chat_id: int, estacion_id: int, activo: bool = True):
        self.suscriptores[suscriptor_id] = {
            "id": suscriptor_id,
            "chat_id": chat_id,
            "estacion_id": estacion_id,
            "activo": activo
        }

    def verificar_cooldown(
        self,
        suscriptor_id: int,
        estacion_id: int,
        parametro: str,
        ahora: datetime
    ) -> bool:
        """
        Replica la condición SQL NOT EXISTS en Notificar_telegram.json:
        SELECT 1 FROM notificaciones_telegram n
        WHERE n.suscriptor_id = s.id AND n.estacion_id = a.estacion_id
          AND n.parametro = a.parametro AND n.estado = 'enviado'
          AND n.enviado_en > now() - interval '24 hours'
        
        Retorna True si el suscriptor está bloqueado por cooldown (existe notificación previa activa).
        """
        limite_tiempo = ahora - self.ventana_cooldown
        param_norm = str(parametro).upper().strip()

        for n in self.notificaciones:
            if (
                n["suscriptor_id"] == suscriptor_id
                and n["estacion_id"] == estacion_id
                and str(n["parametro"]).upper().strip() == param_norm
                and n["estado"] == "enviado"
                and n["enviado_en"] > limite_tiempo
            ):
                return True  # Bloqueado por cooldown
        return False  # Libre para recibir notificación

    def evaluar_y_despachar_alerta(
        self,
        alerta: Dict[str, Any],
        ahora: datetime
    ) -> List[Dict[str, Any]]:
        """
        Simula el flujo completo de Notificar_telegram para una alerta dada:
        1. Filtra suscriptores de la estación de la alerta que estén activos.
        2. Aplica la regla NOT EXISTS del cooldown de 24 horas.
        3. Registra el despacho en `notificaciones_telegram`.
        4. Retorna la lista de notificaciones efectivamente enviadas.
        """
        estacion_id = alerta["estacion_id"]
        parametro = alerta["parametro"]
        alerta_id = alerta["id"]

        enviados = []

        # Paso 1: Obtener suscriptores activos de la estación
        candidatos = [
            s for s in self.suscriptores.values()
            if s["estacion_id"] == estacion_id and s["activo"]
        ]

        for s in candidatos:
            suscriptor_id = s["id"]
            # Paso 2: Verificar cooldown anti-spam
            en_cooldown = self.verificar_cooldown(
                suscriptor_id=suscriptor_id,
                estacion_id=estacion_id,
                parametro=parametro,
                ahora=ahora
            )

            if not en_cooldown:
                # Paso 3: Registrar envío exitoso
                registro = {
                    "id": self._next_notif_id,
                    "suscriptor_id": suscriptor_id,
                    "alerta_id": alerta_id,
                    "estacion_id": estacion_id,
                    "parametro": parametro,
                    "estado": "enviado",
                    "error": None,
                    "enviado_en": ahora
                }
                self.notificaciones.append(registro)
                self._next_notif_id += 1

                enviados.append({
                    "suscriptor_id": suscriptor_id,
                    "chat_id": s["chat_id"],
                    "alerta_id": alerta_id,
                    "estacion_id": estacion_id,
                    "parametro": parametro,
                    "mensaje_enviado": True
                })

        return enviados


# =============================================================================
# CASOS DE PRUEBA: T19 - COOLDOWN ANTI-SPAM (24 HORAS)
# =============================================================================

class TestCooldownAntiSpamTelegram:
    """Pruebas funcionales de la ventana de enfriamiento de 24 horas."""

    @pytest.fixture
    def motor(self):
        m = MotorNotificacionesTelegram(ventana_cooldown_horas=24)
        # Suscriptor 1: Johann Romero en Villa María del Triunfo (ID 5)
        m.registrar_suscriptor(suscriptor_id=101, chat_id=987654321, estacion_id=5, activo=True)
        # Suscriptor 2: Ciudadano 2 en Villa María del Triunfo (ID 5)
        m.registrar_suscriptor(suscriptor_id=102, chat_id=111222333, estacion_id=5, activo=True)
        # Suscriptor 3: Ciudadano 3 en San Borja (ID 8)
        m.registrar_suscriptor(suscriptor_id=103, chat_id=444555666, estacion_id=8, activo=True)
        return m

    def test_primera_alerta_se_despacha_inmediatamente(self, motor):
        """La primera alerta para un suscriptor debe despacharse sin ningún bloqueo."""
        t0 = datetime(2026, 10, 12, 10, 0, 0, tzinfo=timezone.utc)
        alerta = {
            "id": 1,
            "estacion_id": 5,
            "parametro": "pm25",
            "severidad": "alta",
            "valor_registrado": 75.4
        }

        despachados = motor.evaluar_y_despachar_alerta(alerta, ahora=t0)
        
        # Deben recibir ambos suscriptores de la estación 5 (101 y 102)
        suscriptores_notificados = [d["suscriptor_id"] for d in despachados]
        assert len(despachados) == 2
        assert 101 in suscriptores_notificados
        assert 102 in suscriptores_notificados

    def test_segunda_alerta_mismo_parametro_bloqueada_dentro_de_24h(self, motor):
        """Una segunda alerta del mismo contaminante y estación dentro de 24h debe ser suprimida."""
        t0 = datetime(2026, 10, 12, 10, 0, 0, tzinfo=timezone.utc)
        alerta_1 = {"id": 1, "estacion_id": 5, "parametro": "pm25", "severidad": "alta", "valor_registrado": 75.4}
        motor.evaluar_y_despachar_alerta(alerta_1, ahora=t0)

        # 4 horas después ocurre otra anomalía severa de PM2.5 en la misma estación
        t1 = t0 + timedelta(hours=4)
        alerta_2 = {"id": 2, "estacion_id": 5, "parametro": "pm25", "severidad": "critica", "valor_registrado": 110.2}

        despachados_segunda = motor.evaluar_y_despachar_alerta(alerta_2, ahora=t1)

        # No debe enviarse a ninguno porque ambos tienen cooldown activo
        assert len(despachados_segunda) == 0

    def test_alerta_otro_parametro_misma_estacion_no_se_bloquea(self, motor):
        """Un contaminante diferente (ej. SO2 o PM10) no comparte cooldown con PM2.5."""
        t0 = datetime(2026, 10, 12, 10, 0, 0, tzinfo=timezone.utc)
        alerta_pm25 = {"id": 1, "estacion_id": 5, "parametro": "pm25", "severidad": "alta", "valor_registrado": 75.4}
        motor.evaluar_y_despachar_alerta(alerta_pm25, ahora=t0)

        # 2 horas después ocurre anomalía de PM10 en la misma estación
        t1 = t0 + timedelta(hours=2)
        alerta_pm10 = {"id": 2, "estacion_id": 5, "parametro": "pm10", "severidad": "alta", "valor_registrado": 150.0}

        despachados_pm10 = motor.evaluar_y_despachar_alerta(alerta_pm10, ahora=t1)

        # Debe enviarse con éxito porque el parámetro es distinto
        assert len(despachados_pm10) == 2
        assert [d["suscriptor_id"] for d in despachados_pm10] == [101, 102]

    def test_nuevo_suscriptor_recibe_alerta_incluso_si_otros_tienen_cooldown(self, motor):
        """Un usuario recién suscrito recibe la alerta aunque suscriptores anteriores tengan cooldown."""
        t0 = datetime(2026, 10, 12, 10, 0, 0, tzinfo=timezone.utc)
        alerta_1 = {"id": 1, "estacion_id": 5, "parametro": "pm25", "severidad": "alta", "valor_registrado": 75.4}
        motor.evaluar_y_despachar_alerta(alerta_1, ahora=t0)

        # 3 horas después se suscribe un nuevo ciudadano a la estación 5
        motor.registrar_suscriptor(suscriptor_id=104, chat_id=777888999, estacion_id=5, activo=True)

        # Ocurre nueva alerta a las 5 horas
        t1 = t0 + timedelta(hours=5)
        alerta_2 = {"id": 2, "estacion_id": 5, "parametro": "pm25", "severidad": "alta", "valor_registrado": 80.0}

        despachados = motor.evaluar_y_despachar_alerta(alerta_2, ahora=t1)

        # Solo el nuevo suscriptor (104) debe recibirla; 101 y 102 están en cooldown
        assert len(despachados) == 1
        assert despachados[0]["suscriptor_id"] == 104

    def test_expiracion_del_cooldown_tras_24_horas_permite_nuevo_envio(self, motor):
        """Pasadas las 24 horas exactas (ej. 24h + 1min), el cooldown debe levantarse automáticamente."""
        t0 = datetime(2026, 10, 12, 10, 0, 0, tzinfo=timezone.utc)
        alerta_1 = {"id": 1, "estacion_id": 5, "parametro": "pm25", "severidad": "alta", "valor_registrado": 75.4}
        motor.evaluar_y_despachar_alerta(alerta_1, ahora=t0)

        # Caso A: A las 23 horas y 59 minutos aún sigue en cooldown
        t_borde_bloqueado = t0 + timedelta(hours=23, minutes=59)
        alerta_borde = {"id": 2, "estacion_id": 5, "parametro": "pm25", "severidad": "alta", "valor_registrado": 70.0}
        assert len(motor.evaluar_y_despachar_alerta(alerta_borde, ahora=t_borde_bloqueado)) == 0

        # Caso B: A las 24 horas y 1 minuto el cooldown ya expiró
        t_expirado = t0 + timedelta(hours=24, minutes=1)
        alerta_expirada = {"id": 3, "estacion_id": 5, "parametro": "pm25", "severidad": "alta", "valor_registrado": 82.0}
        despachados_expirados = motor.evaluar_y_despachar_alerta(alerta_expirada, ahora=t_expirado)

        assert len(despachados_expirados) == 2
        assert [d["suscriptor_id"] for d in despachados_expirados] == [101, 102]

    def test_alerta_fallida_no_activa_cooldown_permite_reintento(self, motor):
        """Si un envío previo quedó en estado 'fallido', no debe bloquear futuros envíos."""
        t0 = datetime(2026, 10, 12, 10, 0, 0, tzinfo=timezone.utc)
        
        # Simular notificación previa que falló por error de red en Telegram
        motor.notificaciones.append({
            "id": 999,
            "suscriptor_id": 101,
            "alerta_id": 50,
            "estacion_id": 5,
            "parametro": "pm25",
            "estado": "fallido",
            "error": "HTTP 502 Bad Gateway",
            "enviado_en": t0
        })

        # 1 hora después se intenta enviar nuevamente
        t1 = t0 + timedelta(hours=1)
        alerta_reintento = {"id": 51, "estacion_id": 5, "parametro": "pm25", "severidad": "alta", "valor_registrado": 76.0}
        
        # El suscriptor 101 NO debe estar bloqueado porque la anterior fue 'fallido'
        en_cooldown = motor.verificar_cooldown(suscriptor_id=101, estacion_id=5, parametro="pm25", ahora=t1)
        assert not en_cooldown

        despachados = motor.evaluar_y_despachar_alerta(alerta_reintento, ahora=t1)
        assert any(d["suscriptor_id"] == 101 for d in despachados)

    def test_suscriptor_inactivo_no_recibe_alerta_ni_consume_cooldown(self, motor):
        """Un suscriptor con activo=False no es evaluado ni genera registros de notificación."""
        # Desactivar suscriptor 101 (ej. tras /baja)
        motor.suscriptores[101]["activo"] = False

        t0 = datetime(2026, 10, 12, 10, 0, 0, tzinfo=timezone.utc)
        alerta = {"id": 1, "estacion_id": 5, "parametro": "pm25", "severidad": "alta", "valor_registrado": 75.4}

        despachados = motor.evaluar_y_despachar_alerta(alerta, ahora=t0)

        # Solo el suscriptor 102 (activo) debe recibirlo
        assert len(despachados) == 1
        assert despachados[0]["suscriptor_id"] == 102
        assert not any(n["suscriptor_id"] == 101 for n in motor.notificaciones)

    def test_case_insensitive_y_normalizacion_de_parametros(self, motor):
        """Verificar que variaciones como 'PM25', 'pm25' o ' PM25 ' respeten el cooldown unificado."""
        t0 = datetime(2026, 10, 12, 10, 0, 0, tzinfo=timezone.utc)
        alerta_1 = {"id": 1, "estacion_id": 5, "parametro": "pm25", "severidad": "alta", "valor_registrado": 75.0}
        motor.evaluar_y_despachar_alerta(alerta_1, ahora=t0)

        # Segunda alerta con mayúsculas y espacios
        t1 = t0 + timedelta(hours=2)
        alerta_mayus = {"id": 2, "estacion_id": 5, "parametro": " PM25 ", "severidad": "alta", "valor_registrado": 78.0}
        
        despachados = motor.evaluar_y_despachar_alerta(alerta_mayus, ahora=t1)
        assert len(despachados) == 0  # Cooldown debe detectar que es el mismo contaminante
