import sqlite3
import os

DB_PATH = "database.db"
SCHEMA_PATH = "backend/schema.sql"

def init_db():
    if not os.path.exists(DB_PATH):
        print("🛠️ Creating new database from schema.sql...")
        with sqlite3.connect(DB_PATH) as conn:
            with open(SCHEMA_PATH, "r") as f:
                conn.executescript(f.read())
        print("✅ Database initialized.")
    else:
        print("✅ Database already exists. Skipping init.")

if __name__ == "__main__":
    init_db()
