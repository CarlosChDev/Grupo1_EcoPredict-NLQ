
CREATE DATABASE calidad_aire;

\connect calidad_aire

-- =============================================================================
-- ESQUEMA V2: EcoPredict & NLQ (PostgreSQL)
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -----------------------------------------------------------------------------
-- 1. CATÁLOGOS Y UBICACIONES (OpenAQ + SENAMHI)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS estaciones (
    id SERIAL PRIMARY KEY,
    codigo_externo VARCHAR(50) NOT NULL, -- location_id de OpenAQ o código SENAMHI
    nombre VARCHAR(150) NOT NULL,        -- ej. "CAMPO DE MARTE"
    tipo VARCHAR(50) NOT NULL,           -- 'calidad_aire', 'meteorologica', 'mixta'
    zona VARCHAR(50),                    -- 'industrial', 'residencial', 'urbana'
    latitud DOUBLE PRECISION NOT NULL,
    longitud DOUBLE PRECISION NOT NULL,
    pais_iso VARCHAR(5) DEFAULT 'PE',
    timezone VARCHAR(50) DEFAULT 'America/Lima',
    proveedor VARCHAR(100) DEFAULT 'SENAMHI',
    es_movil BOOLEAN DEFAULT FALSE,
    es_monitor BOOLEAN DEFAULT TRUE,
    activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_estaciones_codigo_prov UNIQUE (codigo_externo, proveedor)
);

CREATE INDEX idx_estaciones_zona ON estaciones(zona);
CREATE INDEX idx_estaciones_coords ON estaciones(latitud, longitud);

-- -----------------------------------------------------------------------------
-- 2. MEDICIONES DE CALIDAD DEL AIRE (OpenAQ / Senamhi horario)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mediciones_aire (
    id BIGSERIAL PRIMARY KEY,
    estacion_id INT NOT NULL REFERENCES estaciones(id) ON DELETE CASCADE,
    parametro VARCHAR(20) NOT NULL,     -- 'pm25', 'pm10', 'co', 'no2', 'so2', 'o3'
    valor DOUBLE PRECISION,             -- NULL si vino -99.9 o dato inválido
    unidad VARCHAR(20) NOT NULL,        -- 'µg/m³', 'ppm'
    medido_en TIMESTAMPTZ NOT NULL,     -- datetimeUtc / datetimeLocal normalizado
    ingerido_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    payload_crudo JSONB,
    CONSTRAINT uq_medicion_aire_evento UNIQUE (estacion_id, parametro, medido_en)
);

CREATE INDEX idx_mediciones_aire_busqueda ON mediciones_aire(estacion_id, parametro, medido_en DESC);
CREATE INDEX idx_mediciones_aire_fecha ON mediciones_aire(medido_en DESC);

-- -----------------------------------------------------------------------------
-- 3. DATOS METEOROLÓGICOS (SENAMHI diario / horario)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mediciones_meteorologicas (
    id BIGSERIAL PRIMARY KEY,
    estacion_id INT NOT NULL REFERENCES estaciones(id) ON DELETE CASCADE,
    fecha DATE NOT NULL,
    precipitacion_acum DOUBLE PRECISION,  -- mm (NULL si fue -99.9)
    temperatura_max DOUBLE PRECISION,     -- °C (NULL si fue -99.9)
    temperatura_min DOUBLE PRECISION,     -- °C (NULL si fue -99.9)
    humedad_relativa DOUBLE PRECISION,
    velocidad_viento DOUBLE PRECISION,
    ingerido_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    payload_crudo JSONB,
    CONSTRAINT uq_medicion_meteo_fecha UNIQUE (estacion_id, fecha)
);

CREATE INDEX idx_mediciones_meteo_busqueda ON mediciones_meteorologicas(estacion_id, fecha DESC);

