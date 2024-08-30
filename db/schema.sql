-- Step 1: Create an enum with 3 states (QUEUED, PRINTING, FINISHED)
CREATE TYPE status_enum AS ENUM ('QUEUED', 'PRINTING', 'FINISHED');

-- Step 2: Create a table called Queue with the specified columns
CREATE TABLE IF NOT EXISTS Queue (
    timestamp TIMESTAMPTZ PRIMARY KEY DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(255),
    message TEXT,
    status status_enum DEFAULT 'QUEUED'
);

-- Step 3: Create a SQL function that takes a source and message and creates a new row in Queue
CREATE OR REPLACE FUNCTION add_to_queue(p_source VARCHAR, p_message TEXT) RETURNS VOID AS $$
BEGIN
    INSERT INTO Queue (source, message, status) VALUES (p_source, p_message, 'QUEUED');
END;
$$ LANGUAGE plpgsql;

-- Step 4: Create a function to notify when a new row is added
CREATE OR REPLACE FUNCTION notify_new_row() RETURNS trigger AS $$
BEGIN
    PERFORM pg_notify('new_queue_entry', NEW.timestamp::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Step 5: Create a trigger to call the notification function on row insert
CREATE TRIGGER notify_new_row_trigger
AFTER INSERT ON Queue
FOR EACH ROW
EXECUTE FUNCTION notify_new_row();