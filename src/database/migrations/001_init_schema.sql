-- Sprint 0 · Esquema inicial mínimo
-- El esquema definitivo se definirá en el Sprint 1, tras mapear las APIs reales.

CREATE DATABASE calidad_aire;

\connect calidad_aire

CREATE TABLE IF NOT EXISTS mediciones (
    id          BIGSERIAL PRIMARY KEY,
    fuente      TEXT NOT NULL,
    parametro   TEXT NOT NULL,
    valor       DOUBLE PRECISION,
    medido_en   TIMESTAMPTZ NOT NULL,
    ingerido_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    payload_crudo JSONB
);

INSERT INTO mediciones (fuente, parametro, valor, medido_en)
VALUES ('seed', 'pm25', 42.0, now());