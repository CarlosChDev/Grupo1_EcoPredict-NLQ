"""
=============================================================================
EcoPredict & NLQ — Módulo de Aseguramiento de Calidad (QA / IA Ops)
Sprint 3 — Tarea T18 (#178): Pruebas de Notificación y Suscripción en Telegram (HU-19)
=============================================================================
Suite de pruebas automatizadas para validar el Bot de Telegram de EcoPredict:
- Procesamiento de comandos (/start, /estaciones, /suscribir N, /baja N, /otro)
- Gestión de suscriptores y unicidad (chat_id, estacion_id) en base de datos
- Filtrado estricto por zona/estación (aislamiento de ciudadanos)
- Formato del mensaje con análisis redactado por IA (analisis_llm) y límites
"""

from datetime import datetime, timezone
import re
from typing import Dict, Any, List, Optional, Tuple
import pytest


# =============================================================================
# SIMULADOR DETERMINISTA DEL MOTOR DE TELEGRAM (n8n & Postgres)
# Replica la lógica de los workflows:
# - Bot_telegram_comandos.json
# - Notificar_telegram.json
# - 002_telegram_por_estacion.sql
# =============================================================================
ESTACIONES_FIXTURE = [
    {"id": 1, "nombre": "San Borja (SBJ)", "activo": True},
    {"id": 2, "nombre": "Carabayllo", "activo": True},
    {"id": 3, "nombre": "Huachipa", "activo": True},
    {"id": 4, "nombre": "Santa Anita", "activo": True},
    {"id": 5, "nombre": "Villa María del Triunfo (VMT)", "activo": True},
    {"id": 6, "nombre": "Puente Piedra", "activo": True},
    {"id": 7, "nombre": "San Juan de Lurigancho (SJL)", "activo": True},
    {"id": 8, "nombre": "Campo de Marte (CDM)", "activo": True},
    {"id": 9, "nombre": "Los Olivos (PRO)", "activo": True},
    {"id": 10, "nombre": "San Martín de Porres (SMP)", "activo": True},
    {"id": 99, "nombre": "Estación Inactiva Test", "activo": False}
]


