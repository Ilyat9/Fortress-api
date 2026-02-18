-- Initialize Todo Database
-- ======================

-- Enable UUID extension if needed (optional)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create todos table
CREATE TABLE IF NOT EXISTS todos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(1000),
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_todos_created_at ON todos(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_todos_is_completed ON todos(is_completed);
CREATE INDEX IF NOT EXISTS idx_todos_priority ON todos(priority);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to todos table
CREATE TRIGGER update_todos_updated_at
    BEFORE UPDATE ON todos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data if table is empty
INSERT INTO todos (title, description, is_completed, priority)
SELECT
    'Welcome to Todo API',
    'This is a sample todo. Feel free to add, update, or delete todos through the API.',
    FALSE,
    'medium'
WHERE NOT EXISTS (SELECT 1 FROM todos LIMIT 1);

-- Grant permissions (adjust as needed for production)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO todo_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO todo_user;

-- Set default search path
SET search_path TO public, pg_catalog;
