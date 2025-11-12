"""
SQLite database schema for re:invent sessions.

This module defines the database schema including table creation
and trigger setup for automatic timestamp management.
"""

# Sessions table schema with all required columns
CREATE_SESSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    short_id TEXT,
    title TEXT NOT NULL,
    abstract TEXT,
    session_type TEXT,
    venue_name TEXT,
    venue_room TEXT,
    start_datetime TEXT,
    end_datetime TEXT,
    day TEXT,
    speakers_json TEXT,
    topics_json TEXT,
    areas_of_interest_json TEXT,
    level TEXT,
    level_value INTEGER,
    features_json TEXT,
    seat_capacity INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

# Trigger to automatically update the updated_at timestamp
CREATE_UPDATED_AT_TRIGGER = """
CREATE TRIGGER IF NOT EXISTS update_sessions_timestamp 
AFTER UPDATE ON sessions
FOR EACH ROW
BEGIN
    UPDATE sessions 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE session_id = NEW.session_id;
END
"""

# List of all schema creation statements in order
SCHEMA_STATEMENTS = [
    CREATE_SESSIONS_TABLE,
    CREATE_UPDATED_AT_TRIGGER
]


def initialize_database(connection):
    """
    Initialize the database schema by executing all schema statements.
    
    Args:
        connection: SQLite database connection object
        
    Returns:
        None
        
    Raises:
        sqlite3.Error: If schema creation fails
    """
    cursor = connection.cursor()
    
    for statement in SCHEMA_STATEMENTS:
        cursor.execute(statement)
    
    connection.commit()
    cursor.close()
