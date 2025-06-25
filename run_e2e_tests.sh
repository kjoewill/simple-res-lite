#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# ─── Helper: Kill process on a given port ─────────────────────────────────────
kill_port_process() {
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
TESTING=1 ./venv/bin/uvicorn main:app --port 8000 > ../backend.log 2>&1 &
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
(cd frontend && npx wait-on http://localhost:8000/api/health http://localhost:5173)

# Optional: verify backend health with GET
echo "🔎 Verifying backend health check..."
curl -sSf http://localhost:8000/api/health > /dev/null

# ─── Step 5: Run Playwright Tests ─────────────────────────────────────────────
run_tests() {
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

  return $EXIT_CODE
}

run_tests
RESULT=$?

# ─── Step 6: Cleanup ──────────────────────────────────────────────────────────
echo "🧹 Cleaning up background servers..."
kill $BACK_PID
kill $FRONT_PID

exit $RESULT
