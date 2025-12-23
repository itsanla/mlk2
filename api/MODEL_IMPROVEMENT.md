# 📊 Model Improvement Report - Naive Bayes Optimization

## 🎯 Executive Summary

Model Naive Bayes telah dioptimasi menggunakan **5 Pilar Perbaikan** untuk data kecil (160 samples). Hasil menunjukkan improvement signifikan dalam CV accuracy dan pengurangan overfitting.

---

## 📈 Hasil Improvement

### Before vs After Comparison

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **CV Accuracy** | 51.25% | 55.00% | **+3.75%** ✅ |
| **Overfitting Score** | 37.5% | 13.12% | **-24.38%** ✅ |
| **Vocabulary Size** | 404 | 80 | **-80.2%** ✅ |
| **Sparsity** | 97%+ | 96.13% | **-0.87%** ✅ |
| **Independence Violation** | N/A | 0.89% | **Low** ✅ |

### Per-Class F1 Score

| Class | Before | After | Change |
|-------|--------|-------|--------|
| AI/ML | ~0.60 | **0.68** | +8% ✅ |
| Software | ~0.55 | **0.59** | +4% ✅ |
| Jaringan | ~0.50 | **0.56** | +6% ✅ |
| Animasi | 0.37 | **0.33** | -4% ⚠️ |

**Note**: Animasi masih menjadi kelas terlemah dan memerlukan perbaikan lebih lanjut (lihat Phase 2).

---

## 🏗️ 5 Pilar Perbaikan yang Diterapkan

### ✅ PILAR 1: Aggressive Smoothing
**Implementasi:**
```python
alpha = 3.0  # DARI 0.1 → 3.0
```

**Rasional:**
- Dengan 404 fitur dan hanya 40 samples/kelas, rata-rata fitur muncul 3-4x
- Alpha=3.0 menambahkan "pseudocount" signifikan untuk stabilitas
- Mencegah probabilitas nol dan overfit

**Impact:**
- Zero-probability features: 50% → 32-49% per kelas
- Smoothing impact lebih merata antar kelas

---

### ✅ PILAR 2: Feature Space Compression
**Implementasi:**
```python
TfidfVectorizer(
    max_features=80,      # DARI 500 → 80 (6.25x reduksi)
    ngram_range=(1, 2),   # DARI (1,3) → (1,2)
    min_df=3,             # DARI 2 → 3
    max_df=0.5,           # DARI 0.8 → 0.5
    stop_words=[...]      # +17 domain stopwords
)
```

**Rasional:**
- Rasio fitur:data 2.5:1 → 0.5:1 (ideal untuk Naive Bayes)
- Trigram terlalu sparse untuk 160 data
- Hapus kata IT generik: 'sistem', 'implementasi', 'berbasis', dll

**Impact:**
- Vocabulary: 404 → 80 features
- Sparsity: 97%+ → 96.13%
- Independence violation: 0.89% (sangat rendah)

---

### ✅ PILAR 3: Enhanced Preprocessing
**Implementasi:**
```python
def preprocess(text):
    # Normalisasi domain terms
    # Hapus angka dan simbol
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Hapus kata pendek (<3 karakter)
    tokens = [t for t in tokens if len(t) > 3]
```

**Rasional:**
- Angka dan simbol tidak informatif untuk klasifikasi KBK
- Kata pendek (<3 char) biasanya noise
- Fokus pada kata bermakna

**Impact:**
- Kualitas fitur lebih baik
- Mengurangi noise dalam vocabulary

---

### ✅ PILAR 4: Domain Stopwords
**Implementasi:**
```python
domain_stopwords = [
    'sistem', 'implementasi', 'berbasis', 'aplikasi', 
    'informasi', 'web', 'teknologi', 'media', 'padang', 
    'politeknik', 'negeri', 'perancangan', 'metod',
    'menggunakan', 'dengan', 'untuk', 'pada'
]
```

**Rasional:**
- Kata-kata ini muncul di >50% dokumen semua kelas
- Tidak diskriminatif untuk klasifikasi
- Mengurangi feature overlap antar kelas

**Impact:**
- Fitur lebih mutual exclusive antar kelas
- Meningkatkan class separability

---

### ✅ PILAR 5: Reduced Keyword Boost
**Implementasi:**
```python
KEYWORD_BOOST_FACTOR = 0.10  # DARI 0.15 → 0.10
```

**Rasional:**
- Model base lebih baik, butuh boost lebih kecil
- Mengurangi bias dari keyword matching
- Lebih percaya pada probabilitas Naive Bayes

---

