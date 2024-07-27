-- Step 1: Create an enum with 3 states (QUEUED, PRINTING, FINISHED) if it does not exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_enum') THEN
        CREATE TYPE status_enum AS ENUM ('QUEUED', 'PRINTING', 'FINISHED');
    END IF;
END $$;

-- Step 2: Create a table called Queue with the specified columns if it does not exist
CREATE TABLE IF NOT EXISTS Queue (
    timestamp TIMESTAMPTZ PRIMARY KEY DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(255),
    message TEXT,
    status status_enum DEFAULT 'QUEUED'
);

-- Step 3: Create a SQL function that takes a source and message and creates a new row in Queue if it does not exist
CREATE OR REPLACE FUNCTION add_to_queue(p_source VARCHAR, p_message TEXT) RETURNS VOID AS $$
BEGIN
    INSERT INTO Queue (source, message, status) VALUES (p_source, p_message, 'QUEUED');
END;
$$ LANGUAGE plpgsql;