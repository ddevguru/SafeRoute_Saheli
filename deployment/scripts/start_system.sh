#!/usr/bin/env bash
set -e

echo "=============================================================================="
echo "                SAFEROUTE SAHELI — LOCAL ECOSYSTEM LAUNCHER                   "
echo "=============================================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "[1/3] Checking Dependencies..."
command -v python3 >/dev/null 2>&1 || { echo >&2 "[ERROR] python3 is required but not installed."; exit 1; }
command -v node >/dev/null 2>&1 || { echo >&2 "[ERROR] node is required but not installed."; exit 1; }

echo "[2/3] Starting Python Flask Backend on http://127.0.0.1:5000 in background..."
cd "$ROOT_DIR"
python3 backend/run.py &
BACKEND_PID=$!

sleep 3

echo "[3/3] Starting React Admin Panel on http://localhost:3000..."
cd "$ROOT_DIR/admin_panel"
npm run dev &
ADMIN_PID=$!

trap "kill $BACKEND_PID $ADMIN_PID" EXIT

echo "=============================================================================="
echo "  SafeRoute Saheli Subsystems are Live:"
echo "  - Backend REST API: http://127.0.0.1:5000/api"
echo "  - Admin Command Center: http://localhost:3000"
echo "  Press Ctrl+C to stop all services."
echo "=============================================================================="

wait
