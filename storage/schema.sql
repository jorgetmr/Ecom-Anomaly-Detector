CREATE TABLE IF NOT EXISTS events(
    ts TIMESTAMPTZ NOT NULL, 
    stream TEXT NOT NULL, 
    key TEXT NOT NULL, 
    value DOUBLE PRECISION NOT NULL, 
    tags JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS anomalies(
    ts TIMESTAMPTZ NOT NULL, 
    stream TEXT NOT NULL, 
    key TEXT NOT NULL, 
    score DOUBLE PRECISION NOT NULL, 
    severity TEXT NOT NULL, 
    method TEXT NOT NULL, 
    win TEXT, 
    details JSONB
);

SELECT create_hypertable('events', 'ts', if_not_exists => TRUE);
SELECT create_hypertable('anomalies', 'ts', if_not_exists => TRUE);