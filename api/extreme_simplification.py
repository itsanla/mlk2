#!/usr/bin/env python3
"""Extreme Simplification - Reduce Model Complexity"""

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

# Extreme simplification scenarios
scenarios = [
    # Very few features + high alpha
    {"name": "F30 A10", "max_features": 30, "alpha": 10.0, "min_df": 4},
    {"name": "F40 A10", "max_features": 40, "alpha": 10.0, "min_df": 4},
    {"name": "F50 A10", "max_features": 50, "alpha": 10.0, "min_df": 4},
    {"name": "F30 A15", "max_features": 30, "alpha": 15.0, "min_df": 4},
    {"name": "F40 A15", "max_features": 40, "alpha": 15.0, "min_df": 4},
    {"name": "F50 A15", "max_features": 50, "alpha": 15.0, "min_df": 4},
    
    # Unigram only (simpler)
    {"name": "F40 A10 U", "max_features": 40, "alpha": 10.0, "min_df": 4, "ngram": (1,1)},
    {"name": "F50 A10 U", "max_features": 50, "alpha": 10.0, "min_df": 4, "ngram": (1,1)},
    {"name": "F40 A15 U", "max_features": 40, "alpha": 15.0, "min_df": 4, "ngram": (1,1)},
    
    # High min_df (only frequent terms)
    {"name": "F50 A10 D5", "max_features": 50, "alpha": 10.0, "min_df": 5},
    {"name": "F60 A10 D5", "max_features": 60, "alpha": 10.0, "min_df": 5},
    {"name": "F50 A15 D5", "max_features": 50, "alpha": 15.0, "min_df": 5},
]

stopwords = ['sistem', 'implementasi', 'berbasis', 'aplikasi', 'informasi', 
             'web', 'teknologi', 'media', 'padang', 'politeknik', 'negeri', 
             'perancangan', 'metod', 'menggunakan', 'dengan', 'untuk', 'pada']

print("=" * 90)
print("🔥 EXTREME SIMPLIFICATION - REDUCE MODEL COMPLEXITY")
print("=" * 90)
print(f"{'Scenario':<15} {'Train':<10} {'CV':<10} {'Overfit':<10} {'Underfit':<10} {'Status':<15}")
print("-" * 90)

best = None
best_score = float('inf')

for s in scenarios:
    ngram = s.get("ngram", (1,2))
    vec = TfidfVectorizer(
        max_features=s["max_features"], 
        ngram_range=ngram,
        min_df=s["min_df"], 
        max_df=0.5, 
        sublinear_tf=True, 
        stop_words=stopwords
    )
    X_vec = vec.fit_transform(X)
    model = MultinomialNB(alpha=s["alpha"])
    model.fit(X_vec, y)
    
    train = model.score(X_vec, y)
    cv = np.mean(cross_val_score(model, X_vec, y, cv=5))
    overfit = train - cv
    underfit = 1 - cv
    
    if overfit < 0.10:
        status = f"✅ O:{overfit:.1%}"
        score = underfit
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
    print("\n🏆 WINNER:")
    print(f"   {best['name']}")
    print(f"   Alpha: {best['alpha']}, Features: {best['max_features']}, MinDF: {best['min_df']}")
    print(f"   Train: {best['train']:.2%}, CV: {best['cv']:.2%}")
    print(f"   Overfitting: {best['overfit']:.2%} ✅")
    print(f"   Underfitting: {best['underfit']:.2%}")
    
    # Apply to model
    print("\n📝 Applying to ml_model.py...")
    print(f"   max_features={best['max_features']}")
    print(f"   alpha={best['alpha']}")
    print(f"   min_df={best['min_df']}")
else:
    print("\n❌ Still no solution. Data size (160) is too small for <10% overfitting.")
    print("   Recommendation: Accept 13-15% overfitting OR collect 300+ samples")
