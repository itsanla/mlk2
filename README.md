# mlk2

## Development Mode (Tanpa Docker)

### Backend (Django API)

```bash
# Masuk ke folder api
cd api

# Aktifkan virtual environment
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate  # Windows

# Jalankan server
python manage.py runserver
```

Backend akan berjalan di: `http://localhost:8000`

### Frontend (Next.js)

```bash
# Masuk ke folder web (terminal baru)
cd web

# Jalankan development server
pnpm dev
```

Frontend akan berjalan di: `http://localhost:3000`

---

## Production Mode (Dengan Docker)

```bash
# Build dan jalankan semua service
docker-compose up --build

# Atau jalankan di background
docker-compose up -d

# Stop semua service
docker-compose down
```

- Backend API: `http://localhost:8000`
- Frontend Web: `http://localhost:3000`

---

## API Endpoints

### POST /api/predict/
Prediksi KBK berdasarkan judul TA

**Request:**
```json
{
  "judul": "implementasi cloud computing untuk sistem informasi"
}
```

**Response:**
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
