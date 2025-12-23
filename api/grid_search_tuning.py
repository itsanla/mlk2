#!/usr/bin/env python3
"""
Grid Search untuk menemukan kombinasi optimal:
- Overfitting < 10%
- Underfitting seminimal mungkin
"""

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

# Load data
df = pd.read_csv(Path(__file__).parent / "data.csv")
X = df["Judul TA Bersih"].apply(preprocess)
y = df["KBK"]

# Grid search parameters
scenarios = [
    # Scenario 1: Baseline v2.0
    {"name": "v2.0 Baseline", "max_features": 80, "min_df": 3, "max_df": 0.5, "alpha": 3.0},
    
    # Scenario 2-5: Vary alpha (most impactful)
    {"name": "Alpha 2.5", "max_features": 80, "min_df": 3, "max_df": 0.5, "alpha": 2.5},
    {"name": "Alpha 3.5", "max_features": 80, "min_df": 3, "max_df": 0.5, "alpha": 3.5},
    {"name": "Alpha 4.0", "max_features": 80, "min_df": 3, "max_df": 0.5, "alpha": 4.0},
    {"name": "Alpha 4.5", "max_features": 80, "min_df": 3, "max_df": 0.5, "alpha": 4.5},
    
    # Scenario 6-8: Vary max_features
    {"name": "Features 70", "max_features": 70, "min_df": 3, "max_df": 0.5, "alpha": 3.5},
    {"name": "Features 90", "max_features": 90, "min_df": 3, "max_df": 0.5, "alpha": 3.5},
    {"name": "Features 100", "max_features": 100, "min_df": 3, "max_df": 0.5, "alpha": 3.5},
    
    # Scenario 9-11: Vary min_df
    {"name": "MinDF 2", "max_features": 80, "min_df": 2, "max_df": 0.5, "alpha": 3.5},
    {"name": "MinDF 4", "max_features": 80, "min_df": 4, "max_df": 0.5, "alpha": 3.5},
    
    # Scenario 12-14: Vary max_df
    {"name": "MaxDF 0.4", "max_features": 80, "min_df": 3, "max_df": 0.4, "alpha": 3.5},
    {"name": "MaxDF 0.6", "max_features": 80, "min_df": 3, "max_df": 0.6, "alpha": 3.5},
    
    # Scenario 15-18: Combined optimal
    {"name": "Combo 1", "max_features": 75, "min_df": 3, "max_df": 0.45, "alpha": 3.8},
    {"name": "Combo 2", "max_features": 85, "min_df": 3, "max_df": 0.48, "alpha": 3.6},
    {"name": "Combo 3", "max_features": 78, "min_df": 3, "max_df": 0.5, "alpha": 4.2},
    {"name": "Combo 4", "max_features": 82, "min_df": 3, "max_df": 0.52, "alpha": 3.9},
]

stopwords = ['sistem', 'implementasi', 'berbasis', 'aplikasi', 'informasi', 
             'web', 'teknologi', 'media', 'padang', 'politeknik', 'negeri', 
             'perancangan', 'metod', 'menggunakan', 'dengan', 'untuk', 'pada']

print("=" * 100)
print("🔍 GRID SEARCH - MENCARI KONFIGURASI OPTIMAL")
print("=" * 100)
print(f"{'Scenario':<20} {'Train Acc':<12} {'CV Acc':<12} {'Overfit':<12} {'Underfit':<12} {'Status':<15}")
print("-" * 100)

best_config = None
best_score = float('inf')  # Minimize: overfitting + underfitting

for scenario in scenarios:
    vectorizer = TfidfVectorizer(
        max_features=scenario["max_features"],
        ngram_range=(1, 2),
        min_df=scenario["min_df"],
        max_df=scenario["max_df"],
        sublinear_tf=True,
        stop_words=stopwords
    )
    
    X_vec = vectorizer.fit_transform(X)
    model = MultinomialNB(alpha=scenario["alpha"])
    model.fit(X_vec, y)
    
    train_acc = model.score(X_vec, y)
    cv_scores = cross_val_score(model, X_vec, y, cv=5, scoring="accuracy")
    cv_acc = np.mean(cv_scores)
    
    overfitting = train_acc - cv_acc
    underfitting = 1 - cv_acc
    
    # Status
    if overfitting < 0.10 and underfitting < 0.45:
        status = "✅ EXCELLENT"
        combined_score = overfitting + underfitting
        if combined_score < best_score:
            best_score = combined_score
            best_config = scenario
    elif overfitting < 0.10:
        status = "✓ Good Overfit"
    elif underfitting < 0.45:
        status = "✓ Good Underfit"
    else:
        status = "❌ Poor"
    
    print(f"{scenario['name']:<20} {train_acc:<12.2%} {cv_acc:<12.2%} {overfitting:<12.2%} {underfitting:<12.2%} {status:<15}")

print("=" * 100)
if best_config:
    print("\n🏆 BEST CONFIGURATION FOUND:")
    print(f"   Name: {best_config['name']}")
    print(f"   Max Features: {best_config['max_features']}")
    print(f"   Min DF: {best_config['min_df']}")
    print(f"   Max DF: {best_config['max_df']}")
    print(f"   Alpha: {best_config['alpha']}")
    print(f"   Combined Score: {best_score:.4f}")
else:
    print("\n⚠️  No configuration met the criteria (Overfitting < 10% AND Underfitting < 45%)")
    print("   Recommendation: Collect more data or relax constraints")
