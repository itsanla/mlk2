# 🎓 MLK2 - Prediksi KBK Tugas Akhir

> Sistem prediksi Kelompok Bidang Keahlian (KBK) menggunakan algoritma Naive Bayes

[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://hub.docker.com/u/itsanla)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000?logo=next.js&logoColor=white)](https://nextjs.org/)
[![Django](https://img.shields.io/badge/Django-6.0-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)

## 📋 Deskripsi

Aplikasi web untuk memprediksi kategori KBK (Software, Jaringan, AI/ML, Animasi) berdasarkan judul tugas akhir mahasiswa menggunakan algoritma Naive Bayes.

**Kelompok 2 - Machine Learning**
- 📋 Agel Deska Wisamulya (2311082002) - Project Manager
- 📊 Delonic Ligia (2311081009) - Data Analyst
- 💻 Anla Harpanda (2311083015) - Programmer

---

## 🚀 Quick Start dengan Docker

### Pull dari Docker Hub

```bash
# Pull images
docker pull itsanla/mlk2-api:latest
docker pull itsanla/mlk2-web:latest
```

### Jalankan Container

```bash
# Run backend
docker run -d \
  --name api \
  -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -e ALLOWED_HOSTS=* \
  itsanla/mlk2-api:latest

# Run frontend
docker run -d \
  --name web \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=https://kelompok2-api.mooo.com \
  itsanla/mlk2-web:latest
```

### Akses Aplikasi

- 🌐 **Frontend**: http://localhost:3000
- 🔌 **Backend API**: http://localhost:8000 (development) / https://kelompok2-api.mooo.com (production)

### Stop Container

```bash
docker stop api web
docker rm api web
```

---

## 🐳 Docker Compose (Recommended)

```bash
# Build dan jalankan semua service
docker-compose up -d

# Lihat logs
docker-compose logs -f

# Stop semua service
docker-compose down
```

---

## 💻 Development Mode (Tanpa Docker)

### Backend (Django API)

```bash
cd api

# Buat virtual environment
python3 -m venv venv

# Aktifkan virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Jalankan server
python3 manage.py runserver
```

✅ Backend: `http://localhost:8000`

### Frontend (Next.js)

```bash
cd web

# Install dependencies
pnpm install

# Jalankan development server
pnpm dev
```

✅ Frontend: `http://localhost:3000`

---

## 📡 API Documentation

### Endpoint: Prediksi KBK

**POST** `/api/predict/`

Prediksi kategori KBK berdasarkan judul tugas akhir.

#### Request

```bash
curl -X POST ${API_URL:-http://localhost:8000}/api/predict/ \
  -H "Content-Type: application/json" \
  -d '{"judul": "implementasi cloud computing untuk sistem informasi"}'
```

```json
{
  "judul": "implementasi cloud computing untuk sistem informasi"
}
```

#### Response

```json
{
  "judul": "implementasi cloud computing untuk sistem informasi",
  "predicted_kbk": "Software",
  "probabilities": {
    "Software": 0.35,
    "Animasi": 0.26,
    "Jaringan": 0.21,
    "AI / Machine Learning": 0.18
  }
}
```

---

## 🏗️ Tech Stack

### Backend
- **Framework**: Django 6.0 + Django REST Framework
- **ML Algorithm**: Naive Bayes (scikit-learn)
- **Server**: Gunicorn
- **Language**: Python 3.12

### Frontend
- **Framework**: Next.js 16
- **Styling**: Tailwind CSS
- **Language**: TypeScript
- **Package Manager**: pnpm

### DevOps
- **Containerization**: Docker
- **Registry**: Docker Hub
- **Deployment**: Railway, Vercel
- **DNS**: deSEC (dedyn.io)

---

## 🌐 Live Demo

- **Frontend**: https://kelompok2.mooo.com
- **Backend API**: https://kelompok2-api.mooo.com

---

## 🚀 Deployment

### Backend (Railway)

1. Deploy Docker image:
   ```
   itsanla/mlk2-api:latest
   ```

2. Environment Variables:
   ```env
   SECRET_KEY=your-secret-key
   DEBUG=False
   ALLOWED_HOSTS=*
   ```

3. Railway akan generate URL: `mlk2-api-production.up.railway.app`

### Frontend (Vercel)

1. Connect GitHub repository
2. Framework Preset: **Next.js**
3. Environment Variables:
   ```env
   NEXT_PUBLIC_API_URL=https://kelompok2-api.mooo.com
   ```
4. Deploy

### Custom Domain (deSEC)

1. Login ke [deSEC](https://desec.io/domains/kelompok2.dedyn.io)
2. Tambahkan DNS Records:

   **Frontend (Vercel):**
   ```
   Type: CNAME
   Name: www
   Target: cname.vercel-dns.com
   ```

   **Root Domain:**
   ```
   Type: A
   Name: @
   Target: 76.76.21.21 (Vercel IP)
   ```

3. Di Vercel, tambahkan custom domain:
   - Settings → Domains
   - Add: `www.kelompok2.dedyn.io`
   - Add: `kelompok2.dedyn.io`

---

## 🔧 Environment Variables

### Production URLs

```env
# Backend API
https://kelompok2-api.mooo.com

# Frontend
https://kelompok2.mooo.com
```

### Backend (.env)

```env
SECRET_KEY=your-django-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend.com
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=https://kelompok2-api.mooo.com
```

---

## 📦 Docker Images

- **Backend**: [`itsanla/mlk2-api`](https://hub.docker.com/r/itsanla/mlk2-api)
- **Frontend**: [`itsanla/mlk2-web`](https://hub.docker.com/r/itsanla/mlk2-web)

### Build Custom Image

```bash
# Backend
docker build -t itsanla/mlk2-api:latest ./api

# Frontend
docker build -t itsanla/mlk2-web:latest ./web
```

---

## 📝 License

MIT License - Politeknik Negeri Padang © 2025

---

## 👥 Contributors

Kelompok 2 - Mata Kuliah Machine Learning

**Politeknik Negeri Padang**
