#!/bin/bash

# Build and Push Script for MLK2 Docker Images
# Usage: ./build-push.sh [version]
# Example: ./build-push.sh v1.0.0

VERSION=${1:-latest}

echo "🔨 Building images with tag: $VERSION"

# Build backend
echo "📦 Building backend..."
docker build -t itsanla/mlk2-api:$VERSION -t itsanla/mlk2-api:latest ./api

# Build frontend
echo "📦 Building frontend..."
docker build -t itsanla/mlk2-web:$VERSION -t itsanla/mlk2-web:latest ./web

echo "✅ Build completed!"
echo ""
echo "🚀 Pushing to Docker Hub..."

# Push backend
echo "⬆️  Pushing backend..."
docker push itsanla/mlk2-api:$VERSION
docker push itsanla/mlk2-api:latest

# Push frontend
echo "⬆️  Pushing frontend..."
docker push itsanla/mlk2-web:$VERSION
docker push itsanla/mlk2-web:latest

echo "✅ All images pushed successfully!"
echo ""
echo "📋 Images:"
echo "   - itsanla/mlk2-api:$VERSION"
echo "   - itsanla/mlk2-api:latest"
echo "   - itsanla/mlk2-web:$VERSION"
echo "   - itsanla/mlk2-web:latest"