-- -----------------------------------------------------------------------------
-- 4. DETECCIÓN DE ANOMALÍAS (Flujo A: ETL + LLM/Regla)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS alertas_anomalias (
    id BIGSERIAL PRIMARY KEY,
    estacion_id INT NOT NULL REFERENCES estaciones(id) ON DELETE CASCADE,
    parametro VARCHAR(20) NOT NULL,
    valor_registrado DOUBLE PRECISION NOT NULL,
    umbral_base DOUBLE PRECISION,       -- Límite OMS/ECA o media móvil
    desviacion DOUBLE PRECISION,        -- Grado de desviación / Z-Score
    severidad VARCHAR(20) NOT NULL,     -- 'baja', 'moderada', 'alta', 'critica'
    analisis_llm TEXT,                  -- Explicación del LLM sobre factores
    notificado_telegram BOOLEAN DEFAULT FALSE,
    notificado_correo BOOLEAN DEFAULT FALSE,
    detectado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_alertas_severidad ON alertas_anomalias(severidad, detectado_en DESC);

-- -----------------------------------------------------------------------------
-- 5. CACHÉ Y LOGS DE CONSULTAS NLQ (Flujo B)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS logs_consultas_nlq (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    consulta_usuario TEXT NOT NULL,
    hash_consulta VARCHAR(64) NOT NULL,  -- SHA-256 de consulta normalizada
    filtros_extraidos JSONB,             -- Intención estructurada (zona, fecha, parámetro)
    sql_generado TEXT,
    respuesta_texto TEXT NOT NULL,
    config_grafico JSONB,                -- Schema de Chart.js / Recharts
    tiempo_respuesta_ms INT,
    hit_cache BOOLEAN DEFAULT FALSE,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_nlq_hash ON logs_consultas_nlq(hash_consulta);
CREATE INDEX idx_nlq_fecha ON logs_consultas_nlq(creado_en DESC);

-- -----------------------------------------------------------------------------
-- 6. OBSERVABILIDAD, LLMOps & CONTROL DE ERRORES
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS logs_ejecucion_ia (
    id BIGSERIAL PRIMARY KEY,
    workflow_tipo VARCHAR(50) NOT NULL,  -- 'ETL_ANOMALIAS', 'NLQ_QUERY'
    trace_id VARCHAR(100),               -- ID de traza de LangSmith / n8n Run ID
    modelo_utilizado VARCHAR(50) NOT NULL,
    prompt_tokens INT DEFAULT 0,
    completion_tokens INT DEFAULT 0,
    costo_estimado_usd NUMERIC(10, 6) DEFAULT 0.0,
    hubo_fallback BOOLEAN DEFAULT FALSE, -- Si falló modelo primario y usó respaldo
    hubo_error BOOLEAN DEFAULT FALSE,
    mensaje_error TEXT,
    duracion_ms INT,
    ejecutado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_llmops_workflow ON logs_ejecucion_ia(workflow_tipo, ejecutado_en DESC);
CREATE INDEX idx_llmops_error ON logs_ejecucion_ia(hubo_error);

CREATE TABLE IF NOT EXISTS ingesta_estado (
    fuente           VARCHAR(50) PRIMARY KEY,
    ultimo_medido_en TIMESTAMPTZ NOT NULL,
    ultima_ejecucion TIMESTAMPTZ NOT NULL DEFAULT now(),
    filas_insertadas INT
);
CREATE TABLE IF NOT EXISTS alerta_estado (
    estacion_id   INT REFERENCES estaciones(id) ON DELETE CASCADE,
    parametro     VARCHAR(20),
    severidad     VARCHAR(20) NOT NULL,
    desde         TIMESTAMPTZ NOT NULL,
    ultima_alerta TIMESTAMPTZ,
    PRIMARY KEY (estacion_id, parametro)
);

CREATE TABLE IF NOT EXISTS rate_limit ( 
    ip TEXT PRIMARY KEY, 
    conteo INT NOT NULL DEFAULT 1, 
    ventana_inicio TIMESTAMPTZ NOT NULL DEFAULT now() 
); 

CREATE TABLE IF NOT EXISTS mediciones_referencia_qa ( 
    id BIGSERIAL PRIMARY KEY, 
    estacion TEXT NOT NULL, 
    parametro TEXT NOT NULL, 
    valor DOUBLE PRECISION, 
    medido_en TIMESTAMPTZ NOT NULL, 
    fecha_captura TIMESTAMPTZ NOT NULL DEFAULT now(), 
    fuente TEXT NOT NULL DEFAULT 'SENAMHI' 
); 