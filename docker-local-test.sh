#!/bin/bash

echo "Building local docker image for testing..."

# Check if .env file exists
if [ ! -f .env ]; then
  echo "Error: .env file not found. Please create it from .env.template and fill in your API keys."
  exit 1
fi

docker build -t anyllm2music-backend .

# Run the container (env vars loaded from .env file copied into the image)
CONTAINER_ID=$(docker run -d -p 8000:80 anyllm2music-backend)

echo "Waiting for services to start..."
sleep 10

echo "Testing nginx proxy..."
curl -f http://localhost:8000/ || echo "Test failed"

echo "Testing health endpoint..."
curl -f http://localhost:8000/health || echo "Health check failed"

echo "Stopping the container..."
docker stop $CONTAINER_ID
