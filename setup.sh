#!/bin/bash

# Quick setup script for template-fastapi

set -e

echo "Setting up template-fastapi..."

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
    echo "Poetry installed."
else
    echo "Poetry is already installed."
fi

# Install dependencies
echo "Installing dependencies..."
poetry install --with dev

# Copy env template if .env doesn't exist
if [ ! -f .env ]; then
    cp .env.template .env
    echo "Copied .env.template to .env. Please edit .env with your actual values."
else
    echo ".env file already exists."
fi

echo "Setup complete! You can now run the server with: poetry run uvicorn src.main:app --reload"