class SimuladorBotTelegram:
    """Simula de forma determinista la lógica de n8n para el Bot de Telegram."""

    def __init__(self, estaciones: Optional[List[Dict[str, Any]]] = None):
        self.estaciones = {e["id"]: e for e in (estaciones or ESTACIONES_FIXTURE)}
        # Tabla en memoria: suscriptores_telegram (chat_id, estacion_id) -> dict
        self.suscriptores: Dict[Tuple[int, int], Dict[str, Any]] = {}
        # Historial de notificaciones enviadas
        self.notificaciones_enviadas: List[Dict[str, Any]] = []

    def interpretar_comando(self, texto: str, chat_id: int) -> Dict[str, Any]:
        """Replica el nodo 'Interpretar comando' de Bot_telegram_comandos.json."""
        t = str(texto or "").strip()
        partes = re.split(r"\s+", t)
        validos = ["/start", "/estaciones", "/suscribir", "/baja"]
        cmd = (partes[0] if partes else "").lower().split("@")[0]
        comando = cmd if cmd in validos else "/otro"
        arg = partes[1] if len(partes) > 1 else ""
        estacion_id = int(arg) if re.match(r"^\d{1,9}$", arg) else 0
        return {"chat_id": chat_id, "comando": comando, "estacion_id": estacion_id}

    def procesar_mensaje(self, chat_id: int, texto_mensaje: str) -> Dict[str, Any]:
        """Procesa un mensaje entrante y retorna la respuesta emitida al usuario."""
        c = self.interpretar_comando(texto_mensaje, chat_id)
        cmd = c["comando"]
        est_id = c["estacion_id"]

        # Estaciones activas ordenadas por nombre
        est_activas = sorted(
            [e for e in self.estaciones.values() if e.get("activo", True)],
            key=lambda x: x["nombre"]
        )
        lista_str = "\n".join(f"{e['id']} · {e['nombre']}" for e in est_activas)

        if cmd == "/start":
            respuesta = (
                "Hola 👋 Soy el bot de alertas de calidad del aire de EcoPredict.\n\n"
                "Comandos:\n"
                "/estaciones – ver las estaciones y su número\n"
                "/suscribir N – recibir alertas de la estación N\n"
                "/baja N – dejar de recibirlas\n\n"
                "Ejemplo: /suscribir 10"
            )
            return {"chat_id": chat_id, "texto": respuesta, "accion": "start"}

        elif cmd == "/estaciones":
            respuesta = (
                "Estaciones disponibles (número · nombre):\n\n"
                + (lista_str if lista_str else "No hay estaciones.")
                + "\n\nPara suscribirte: /suscribir N"
            )
            return {"chat_id": chat_id, "texto": respuesta, "accion": "estaciones"}

        elif cmd == "/suscribir":
            if not est_id:
                respuesta = "Indica el número de la estación. Ejemplo: /suscribir 10\nVer los números: /estaciones"
                return {"chat_id": chat_id, "texto": respuesta, "accion": "error_arg"}

            est = self.estaciones.get(est_id)
            if not est or not est.get("activo", True):
                respuesta = f"No existe la estación {est_id}. Mira la lista con /estaciones"
                return {"chat_id": chat_id, "texto": respuesta, "accion": "estacion_no_encontrada"}

            # Ejecutar alta o reactivación (ON CONFLICT DO UPDATE SET activo = true)
            clave = (chat_id, est_id)
            self.suscriptores[clave] = {
                "chat_id": chat_id,
                "estacion_id": est_id,
                "activo": True,
                "fecha_alta": datetime.now(timezone.utc).isoformat()
            }
            respuesta = f"✅ Listo. Recibirás alertas de {est['nombre']}.\nPara dejar de recibirlas: /baja {est_id}"
            return {"chat_id": chat_id, "texto": respuesta, "accion": "suscripcion_exitosa"}

        elif cmd == "/baja":
            if not est_id:
                respuesta = "Indica el número de la estación. Ejemplo: /baja 10"
                return {"chat_id": chat_id, "texto": respuesta, "accion": "error_arg"}

            clave = (chat_id, est_id)
            sub = self.suscriptores.get(clave)
            if not sub or not sub.get("activo", False):
                respuesta = f"No estabas suscrito a la estación {est_id}."
                return {"chat_id": chat_id, "texto": respuesta, "accion": "no_suscrito"}

            sub["activo"] = False
            est_nom = self.estaciones.get(est_id, {}).get("nombre", f"Estación {est_id}")
            respuesta = f"Listo. Ya no recibirás alertas de {est_nom}."
            return {"chat_id": chat_id, "texto": respuesta, "accion": "baja_exitosa"}

        else:
            respuesta = "No entendí ese comando. Usa /estaciones, /suscribir N o /baja N."
            return {"chat_id": chat_id, "texto": respuesta, "accion": "comando_desconocido"}

    def armar_mensaje_alerta(self, alerta: Dict[str, Any]) -> str:
        """Replica el nodo 'Armar mensaje' de Notificar_telegram.json."""
        estacion = alerta.get("estacion", "Estación Desconocida")
        parametro = str(alerta.get("parametro", "")).upper()
        valor = alerta.get("valor_registrado", 0.0)
        severidad = alerta.get("severidad", "moderada")
        analisis_raw = alerta.get("analisis_llm") or "Sin análisis disponible."
        analisis = str(analisis_raw)[:3500]
        est_id = alerta.get("estacion_id", 0)

        mensaje = (
            f"⚠️ Alerta de calidad del aire · {estacion}\n"
            f"{parametro}: {valor} (severidad {severidad})\n\n"
            f"{analisis}\n\n"
            f"Para dejar de recibir alertas de esta estación: /baja {est_id}"
        )
        return mensaje

    def despachar_alerta_a_suscriptores(self, alerta: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Replica el nodo 'Buscar suscriptores' y 'Enviar a Telegram':
        Filtra únicamente suscriptores activos para la estación afectada.
        """
        est_id = alerta.get("estacion_id")
        suscriptores_destino = [
            s for (c_id, e_id), s in self.suscriptores.items()
            if e_id == est_id and s.get("activo", False)
        ]

        envios = []
        for s in suscriptores_destino:
            msg = self.armar_mensaje_alerta(alerta)
            registro = {
                "chat_id": s["chat_id"],
                "estacion_id": est_id,
                "alerta_id": alerta.get("id"),
                "parametro": alerta.get("parametro"),
                "mensaje": msg,
                "estado": "enviado",
                "enviado_en": datetime.now(timezone.utc).isoformat()
            }
            self.notificaciones_enviadas.append(registro)
            envios.append(registro)

        return envios


# =============================================================================
# FIXTURES DE PYTEST
# =============================================================================
@pytest.fixture
def bot():
    """Retorna una instancia limpia del simulador del bot de Telegram."""
    return SimuladorBotTelegram()


@pytest.fixture
def alerta_campo_de_marte():
    """Fixture con una anomalía detectada en Campo de Marte (ID 8) con analisis_llm."""
    return {
        "id": 101,
        "estacion_id": 8,
        "estacion": "Campo de Marte (CDM)",
        "parametro": "pm25",
        "valor_registrado": 78.5,
        "severidad": "critica",
        "analisis_llm": (
            "Se detectó un pico anómalo de PM2.5 de 78.5 µg/m³ superando el estándar "
            "ECA de 25 µg/m³. Se recomienda a personas con asma y adultos mayores "
            "evitar realizar ejercicios al aire libre."
        )
    }


# =============================================================================
# 1. PRUEBAS DE COMANDOS DEL BOT (/start, /estaciones, /suscribir, /baja)
# =============================================================================
class TestComandosBotTelegram:
    """Verifica el ciclo de vida de los comandos del bot conforme al nodo de n8n."""

    def test_comando_start_bienvenida_y_menu(self, bot):
        """Verifica que /start devuelva la bienvenida y el listado de comandos."""
        res = bot.procesar_mensaje(chat_id=123456789, texto_mensaje="/start")
        assert res["accion"] == "start"
        assert "Hola 👋" in res["texto"]
        assert "/estaciones" in res["texto"]
        assert "/suscribir" in res["texto"]
        assert "/baja" in res["texto"]

    def test_comando_estaciones_lista_ordenada_y_activas(self, bot):
        """Verifica que /estaciones liste las estaciones oficiales y omita inactivas."""
        res = bot.procesar_mensaje(chat_id=123456789, texto_mensaje="/estaciones")
        assert res["accion"] == "estaciones"
        assert "Estaciones disponibles" in res["texto"]
        assert "8 · Campo de Marte (CDM)" in res["texto"]
        assert "1 · San Borja (SBJ)" in res["texto"]
        # La estación 99 está inactiva y no debe figurar
        assert "Estación Inactiva Test" not in res["texto"]

    def test_comando_suscribir_exitoso(self, bot):
        """Verifica suscripción exitosa a una estación existente (/suscribir 8)."""
        res = bot.procesar_mensaje(chat_id=123456789, texto_mensaje="/suscribir 8")
        assert res["accion"] == "suscripcion_exitosa"
        assert "✅ Listo" in res["texto"]
        assert "Campo de Marte (CDM)" in res["texto"]
        assert "/baja 8" in res["texto"]

        # Verificar persistencia en tabla suscriptores_telegram
        sub = bot.suscriptores.get((123456789, 8))
        assert sub is not None
        assert sub["activo"] is True

    def test_comando_suscribir_sin_numero_muestra_guia(self, bot):
        """Verifica que /suscribir sin parámetro numérico guíe al usuario."""
        res = bot.procesar_mensaje(chat_id=123456789, texto_mensaje="/suscribir")
        assert res["accion"] == "error_arg"
        assert "Indica el número de la estación" in res["texto"]

    def test_comando_suscribir_estacion_inexistente(self, bot):
        """Verifica rechazo al intentar suscribirse a un ID fuera de catálogo."""
        res = bot.procesar_mensaje(chat_id=123456789, texto_mensaje="/suscribir 999")
        assert res["accion"] == "estacion_no_encontrada"
        assert "No existe la estación 999" in res["texto"]

    def test_comando_baja_exitosa(self, bot):
        """Verifica desuscripción lógica (/baja 8) desactivando la suscripción."""
        # 1. Suscribirse primero
        bot.procesar_mensaje(chat_id=123456789, texto_mensaje="/suscribir 8")
        # 2. Solicitar baja
        res = bot.procesar_mensaje(chat_id=123456789, texto_mensaje="/baja 8")
        assert res["accion"] == "baja_exitosa"
        assert "Ya no recibirás alertas de Campo de Marte" in res["texto"]

        # Verificar estado inactivo
        sub = bot.suscriptores.get((123456789, 8))
        assert sub["activo"] is False

    def test_comando_baja_sin_suscripcion_previa(self, bot):
        """Verifica mensaje adecuado cuando el usuario pide baja de una estación a la que no está suscrito."""
        res = bot.procesar_mensaje(chat_id=999999, texto_mensaje="/baja 3")
        assert res["accion"] == "no_suscrito"
        assert "No estabas suscrito a la estación 3" in res["texto"]

    def test_reactivacion_tras_baja_idempotente(self, bot):
        """Verifica que volver a suscribirse tras una baja reactive la suscripción sin duplicar registros."""
        chat_id = 456789
        bot.procesar_mensaje(chat_id, "/suscribir 1")
        bot.procesar_mensaje(chat_id, "/baja 1")
        assert bot.suscriptores[(chat_id, 1)]["activo"] is False

        # Reactivación
        res = bot.procesar_mensaje(chat_id, "/suscribir 1")
        assert res["accion"] == "suscripcion_exitosa"
        assert bot.suscriptores[(chat_id, 1)]["activo"] is True
        # Debe mantenerse una sola entrada en el diccionario por la unicidad (chat_id, estacion_id)
        assert len([k for k in bot.suscriptores.keys() if k == (chat_id, 1)]) == 1

    def test_comando_desconocido_muestra_ayuda(self, bot):
        """Verifica que mensajes o comandos inválidos (/clima, etc.) devuelvan texto de ayuda."""
        res = bot.procesar_mensaje(chat_id=123456789, texto_mensaje="/clima_hoy")
        assert res["accion"] == "comando_desconocido"
        assert "No entendí ese comando" in res["texto"]


# =============================================================================
# 2. PRUEBAS DE FILTRADO POR ZONA Y AISLAMIENTO DE CIUDADANOS
# =============================================================================
class TestFiltradoPorEstacionYAislamiento:
    """Verifica que las alertas solo se envíen a los suscriptores de la estación afectada."""

    def test_solo_suscriptores_de_estacion_afectada_reciben_alerta(self, bot, alerta_campo_de_marte):
        """
        Escenario:
        - Ciudadano A suscrito a Estación 8 (Campo de Marte).
        - Ciudadano B suscrito a Estación 1 (San Borja).
        - Ciudadano C suscrito a Estación 8 pero en estado inactivo (dio /baja).
        Ocurre alerta en Estación 8: Solo el Ciudadano A debe recibir el mensaje.
        """
        # Configurar suscriptores
        bot.procesar_mensaje(chat_id=1001, texto_mensaje="/suscribir 8")  # Ciudadano A
        bot.procesar_mensaje(chat_id=1002, texto_mensaje="/suscribir 1")  # Ciudadano B
        bot.procesar_mensaje(chat_id=1003, texto_mensaje="/suscribir 8")  # Ciudadano C
        bot.procesar_mensaje(chat_id=1003, texto_mensaje="/baja 8")       # Ciudadano C se dio de baja

        envios = bot.despachar_alerta_a_suscriptores(alerta_campo_de_marte)

        # Solo debe haber 1 envío (para Ciudadano A)
        assert len(envios) == 1
        assert envios[0]["chat_id"] == 1001
        assert envios[0]["estacion_id"] == 8

        chats_notificados = [e["chat_id"] for e in envios]
        assert 1002 not in chats_notificados  # Ciudadano B excluido
        assert 1003 not in chats_notificados  # Ciudadano C excluido por inactivo

    def test_ciudadano_con_multiples_suscripciones(self, bot):
        """Verifica que un ciudadano suscrito a varias estaciones reciba la alerta correspondiente a cada una."""
        chat_id = 777777
        bot.procesar_mensaje(chat_id, "/suscribir 1")  # San Borja
        bot.procesar_mensaje(chat_id, "/suscribir 8")  # Campo de Marte

        # Alerta en San Borja (ID 1)
        alerta_sbj = {
            "id": 201,
            "estacion_id": 1,
            "estacion": "San Borja (SBJ)",
            "parametro": "so2",
            "valor_registrado": 35.0,
            "severidad": "alta",
            "analisis_llm": "Pico de SO2 por tráfico vehicular."
        }
        envios = bot.despachar_alerta_a_suscriptores(alerta_sbj)
        assert len(envios) == 1
        assert envios[0]["chat_id"] == chat_id
        assert "San Borja" in envios[0]["mensaje"]


# =============================================================================
# 3. PRUEBAS DE ESTRUCTURA DEL MENSAJE Y ANÁLISIS IA (analisis_llm)
# =============================================================================
class TestEstructuraMensajeYAnalisisIA:
    """Verifica que el mensaje enviado contenga analisis_llm y cumpla los límites de Telegram."""

    def test_mensaje_incluye_analisis_llm_obligatorio(self, bot, alerta_campo_de_marte):
        """Verifica que el cuerpo del mensaje incluya el análisis redactado por la IA."""
        msg = bot.armar_mensaje_alerta(alerta_campo_de_marte)

        assert "⚠️ Alerta de calidad del aire · Campo de Marte (CDM)" in msg
        assert "PM25: 78.5 (severidad critica)" in msg
        assert "Se detectó un pico anómalo de PM2.5" in msg
        assert "Para dejar de recibir alertas de esta estación: /baja 8" in msg

    def test_analisis_llm_trunca_a_3500_caracteres_limite_telegram(self, bot):
        """
        Telegram tiene un límite máximo de 4096 caracteres por mensaje.
        El workflow trunca el analisis_llm a 3500 chars para evitar error 400 Bad Request.
        """
        analisis_enorme = "A" * 5000
        alerta = {
            "id": 301,
            "estacion_id": 2,
            "estacion": "Carabayllo",
            "parametro": "pm10",
            "valor_registrado": 120.0,
            "severidad": "alta",
            "analisis_llm": analisis_enorme
        }
        msg = bot.armar_mensaje_alerta(alerta)
        # El mensaje total debe ser menor al límite de Telegram (4096)
        assert len(msg) < 4000
        # El análisis inyectado no debe superar 3500 chars
        assert "A" * 3501 not in msg

    def test_analisis_llm_nulo_o_vacio_usa_fallback_seguro(self, bot):
        """Verifica que si el análisis de IA es nulo o vacío, se use un texto seguro sin romper la ejecución."""
        alerta_sin_ia = {
            "id": 302,
            "estacion_id": 3,
            "estacion": "Huachipa",
            "parametro": "no2",
            "valor_registrado": 85.0,
            "severidad": "moderada",
            "analisis_llm": None
        }
        msg = bot.armar_mensaje_alerta(alerta_sin_ia)
        assert "Sin análisis disponible." in msg
        assert "/baja 3" in msg
