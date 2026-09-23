#!/bin/bash
echo "========================================"
echo "  DRUSTI — Starting Development Server"
echo "========================================"

ROOT="$(cd "$(dirname "$0")" && pwd)"

# Start Backend
echo "[1/2] Starting FastAPI backend..."
cd "$ROOT/backend"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt --quiet
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

sleep 2

# Start Frontend
echo "[2/2] Starting Next.js frontend..."
cd "$ROOT/frontend"
npm install --silent
npm run dev &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "========================================"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
