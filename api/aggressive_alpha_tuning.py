#!/usr/bin/env python3
"""Aggressive Alpha Tuning untuk Overfitting < 10%"""

import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import cross_val_score
from pathlib import Path

def preprocess(text):
    text = text.lower()
    text = re.sub(r"na[iï]ve?\s*baye?s?", "naive bayes", text)
    text = re.sub(r"augment\s*realiti", "augmented reality", text)
    text = re.sub(r"virtual\s*realiti", "virtual reality", text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = [t for t in text.split() if len(t) >= 4]
    return ' '.join(tokens)

df = pd.read_csv(Path(__file__).parent / "data.csv")
X = df["Judul TA Bersih"].apply(preprocess)
y = df["KBK"]

# Aggressive alpha + feature combinations
scenarios = [
    # Very high alpha
    {"name": "Alpha 5.0", "max_features": 80, "alpha": 5.0},
    {"name": "Alpha 6.0", "max_features": 80, "alpha": 6.0},
    {"name": "Alpha 7.0", "max_features": 80, "alpha": 7.0},
    {"name": "Alpha 8.0", "max_features": 80, "alpha": 8.0},
    {"name": "Alpha 10.0", "max_features": 80, "alpha": 10.0},
    
    # High alpha + more features
    {"name": "A5.0 F100", "max_features": 100, "alpha": 5.0},
    {"name": "A6.0 F100", "max_features": 100, "alpha": 6.0},
    {"name": "A7.0 F100", "max_features": 100, "alpha": 7.0},
    {"name": "A5.0 F120", "max_features": 120, "alpha": 5.0},
    {"name": "A6.0 F120", "max_features": 120, "alpha": 6.0},
    
    # High alpha + fewer features
    {"name": "A5.0 F60", "max_features": 60, "alpha": 5.0},
    {"name": "A6.0 F60", "max_features": 60, "alpha": 6.0},
    {"name": "A7.0 F60", "max_features": 60, "alpha": 7.0},
]

stopwords = ['sistem', 'implementasi', 'berbasis', 'aplikasi', 'informasi', 
             'web', 'teknologi', 'media', 'padang', 'politeknik', 'negeri', 
             'perancangan', 'metod', 'menggunakan', 'dengan', 'untuk', 'pada']

print("=" * 90)
print("🎯 AGGRESSIVE ALPHA TUNING - TARGET: OVERFITTING < 10%")
print("=" * 90)
print(f"{'Scenario':<15} {'Train':<10} {'CV':<10} {'Overfit':<10} {'Underfit':<10} {'Status':<15}")
print("-" * 90)

best = None
best_score = float('inf')

for s in scenarios:
    vec = TfidfVectorizer(max_features=s["max_features"], ngram_range=(1,2), 
                          min_df=3, max_df=0.5, sublinear_tf=True, stop_words=stopwords)
    X_vec = vec.fit_transform(X)
    model = MultinomialNB(alpha=s["alpha"])
    model.fit(X_vec, y)
    
    train = model.score(X_vec, y)
    cv = np.mean(cross_val_score(model, X_vec, y, cv=5))
    overfit = train - cv
    underfit = 1 - cv
    
    if overfit < 0.10:
        status = f"✅ {overfit:.1%}"
        score = underfit  # Minimize underfitting
        if score < best_score:
            best_score = score
            best = s.copy()
            best['train'] = train
            best['cv'] = cv
            best['overfit'] = overfit
            best['underfit'] = underfit
    else:
        status = f"❌ {overfit:.1%}"
    
    print(f"{s['name']:<15} {train:<10.2%} {cv:<10.2%} {overfit:<10.2%} {underfit:<10.2%} {status:<15}")

print("=" * 90)
if best:
    print("\n🏆 BEST CONFIGURATION:")
    print(f"   Scenario: {best['name']}")
    print(f"   Alpha: {best['alpha']}")
    print(f"   Max Features: {best['max_features']}")
    print(f"   Train Accuracy: {best['train']:.2%}")
    print(f"   CV Accuracy: {best['cv']:.2%}")
    print(f"   Overfitting: {best['overfit']:.2%} ✅")
    print(f"   Underfitting: {best['underfit']:.2%}")
else:
    print("\n❌ No configuration achieved Overfitting < 10%")
