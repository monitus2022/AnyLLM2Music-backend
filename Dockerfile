# Build stage ------------------------------------
FROM python:3.12-slim AS build

WORKDIR /app

# Install Poetry
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN curl -sSL https://install.python-poetry.org | python3 - && /root/.local/bin/poetry config virtualenvs.create false

# Install dependency
COPY pyproject.toml poetry.lock ./
RUN /root/.local/bin/poetry install --no-interaction --no-ansi --only=main

# Copy source code
COPY src/ ./src/




# Runtime stage --------------------------------------
FROM python:3.12-slim AS runtime

WORKDIR /app

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y nginx supervisor && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from build stage
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Copy source code and configs from build stage
COPY --from=build /app/src ./src/
COPY nginx.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy .env if it exists (for local testing; production uses env vars)
RUN [ -f .env ] && cp .env /app/.env || true

EXPOSE 80

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
