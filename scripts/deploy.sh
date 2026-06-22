#!/bin/bash
set -e

echo "🚀 Deploying Social App to Production"
echo "====================================="

# Build and start services
docker-compose -f docker/docker-compose.yml down
docker-compose -f docker/docker-compose.yml build
docker-compose -f docker/docker-compose.yml up -d

# Run migrations
docker-compose -f docker/docker-compose.yml exec web python manage.py migrate

# Collect static
docker-compose -f docker/docker-compose.yml exec web python manage.py collectstatic --noinput

# Create cache tables
docker-compose -f docker/docker-compose.yml exec web python manage.py createcachetable

echo "✅ Deployment complete!"
echo "App running at: http://localhost"
echo "MinIO Console: http://localhost:9001"
