import os
import sqlite3
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request as StarletteRequest

# ─── Configure logging ───────────────────────────────────────────────────────
logging.basicConfig(level=logging.DEBUG)

# ─── Constants ───────────────────────────────────────────────────────────────
TESTING = os.getenv("TESTING") == "1"
DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

# ─── Database setup ──────────────────────────────────────────────────────────
def create_db_if_missing():
    if not os.path.exists(DB_PATH):
        logging.info("📦 Creating database from schema...")
        with sqlite3.connect(DB_PATH) as conn:
            with open(SCHEMA_PATH, "r") as f:
                conn.executescript(f.read())
        logging.info("✅ Database created.")
    else:
        logging.info("✅ Database already exists.")

create_db_if_missing()

# ─── FastAPI App ─────────────────────────────────────────────────────────────
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Models ──────────────────────────────────────────────────────────────────
class GliderIn(BaseModel):
    name: str

# ─── Routes ──────────────────────────────────────────────────────────────────

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
    return JSONResponse({f"{glider}-{time}": name for glider, time, name in rows})

@app.get("/api/gliders")
def get_gliders():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM gliders")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

@app.post("/api/gliders")
def add_glider(glider: GliderIn):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO gliders (name) VALUES (?)", (glider.name,))
    conn.commit()
    conn.close()
    return {"status": "ok", "name": glider.name}

@app.delete("/api/gliders/{name}")
def delete_glider(name: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM gliders WHERE name = ?", (name,))
    conn.commit()
    conn.close()
    return {"status": "deleted", "name": name}

@app.post("/api/test/seed")
async def seed_test_data(request: Request):
    if not TESTING:
        return JSONResponse(status_code=403, content={"error": "Test-only endpoint"})

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM reservations")
    cursor.execute("DELETE FROM gliders")

    glider_names = ["G1", "G2", "G3", "G4"]
    cursor.executemany("INSERT INTO gliders (name) VALUES (?)", [(name,) for name in glider_names])

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
        "gliders": len(glider_names),
        "reservations": len(test_data),
    }

@app.api_route("/api/health", methods=["GET", "HEAD"], include_in_schema=False)
def health_check():
    return {"status": "ok"}

if not TESTING:
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

# ─── Catch-all handler for client-side routing ───────────────────────────────
if not TESTING:
    @app.exception_handler(StarletteHTTPException)
    async def custom_404_handler(request: StarletteRequest, exc: StarletteHTTPException):
        if request.url.path.startswith("/api"):
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
        index_path = os.path.join("frontend", "dist", "index.html")
        return FileResponse(index_path)
