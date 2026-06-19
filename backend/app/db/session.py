import sqlite3
import os

def get_db_path():
    """Returns the database path. Uses a test database if in testing environment."""
    if os.getenv("TESTING") == "1":
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test_roadmap.db")
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "roadmap.db")

def get_db_connection():
    """Returns a SQLite connection with row factory enabled and tables auto-initialized."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    
    # Auto-initialize the table if it doesn't exist
    conn.execute("""
        CREATE TABLE IF NOT EXISTS roadmaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal TEXT NOT NULL,
            current_level TEXT NOT NULL,
            hours_per_week INTEGER NOT NULL,
            scores TEXT NOT NULL,
            explanation TEXT NOT NULL,
            roadmap TEXT NOT NULL,
            source TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def init_db():
    """Initializes the SQLite database. Auto-called by get_db_connection."""
    conn = get_db_connection()
    conn.close()

