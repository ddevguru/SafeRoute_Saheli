#!/usr/bin/env bash
# ==============================================================================
# SafeRoute Saheli — Render Build & Migration Script
# ==============================================================================
set -o errexit

echo ">>> [1/3] Upgrading pip and installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ">>> [2/3] Running database schema creation & migrations..."
python backend/scripts/init_db.py

echo ">>> [3/3] Build completed successfully. Ready for launch."
