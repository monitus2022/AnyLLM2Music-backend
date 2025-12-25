FROM python:3.12-slim

WORKDIR /app

# Add nginx and supervisor dependencies
RUN apt-get update && apt-get install -y curl nginx supervisor && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 - && /root/.local/bin/poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN /root/.local/bin/poetry install --no-interaction --no-ansi

COPY src/ ./src/
COPY nginx.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 80

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]