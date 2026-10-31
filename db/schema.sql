-- DARK STICKMAN STUDIO — Schema SQLite
-- ai_generated: True
-- ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB

CREATE TABLE IF NOT EXISTS jobs (
    job_id          TEXT PRIMARY KEY,
    titulo          TEXT NOT NULL,
    canal           TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'pendente',
    -- status: pendente | processando | concluido | erro | cancelado
    qualidade       TEXT NOT NULL DEFAULT 'medium_quality',
    formato         TEXT NOT NULL DEFAULT '16:9',
    criado_em       TEXT NOT NULL,
    atualizado_em   TEXT NOT NULL,
    duracao_s       REAL,
    output_path     TEXT,
    thumbnail_path  TEXT,
    shorts_path     TEXT,
    erro            TEXT,
    ai_generated    INTEGER NOT NULL DEFAULT 1,
    ai_disclosure   TEXT NOT NULL DEFAULT 'Produzido com DARK STUDIO AAA — DARK CREATIVE LAB'
);

CREATE INDEX IF NOT EXISTS idx_jobs_canal    ON jobs(canal);
CREATE INDEX IF NOT EXISTS idx_jobs_status   ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_criado   ON jobs(criado_em);
