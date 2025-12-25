FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry
RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi

# Add fluidsynth dependencies
RUN apt-get update && apt-get install -y fluidsynth && rm -rf /var/lib/apt/lists/*

COPY src/ ./src/

# Local testing purpose
COPY .env ./ 

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]