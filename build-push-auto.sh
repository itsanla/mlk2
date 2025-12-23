#!/bin/bash

VERSION_FILE=".version"

# Baca versi saat ini atau mulai dari 1.0.0
if [ -f "$VERSION_FILE" ]; then
    CURRENT_VERSION=$(cat "$VERSION_FILE")
else
    CURRENT_VERSION="1.0.0"
fi

# Parse versi
IFS='.' read -r -a VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR="${VERSION_PARTS[0]}"
MINOR="${VERSION_PARTS[1]}"
PATCH="${VERSION_PARTS[2]}"

# Increment patch version
PATCH=$((PATCH + 1))
NEW_VERSION="$MAJOR.$MINOR.$PATCH"

echo "📦 Current version: $CURRENT_VERSION"
echo "🆕 New version: $NEW_VERSION"
echo ""

# Simpan versi baru
echo "$NEW_VERSION" > "$VERSION_FILE"

echo "🔨 Building images..."

# Build backend
docker build -t itsanla/mlk2-api:$NEW_VERSION -t itsanla/mlk2-api:latest ./api

# Build frontend
docker build \
  --build-arg NEXT_PUBLIC_API_URL=https://kelompok2-api.mooo.com \
  -t itsanla/mlk2-web:$NEW_VERSION \
  -t itsanla/mlk2-web:latest \
  ./web

echo "✅ Build completed!"
echo ""
echo "🚀 Pushing to Docker Hub..."

# Push dengan version tag
docker push itsanla/mlk2-api:$NEW_VERSION
docker push itsanla/mlk2-web:$NEW_VERSION

# Push latest tag
docker push itsanla/mlk2-api:latest
docker push itsanla/mlk2-web:latest

echo ""
echo "✅ Successfully pushed version $NEW_VERSION"
echo "📋 Images:"
echo "   - itsanla/mlk2-api:$NEW_VERSION"
echo "   - itsanla/mlk2-api:latest"
echo "   - itsanla/mlk2-web:$NEW_VERSION"
echo "   - itsanla/mlk2-web:latest"
