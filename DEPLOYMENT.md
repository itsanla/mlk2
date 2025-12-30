# 🚀 MLK2 Production Deployment Guide

## 📋 Prerequisites

- Docker & Docker Compose installed
- Domain configured (kelompok2.mooo.com)
- SSL certificate (optional, for HTTPS)

## 🔧 Quick Start

### 1. Clone Repository
```bash
git clone <repository-url>
cd mlk2
```

### 2. Configure Environment
```bash
cp .env.production .env
# Edit .env and set your SECRET_KEY
```

### 3. Build & Run
```bash
docker-compose up -d --build
```

### 4. Check Status
```bash
docker-compose ps
docker-compose logs -f
```

## 🏥 Health Checks

- **Redis**: `docker exec mlk2-redis redis-cli ping`
- **API**: `curl http://localhost:8000/api/health/`
- **Web**: `curl http://localhost:3000/`

## 📊 Services

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend API | 8000 | http://localhost:8000 |
| Redis | 6379 | redis://localhost:6379 |

## 🔄 Update Deployment

```bash
# Pull latest images
docker-compose pull

# Restart services
docker-compose up -d

# Or rebuild from source
docker-compose up -d --build
```

## 🛑 Stop Services

```bash
docker-compose down
```

## 🗑️ Clean Up (Remove all data)

```bash
docker-compose down -v
```

## 📦 Build & Push Images

### Backend
```bash
cd api
docker build -t itsanla/mlk2-api:latest .
docker push itsanla/mlk2-api:latest
```

### Frontend
```bash
cd web
docker build -t itsanla/mlk2-web:latest \
  --build-arg NEXT_PUBLIC_API_URL=https://kelompok2-api.mooo.com .
docker push itsanla/mlk2-web:latest
```

## 🔐 Security Notes

1. **Change SECRET_KEY** in production
2. **Set DEBUG=False** in production
3. **Configure ALLOWED_HOSTS** properly
4. **Use HTTPS** in production
5. **Limit Redis memory** (already set to 256MB)

## 📈 Monitoring

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f web
docker-compose logs -f redis
```

### Resource Usage
```bash
docker stats mlk2-api mlk2-web mlk2-redis
```

## 🎯 Default Model

The system uses **Model v4.1.0** by default:
- Trigram (1-3)
- Alpha: 0.01
- TF-IDF: True
- Cross-Validation: 88% accuracy

## 🌐 Production URLs

- **Frontend**: https://kelompok2.mooo.com
- **Backend API**: https://kelompok2-api.mooo.com

## 📞 Support

For issues, check logs:
```bash
docker-compose logs --tail=100
```
