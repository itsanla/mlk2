#!/bin/sh

# Replace API_URL at runtime
API_URL=${API_URL:-http://localhost:8000}
echo "Setting API_URL to: $API_URL"

# Replace in public env.js
sed -i "s|API_URL_PLACEHOLDER|$API_URL|g" /app/public/env.js

exec "$@"
