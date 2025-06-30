import os
import sqlite3
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# ─── SETUP LOGGING ──────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)

# ─── CREATE DB IF NEEDED ────────────────────────────────────────────────────────
DB_PATH = "database.db"
SCHEMA_PATH = os.path.join("backend", "schema.sql")

if not os.path.exists(DB_PATH):
    logging.info("📁 Database file not found. Creating new database.")
    with sqlite3.connect(DB_PATH) as conn:
        with open(SCHEMA_PATH, "r") as f:
            conn.executescript(f.read())
    logging.info("✅ Database initialized from schema.sql.")

# ─── APP SETUP ───────────────────────────────────────────────────────────────────
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Consider locking this down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TESTING = os.getenv("TESTING") == "1"
if not TESTING:
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

# ─── ROUTES ──────────────────────────────────────────────────────────────────────

@app.get("/api/ping")
def ping():
    return {"message": "pong"}

@app.get("/api/reservations/{date}")
def get_reservations(date: str):
    conn = sqlite3.connect(DB_PATH)
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

    conn = sqlite3.connect(DB_PATH)
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

    return {"status": "seeded", "rows": len(test_data)}

@app.api_route("/api/health", methods=["GET", "HEAD"], include_in_schema=False)
def health_check():
    return {"status": "ok"}
