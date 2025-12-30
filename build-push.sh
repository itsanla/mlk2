#!/bin/bash

# Build and Push Script for MLK2 Docker Images

set -e  # Exit on error

VERSION=${1:-latest}

echo "🔨 Building MLK2 Docker Images v$VERSION"
echo "================================================"
echo ""

echo "📦 Building Backend API..."
docker build -t itsanla/mlk2-api:$VERSION ./api

echo ""
echo "📦 Building Frontend Web..."
docker build \
  --build-arg NEXT_PUBLIC_API_URL=https://kelompok2-api.mooo.com \
  -t itsanla/mlk2-web:$VERSION \
  ./web

if [ "$VERSION" != "latest" ]; then
    echo ""
    echo "🏷️  Tagging as latest..."
    docker tag itsanla/mlk2-api:$VERSION itsanla/mlk2-api:latest
    docker tag itsanla/mlk2-web:$VERSION itsanla/mlk2-web:latest
fi

echo ""
echo "✅ Build completed!"
echo ""
echo "🚀 Pushing to Docker Hub..."
echo "================================================"

docker push itsanla/mlk2-api:$VERSION
docker push itsanla/mlk2-web:$VERSION

if [ "$VERSION" != "latest" ]; then
    docker push itsanla/mlk2-api:latest
    docker push itsanla/mlk2-web:latest
fi

echo ""
echo "✅ Successfully pushed!"
echo "📋 Images:"
echo "   - itsanla/mlk2-api:$VERSION"
echo "   - itsanla/mlk2-web:$VERSION"
if [ "$VERSION" != "latest" ]; then
    echo "   - itsanla/mlk2-api:latest"
    echo "   - itsanla/mlk2-web:latest"
fi
echo ""
echo "🎯 Usage:"
echo "   docker-compose pull"
echo "   docker-compose up -d"
echo ""
