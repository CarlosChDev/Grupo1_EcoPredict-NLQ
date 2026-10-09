-- =============================================================================
-- 002 · HU-01 Telegram: suscripción por estación
-- Para bases YA creadas con el esquema viejo (suscriptores_telegram con "zona").
-- En una base nueva, 001 ya deja todo en su estado final y este archivo no cambia nada.
-- Se puede ejecutar más de una vez.
-- =============================================================================
\connect calidad_aire

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS suscriptores_telegram (
    id          SERIAL PRIMARY KEY,
    chat_id     BIGINT NOT NULL,
    estacion_id INT NOT NULL REFERENCES estaciones(id) ON DELETE CASCADE,
    activo      BOOLEAN DEFAULT true,
    fecha_alta  TIMESTAMPTZ DEFAULT now(),
    UNIQUE (chat_id, estacion_id)
);

ALTER TABLE suscriptores_telegram
    ADD COLUMN IF NOT EXISTS estacion_id INT REFERENCES estaciones(id) ON DELETE CASCADE;

-- Las suscripciones por zona no se pueden convertir a estación: se descartan.
DELETE FROM suscriptores_telegram WHERE estacion_id IS NULL;

-- Al quitar la columna, PostgreSQL elimina también UNIQUE (chat_id, zona).
ALTER TABLE suscriptores_telegram DROP COLUMN IF EXISTS zona;
ALTER TABLE suscriptores_telegram ALTER COLUMN estacion_id SET NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_suscriptores_chat_estacion
    ON suscriptores_telegram (chat_id, estacion_id);

CREATE TABLE IF NOT EXISTS notificaciones_telegram (
    id            BIGSERIAL PRIMARY KEY,
    suscriptor_id INT    NOT NULL REFERENCES suscriptores_telegram(id) ON DELETE CASCADE,
    alerta_id     BIGINT NOT NULL REFERENCES alertas_anomalias(id) ON DELETE CASCADE,
    estacion_id   INT    NOT NULL REFERENCES estaciones(id) ON DELETE CASCADE,
    parametro     VARCHAR(20) NOT NULL,
    estado        VARCHAR(20) NOT NULL CHECK (estado IN ('enviado', 'fallido')),
    error         TEXT,
    enviado_en    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_notif_cooldown
    ON notificaciones_telegram (suscriptor_id, estacion_id, parametro, enviado_en DESC);

CREATE TABLE IF NOT EXISTS telegram_offset (
    id               SMALLINT PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    ultimo_update_id BIGINT NOT NULL DEFAULT 0,
    actualizado_en   TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO telegram_offset (id, ultimo_update_id) VALUES (1, 0) ON CONFLICT (id) DO NOTHING;
