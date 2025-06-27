import os
import sqlite3

def init_db():
    # Always resolves path relative to this file's location
    base_dir = os.path.dirname(__file__)  # -> backend/
    schema_path = os.path.join(base_dir, "schema.sql")
    db_path = os.path.join(base_dir, "database.db")

    with sqlite3.connect(db_path) as conn:
        with open(schema_path, "r") as f:
            conn.executescript(f.read())

if __name__ == "__main__":
    init_db()
    print("✅ Database initialized.")
