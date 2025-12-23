#!/bin/bash

echo "🧹 Cleaning up disk space..."

# Stop containers
docker-compose down 2>/dev/null

# Remove unused Docker data
echo "Removing unused Docker images..."
docker image prune -af

echo "Removing unused Docker containers..."
docker container prune -f

echo "Removing unused Docker volumes..."
docker volume prune -f

echo "Removing unused Docker networks..."
docker network prune -f

echo "Removing build cache..."
docker builder prune -af

echo ""
echo "✅ Cleanup completed!"
echo ""
echo "📊 Disk usage:"
df -h /
