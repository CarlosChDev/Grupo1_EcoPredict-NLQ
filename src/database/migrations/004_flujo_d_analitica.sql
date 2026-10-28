-- ============================================================================
-- 004_flujo_d_analitica.sql
-- Flujo D (Sprint 4) · tablas de analítica histórica por distrito
--
-- analitica_diaria  : agregado diario por distrito y parámetro (PM2.5, PM10).
--                     Lo llena el cron de las 06:30 del Flujo D; la clave
--                     primaria evita duplicados si el cron se repite (UPSERT).
-- analitica_insights: resumen semanal redactado por la IA, uno por distrito.
--
-- Los endpoints del Flujo D leen con el rol nlq_reader (solo lectura).
-- El cron escribe con la credencial que ya usa el Flujo A.
--
-- Idempotente: se puede ejecutar más de una vez.
-- Como 001-003, empieza con \connect: se ejecuta con psql contra el servidor.
--
-- Aplicar (con respaldo previo):
--   docker exec -i aire_postgres psql -U <USUARIO> -v ON_ERROR_STOP=1 < 004_flujo_d_analitica.sql
-- ============================================================================
\connect calidad_aire

CREATE TABLE IF NOT EXISTS analitica_diaria (
    fecha          DATE             NOT NULL,   -- día calendario en hora de Lima
    distrito       VARCHAR(50)      NOT NULL,   -- estaciones.zona
    parametro      VARCHAR(20)      NOT NULL,   -- 'pm25' o 'pm10'
    promedio       DOUBLE PRECISION,            -- promedio del día (µg/m³)
    maximo         DOUBLE PRECISION,
    minimo         DOUBLE PRECISION,
    n_mediciones   INT              NOT NULL,
    n_estaciones   INT              NOT NULL,
    horas_con_dato SMALLINT         NOT NULL,   -- horas distintas con lectura
    limite_eca     DOUBLE PRECISION,            -- límite ECA 24 h aplicado
    excede_eca     BOOLEAN          NOT NULL DEFAULT false,
    calculado_en   TIMESTAMPTZ      NOT NULL DEFAULT now(),
    PRIMARY KEY (fecha, distrito, parametro)
);

CREATE INDEX IF NOT EXISTS idx_analitica_diaria_distrito
    ON analitica_diaria (distrito, parametro, fecha DESC);

CREATE TABLE IF NOT EXISTS analitica_insights (
    semana_inicio  DATE         NOT NULL,       -- lunes de la semana resumida
    distrito       VARCHAR(50)  NOT NULL,
    resumen        TEXT         NOT NULL,       -- texto generado por la IA
    modelo         VARCHAR(80),                 -- p. ej. groq:openai/gpt-oss-120b
    generado_en    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    PRIMARY KEY (semana_inicio, distrito)
);

-- Permisos: los endpoints consultan con el rol de solo lectura nlq_reader.
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'nlq_reader') THEN
        EXECUTE 'GRANT SELECT ON analitica_diaria, analitica_insights TO nlq_reader';
    END IF;
END
$$;

-- Si las tablas las crea un usuario distinto al que usa el Flujo A en n8n,
-- hay que dar escritura a esa credencial (reemplazar <USUARIO_N8N>):
--   GRANT INSERT, UPDATE, SELECT ON analitica_diaria, analitica_insights TO <USUARIO_N8N>;
