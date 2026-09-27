#!/usr/bin/env bash
set -e

echo "========================================================"
echo "  SafeRoute Saheli - Database Initialization Utility"
echo "========================================================"

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-3306}"
DB_USER="${DB_USER:-saheli_user}"
DB_PASS="${DB_PASS:-saheli_password}"
DB_NAME="${DB_NAME:-saferoute_saheli}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "Applying Schema from database/schema.sql..."
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" < "$ROOT_DIR/database/schema.sql"

echo "Seeding Benchmark Data from database/seed_data.sql..."
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" < "$ROOT_DIR/database/seed_data.sql"

echo "[SUCCESS] SafeRoute Saheli database successfully initialized!"
