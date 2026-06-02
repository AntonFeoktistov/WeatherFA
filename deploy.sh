#!/bin/sh
set -e

cd "$(dirname "$0")"

if [ ! -f .env ]; then
  echo "Missing .env — copy .env.example to .env and set secrets first."
  exit 1
fi

docker compose -f docker-compose.prod.yml up -d --build

echo "Deployed. App should be available on port 80."
