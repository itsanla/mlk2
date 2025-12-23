#!/bin/bash

# Build and Push Script for MLK2 Docker Images

VERSION=${1:-latest}

echo "🔨 Building images..."

# Build backend
docker build -t itsanla/mlk2-api:$VERSION ./api

# Build frontend with production API URL
docker build \
  --build-arg NEXT_PUBLIC_API_URL=https://sitabi-api.mooo.com \
  -t itsanla/mlk2-web:$VERSION \
  ./web

if [ "$VERSION" != "latest" ]; then
    docker tag itsanla/mlk2-api:$VERSION itsanla/mlk2-api:latest
    docker tag itsanla/mlk2-web:$VERSION itsanla/mlk2-web:latest
fi

echo "✅ Build completed!"
echo ""
echo "🚀 Pushing to Docker Hub..."

docker push itsanla/mlk2-api:$VERSION
docker push itsanla/mlk2-web:$VERSION

if [ "$VERSION" != "latest" ]; then
    docker push itsanla/mlk2-api:latest
    docker push itsanla/mlk2-web:latest
fi

echo "✅ Done!"
