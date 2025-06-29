import os
import sqlite3
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# Determine if we are in test mode
TESTING = os.getenv("TESTING") == "1"

if not TESTING:
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

# ✅ Configure basic logging
logging.basicConfig(level=logging.DEBUG)

# ✅ Initialize the test database schema if in test mode
if TESTING:
    try:
        from init_db import init_db
        init_db()
        logging.debug("✅ Initialized database from schema.sql")
    except Exception as e:
        logging.error(f"❌ Failed to initialize test DB: {e}")

app = FastAPI()

# Enable CORS for all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Consider locking this down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── ROUTES ─────────────────────────────────────────────────────────────

@app.get("/api/ping")
def ping():
    return {"message": "pong"}

@app.get("/api/reservations/{date}")
def get_reservations(date: str):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT glider, time, name FROM reservations WHERE date = ?", (date,))
    rows = cursor.fetchall()
    conn.close()

    result = {f"{glider}-{time}": name for glider, time, name in rows}
    return JSONResponse(content=result)

@app.post("/api/test/seed")
async def seed_test_data(request: Request):
    if not TESTING:
        return JSONResponse(status_code=403, content={"error": "Test-only endpoint"})

    db_path = "database.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM reservations")

    test_data = [
        ("2025-07-01", "G1", "08:00", "Alice"),
        ("2025-07-01", "G2", "09:00", "Bob"),
        ("2025-07-01", "G3", "10:00", "Charlie"),
    ]
    cursor.executemany("INSERT INTO reservations (date, glider, time, name) VALUES (?, ?, ?, ?)", test_data)
    conn.commit()
    conn.close()

    return {
        "status": "seeded",
        "rows": len(test_data),
        "db_file": os.path.abspath(db_path),
    }

@app.api_route("/api/health", methods=["GET", "HEAD"], include_in_schema=False)
def health_check():
    return {"status": "ok"}
