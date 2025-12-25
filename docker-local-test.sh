#!/bin/bash

echo "Building local docker image for testing..."

docker build -t anyllm2music-backend .

# Inject env variable
docker run -d -p 80:80 \
  -e OPENROUTER_API_KEY=fake_key \
  -e OPENROUTER_URL=https://openrouter.ai/api/v1 \
  -e OPENROUTER_DEFAULT_FREE_MODEL=meta-llama/llama-3.3-70b-instruct:free \
  -e OPENROUTER_DEFAULT_MODEL=x-ai/grok-4.1-fast anyllm2music-backend

echo "Waiting for services to start..."
sleep 10

echo "Testing nginx proxy..."
curl -f http://localhost/ || echo "Test failed"

echo "Testing health endpoint..."
curl -f http://localhost/health || echo "Health check failed"
