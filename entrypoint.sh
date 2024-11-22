#!/bin/sh

# Wait for PostgreSQL to be ready
while ! nc -z postgres 5432; do
  echo "Waiting for PostgreSQL..."
  sleep 1
done

# Apply migrations
alembic upgrade head

# Start the main application and Celery processes
python3 bot_state_main.py &
celery -A telegram_app.celery_app.celery_app.app worker --loglevel=info &
celery -A telegram_app.celery_app.celery_app.app beat --loglevel=info &

# Keep the container running
wait