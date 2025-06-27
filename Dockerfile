# ─── Base Python Image ─────────────────────────────────────────────────────────
FROM python:3.11-slim

# ─── Set Working Directory ─────────────────────────────────────────────────────
WORKDIR /app

# ─── Copy Only Backend Code ────────────────────────────────────────────────────
COPY backend/ ./backend/
COPY backend/requirements.txt .

# ─── Install Dependencies ──────────────────────────────────────────────────────
RUN pip install --no-cache-dir -r requirements.txt

# ─── Initialize Database ───────────────────────────────────────────────────────
RUN python backend/init_db.py

# ─── Expose Port for Uvicorn ───────────────────────────────────────────────────
EXPOSE 8000

# ─── Run Uvicorn Server ────────────────────────────────────────────────────────
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
