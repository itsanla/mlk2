# API Backend - Prediksi KBK Tugas Akhir

Backend Django dengan model Naive Bayes untuk memprediksi KBK (Kelompok Bidang Keahlian) berdasarkan judul Tugas Akhir.

## Setup

1. Aktifkan virtual environment:
```bash
source venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Jalankan migrasi:
```bash
python manage.py migrate
```

4. Jalankan server:
```bash
python manage.py runserver
```

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

### POST /api/train/
Train ulang model (opsional)

**Response:**
```json
{
  "message": "Model trained successfully"
}
```

## Model

- Algorithm: Multinomial Naive Bayes
- Vectorizer: TfidfVectorizer
- Dataset: 160 judul TA dengan 4 kategori KBK
  - Software
  - Jaringan
  - AI / Machine Learning
  - Animasi
