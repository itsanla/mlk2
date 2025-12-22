# 🚀 Deployment Guide

This guide explains how to deploy the MLK2 application in different environments using proper environment variable configuration.

## 📁 Environment Files

- `.env.development` - For local development
- `.env.production` - For production deployment
- `.env.example` - Template for environment variables
- `.env` - Current active environment (not in git)

## 🏠 Local Development

### Option 1: Using Environment File
```bash
# Copy development environment
cp .env.development .env

# Start services
docker-compose up -d
```

### Option 2: Manual Setup
```bash
# Backend
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 manage.py runserver

# Frontend (in new terminal)
cd web
pnpm install
pnpm dev
```

## 🌐 Production Deployment

### Option 1: Docker Compose with Production Override
```bash
# Copy production environment
cp .env.production .env

# Deploy with production configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Option 2: Manual Environment Variables
```bash
# Set environment variables
export NEXT_PUBLIC_API_URL=https://sitabi-api.mooo.com
export DEBUG=False
export SECRET_KEY=your-production-secret-key

# Deploy
docker-compose up -d
```

### Option 3: Individual Container Deployment
```bash
# Backend
docker run -d \
  --name api \
  -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -e DEBUG=False \
  -e ALLOWED_HOSTS=sitabi-api.mooo.com \
  -e CORS_ALLOWED_ORIGINS=https://sitabi.mooo.com \
  itsanla/mlk2-api:latest

# Frontend
docker run -d \
  --name web \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=https://sitabi-api.mooo.com \
  -e NODE_ENV=production \
  itsanla/mlk2-web:latest
```

## 🔧 Environment Variables

### Backend Variables
- `DEBUG` - Enable/disable debug mode (True/False)
- `SECRET_KEY` - Django secret key for security
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `CORS_ALLOWED_ORIGINS` - Comma-separated list of allowed CORS origins

### Frontend Variables
- `NEXT_PUBLIC_API_URL` - Backend API URL (must start with NEXT_PUBLIC_ for client-side access)
- `NODE_ENV` - Node.js environment (development/production)

## 🌍 Current Production URLs

- **Frontend**: https://sitabi.mooo.com
- **Backend API**: https://sitabi-api.mooo.com

## 🔄 Switching Environments

To switch between environments, simply copy the appropriate environment file:

```bash
# For development
cp .env.development .env

# For production
cp .env.production .env

# Restart services
docker-compose down
docker-compose up -d
```

## ⚠️ Security Notes

1. Never commit `.env` files with real secrets to git
2. Use strong, unique secret keys in production
3. Restrict `ALLOWED_HOSTS` to your actual domains in production
4. Use HTTPS in production environments
5. Regularly rotate secret keys and API tokens

## 🐛 Troubleshooting

### Frontend can't connect to backend
- Check `NEXT_PUBLIC_API_URL` is set correctly
- Verify backend is accessible at the specified URL
- Check CORS configuration in backend

### Environment variables not loading
- Ensure `.env` file exists in project root
- Check variable names are correct (case-sensitive)
- Restart containers after changing environment variables

### Docker containers not communicating
- Verify both containers are on the same network
- Use service names (e.g., `api:8000`) for internal communication
- Use external URLs for client-side requests