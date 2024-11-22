# Use the base Python image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    netcat-openbsd \
    && apt-get clean

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"  

# Set working directory
WORKDIR /app

# Copy pyproject.toml and poetry.lock for dependency installation
COPY pyproject.toml poetry.lock /app/

# Install dependencies globally
RUN poetry config virtualenvs.create false && poetry install --no-dev

# Copy the rest of the application code
COPY . /app

# Command to wait for PostgreSQL, run migrations, and start the app
CMD sh -c ' \
  echo "Waiting for PostgreSQL to start..."; \
  while ! nc -z postgres 5432; do sleep 1; done; \
  echo "PostgreSQL is up!"; \
  echo "Running Alembic migrations..."; \
  alembic stamp head; \
  alembic revision --autogenerate -m "Initial migration"; \
  alembic upgrade head; \
  echo "Starting the application..."; \
  python3 bot_state_main.py & \
  celery -A telegram_app.celery_app.celery_app.app worker --loglevel=info & \
  celery -A telegram_app.celery_app.celery_app.app beat --loglevel=info & \
  wait'
