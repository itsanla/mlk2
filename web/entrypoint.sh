#!/bin/sh

# Replace API_URL at runtime
API_URL=${NEXT_PUBLIC_API_URL:-http://localhost:8000}
echo "Setting API_URL to: $API_URL"

# Replace in public env.js if it exists
if [ -f "/app/public/env.js" ]; then
    sed -i "s|API_URL_PLACEHOLDER|$API_URL|g" /app/public/env.js
fi

exec "$@"
