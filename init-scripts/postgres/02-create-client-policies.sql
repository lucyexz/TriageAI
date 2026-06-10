-- Tabela de políticas por cliente (governança)
-- Criada no banco 'mlops' pelo init script do Postgres

\c mlops;

CREATE TABLE IF NOT EXISTS client_policies (
    client_id       VARCHAR(100) PRIMARY KEY,
    temperature     FLOAT        NOT NULL DEFAULT 0.7,
    system_prompt_override TEXT,
    guardrails      TEXT,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP    NOT NULL DEFAULT NOW()
);

INSERT INTO client_policies (client_id, temperature, system_prompt_override, guardrails)
VALUES
    ('anonymous',       0.7,  NULL, NULL),
    ('hospital-central',0.5,  NULL, 'Resposta deve ser objetiva e técnica.'),
    ('upa-norte',       0.8,  NULL, 'Priorizar casos pediátricos.')
ON CONFLICT (client_id) DO NOTHING;
