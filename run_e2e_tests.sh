#!/bin/bash

set -e

# ─── Config ───────────────────────────────────────────────────────────────────
WATCH_MODE=false
if [[ "$1" == "--watch" ]]; then
  WATCH_MODE=true
fi

# ─── Helper: Kill process on a given port ─────────────────────────────────────
function kill_port_process() {
  local PORT=$1
  lsof -ti tcp:$PORT | xargs kill -9 2>/dev/null || true
}

# ─── Step 1: Cleanup ──────────────────────────────────────────────────────────
echo "🧹 Cleaning up any existing processes on ports 8000 and 5173..."
kill_port_process 8000
kill_port_process 5173
rm -f backend.log frontend.log

# ─── Step 2: Start Backend ────────────────────────────────────────────────────
echo "🔧 Starting backend..."
cd backend
TESTING=1 ./venv/bin/uvicorn main:app --reload --port 8000 > ../backend.log 2>&1 &
BACK_PID=$!
cd ..

# ─── Step 3: Start Frontend ───────────────────────────────────────────────────
echo "🔧 Starting frontend..."
cd frontend
npm run dev -- --port 5173 --strictPort > ../frontend.log 2>&1 &
FRONT_PID=$!
cd ..

# ─── Step 4: Wait for Servers ─────────────────────────────────────────────────
echo "⏳ Waiting for backend and frontend to be ready..."
if ! (cd frontend && npx wait-on --timeout 30000 http://localhost:8000/api/health http://localhost:5173); then
  echo "❌ Timeout waiting for servers to become ready."
  echo "🚨 Backend log tail:"
  tail -n 20 backend.log || echo "(no backend.log found)"
  echo "🚨 Frontend log tail:"
  tail -n 20 frontend.log || echo "(no frontend.log found)"
  kill $BACK_PID $FRONT_PID 2>/dev/null || true
  exit 1
fi

# ─── Step 5: Either Run Tests or Watch ────────────────────────────────────────
if [ "$WATCH_MODE" = true ]; then
  echo "✅ Servers running in watch mode. Ctrl+C to stop."
  trap "echo '🧹 Cleaning up...'; kill $BACK_PID $FRONT_PID; exit" INT
  wait
else
  echo "✅ Servers ready. Running Playwright tests..."
  cd frontend
  npx playwright test
  EXIT_CODE=$?
  cd ..

  if [ "$EXIT_CODE" -ne 0 ]; then
    echo "🚨 Frontend log tail:"
    tail -n 20 frontend.log
    echo "🚨 Backend log tail:"
    tail -n 20 backend.log
  fi

  echo "🧹 Cleaning up background servers..."
  kill $BACK_PID
  kill $FRONT_PID

  exit $EXIT_CODE
fi
