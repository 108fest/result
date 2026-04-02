#!/bin/sh
set -e

echo "[backend] Waiting for database and applying migrations..."
MAX_RETRIES="${DB_MIGRATION_MAX_RETRIES:-30}"
RETRY_DELAY="${DB_MIGRATION_RETRY_DELAY_SECONDS:-2}"
ATTEMPT=1

until alembic upgrade head; do
  if [ "$ATTEMPT" -ge "$MAX_RETRIES" ]; then
    echo "[backend] Migration failed after ${MAX_RETRIES} attempts"
    exit 1
  fi

  echo "[backend] Migration attempt ${ATTEMPT} failed. Retrying in ${RETRY_DELAY}s..."
  ATTEMPT=$((ATTEMPT + 1))
  sleep "$RETRY_DELAY"
done

echo "[backend] Running startup script..."
PYTHONPATH=. python3 scripts/create_support_user_with_chats.py

echo "[backend] Starting API server..."
exec uvicorn app:app --host 0.0.0.0 --port 8000
