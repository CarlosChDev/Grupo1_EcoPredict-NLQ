-- ============================================================================
-- 003_hu02_pgvector_rag.sql
-- HU-02 (RAG) · Tarea 2: habilitar pgvector y preparar el esquema vectorial
--
-- Requiere una imagen de PostgreSQL con la extensión pgvector instalada
-- (p. ej. pgvector/pgvector:pg16-bookworm). En la imagen postgres:16-alpine
-- actual, CREATE EXTENSION vector falla.
--
-- Dimensión fija: 768 (gemini-embedding-001 con outputDimensionality = 768).
-- Los vectores de 3072 dimensiones (valor por defecto) NO admiten índice
-- HNSW sobre el tipo vector (límite de 2000 dimensiones).
--
-- Idempotente: se puede ejecutar más de una vez.
-- Como 001, empieza con \connect: los scripts de /docker-entrypoint-initdb.d
-- se ejecutan contra la base "postgres" y 001 crea calidad_aire.
-- ============================================================================
\connect calidad_aire

CREATE EXTENSION IF NOT EXISTS vector;

-- ----------------------------------------------------------------------------
-- A) Embeddings sobre el historial de consultas (criterio de aceptación HU-02)
--    Sirve para: consultas parecidas, caché semántica y análisis de fallos.
-- ----------------------------------------------------------------------------
ALTER TABLE logs_consultas_nlq
    ADD COLUMN IF NOT EXISTS embedding vector(768);

CREATE INDEX IF NOT EXISTS idx_logs_consultas_nlq_embedding
    ON logs_consultas_nlq USING hnsw (embedding vector_cosine_ops);

-- ----------------------------------------------------------------------------
-- B) Base de conocimiento del RAG: catálogo de estaciones + normativa y salud
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS documentos_rag (
    id               BIGSERIAL PRIMARY KEY,
    tipo             TEXT        NOT NULL CHECK (tipo IN ('estacion', 'zona', 'norma', 'salud')),
    fuente           TEXT        NOT NULL,            -- nombre de la norma o guía
    referencia       TEXT,                            -- artículo, tabla o página
    parametro        TEXT,                            -- PM2.5, PM10, NO2, O3, CO, SO2...
    contenido        TEXT        NOT NULL,            -- texto literal que se recupera
    metadata         JSONB       NOT NULL DEFAULT '{}'::jsonb,  -- tipo zona: {"zona": "<distrito>"}
    estacion_id      INT         REFERENCES estaciones(id) ON DELETE CASCADE,  -- solo tipo estacion
    verificado       BOOLEAN     NOT NULL DEFAULT false,   -- comparado con el original
    embedding        vector(768),
    embedding_modelo TEXT,                            -- p. ej. gemini-embedding-001
    creado_en        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_documentos_rag_tipo_parametro
    ON documentos_rag (tipo, parametro);

CREATE INDEX IF NOT EXISTS idx_documentos_rag_estacion
    ON documentos_rag (estacion_id) WHERE estacion_id IS NOT NULL;

-- Con pocas filas el índice HNSW no acelera nada (el recorrido exacto ya es
-- instantáneo); se crea para dejar el esquema listo si la base crece.
CREATE INDEX IF NOT EXISTS idx_documentos_rag_embedding
    ON documentos_rag USING hnsw (embedding vector_cosine_ops);

-- ----------------------------------------------------------------------------
-- C) Permisos: el Flujo B consulta con el rol de solo lectura nlq_reader.
--    El LLM nunca genera SQL; este rol solo lee.
-- ----------------------------------------------------------------------------
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'nlq_reader') THEN
        EXECUTE 'GRANT SELECT ON documentos_rag TO nlq_reader';
    END IF;
END
$$;
