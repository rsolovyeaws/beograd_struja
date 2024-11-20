# Use the base Python image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
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

# Expose necessary ports (if applicable)
# EXPOSE 8000  # Example: FastAPI default port, adjust as needed

# Set default command
CMD ["sh", "-c", "python3 bot_state_main.py & \
    celery -A telegram_app.celery_app.celery_app.app worker --loglevel=info & \
    celery -A telegram_app.celery_app.celery_app.app beat --loglevel=info"]