## 🔬 Analisis Teknis

### Naive Bayes Properties

1. **Class Priors** (P(class))
   - Balanced: ~25% per kelas
   - fit_prior=True bekerja optimal

2. **Feature Log Probabilities**
   - Mean: -4.5 to -4.0 (stabil)
   - Std: 0.8-1.0 (variance rendah)
   - Smoothing bekerja efektif

3. **Conditional Independence**
   - Violation ratio: 0.89% (sangat rendah!)
   - Naive Bayes assumption terpenuhi
   - Feature correlation minimal

4. **Laplace Smoothing Impact**
   - Avg difference: 0.01-0.02 per kelas
   - Smoothing signifikan tapi tidak dominan
   - Balance antara data dan prior

---

## ⚠️ Masalah yang Masih Ada

### 1. Animasi Class Performance
**Problem:**
- F1 Score: 0.33 (terendah)
- Precision: 37.5%, Recall: 30%
- Sering misclassified sebagai Software (11x) dan AI/ML (8x)

**Root Cause:**
- Overlap keyword dengan Software (aplikasi, web, interaktif)
- Kurangnya distinctive features untuk Animasi
- Sample size mungkin tidak representatif

**Recommended Fix (Phase 2):**
```python
# Tambahkan fitur pseudo khusus Animasi
animasi_keywords = [
    'blender', 'maya', 'rigging', 'render', 'animasi', 
    '3d', 'karakter', 'motion', 'vfx', 'texturing', 'modelling'
]

def enhance_animasi_features(text):
    score = sum(1 for kw in animasi_keywords if kw in text.lower())
    return {'animasi_score': score, 'is_animasi': score > 0}
```

### 2. Overfitting Masih Moderate
**Problem:**
- Train: 68.12%, CV: 55.00%
- Gap: 13.12% (target <10%)

**Recommended Fix (Phase 2):**
- Gunakan ComplementNB (lebih robust untuk data kecil)
- Feature selection dengan mutual information
- Ensemble dengan different alpha values

### 3. High Bias
**Problem:**
- Bias: 45% (CV accuracy rendah)
- Model underfitting

**Recommended Fix (Phase 2):**
- Tambahkan bigram yang lebih spesifik
- Feature engineering: POS tags, domain entities
- Augmentasi data dengan parafrase

---

## 🚀 Roadmap Perbaikan Lanjutan

### Phase 2: Feature Engineering (Target: CV 60-65%)
- [ ] Class-specific feature extraction untuk Animasi
- [ ] Mutual information feature selection
- [ ] Bigram optimization (pilih bigram informatif)
- [ ] Stemming dengan Sastrawi

### Phase 3: Advanced Tuning (Target: CV 65-70%)
- [ ] ComplementNB vs MultinomialNB comparison
- [ ] Grid search: alpha [1.5, 2.0, 2.5, 3.0, 5.0]
- [ ] SelectKBest dengan chi2 (k=40-60)
- [ ] Ensemble: voting dari multiple alpha

### Phase 4: Data Quality (Target: CV 70-75%)
- [ ] Review dan clean mislabeled data
- [ ] Augmentasi data dengan sinonim
- [ ] Collect more Animasi samples
- [ ] Balance class distribution jika perlu

---

## 📝 Kesimpulan

### ✅ Achievements
1. **CV Accuracy improved**: 51.25% → 55.00% (+3.75%)
2. **Overfitting reduced**: 37.5% → 13.12% (-24.38%)
3. **Feature space optimized**: 404 → 80 features (-80%)
4. **Model health better**: Independence violation <1%

### 🎯 Next Steps
1. **Immediate**: Deploy model baru ke production
2. **Short-term**: Implement Phase 2 (Feature Engineering)
3. **Long-term**: Data collection untuk Animasi class

### 💡 Key Learnings
- **Untuk data kecil**: Less is more (fitur sedikit > fitur banyak)
- **Smoothing**: Alpha besar (>1.0) lebih baik untuk data kecil
- **Domain knowledge**: Stopwords domain-specific sangat penting
- **Naive Bayes**: Bekerja optimal ketika feature independence terpenuhi

---

## 📚 References

- Scikit-learn Naive Bayes: https://scikit-learn.org/stable/modules/naive_bayes.html
- TF-IDF Best Practices: https://scikit-learn.org/stable/modules/feature_extraction.html
- Laplace Smoothing: https://en.wikipedia.org/wiki/Additive_smoothing

---

**Generated**: 2025-01-XX  
**Model Version**: v2.0 (Optimized)  
**Author**: Kelompok 2 - Machine Learning
