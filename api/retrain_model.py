#!/usr/bin/env python3
"""
Script untuk retrain model v3.0 dengan optimasi agresif
Menerapkan Quick Wins: Animasi Features, ComplementNB, Bigram Focus
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from prediction.ml_model import NaiveBayesModel

def main():
    print("=" * 80)
    print("🚀 RETRAINING MODEL v3.0 - QUICK WINS IMPLEMENTATION")
    print("=" * 80)
    print()
    print("📋 v3.0 - Extreme Simplification (Best Possible):")
    print("   ✅ Alpha: 3.0 → 10.0 (extreme smoothing)")
    print("   ✅ Features: 80 → 40 (50% reduction)")
    print("   ✅ Min DF: 3 → 4 (only frequent terms)")
    print("   ✅ Animasi Boost 30%")
    print("   ✅ Expected: Overfitting ~11.9% (closest to <10%)")
    print("   ⚠️  Note: <10% impossible with 160 data")
    print()
    print("-" * 80)
    
    # Path to CSV
    csv_path = Path(__file__).parent / "data.csv"
    
    if not csv_path.exists():
        print(f"❌ Error: File {csv_path} tidak ditemukan!")
        return 1
    
    print(f"📂 Loading data dari: {csv_path}")
    
    # Initialize and train model
    model = NaiveBayesModel()
    
    print("🔄 Training model...")
    try:
        model.train(str(csv_path))
        print("✅ Model berhasil di-train dan disimpan!")
    except Exception as e:
        print(f"❌ Error saat training: {e}")
        return 1
    
    print()
    print("-" * 80)
    print("📊 ANALISIS MODEL")
    print("-" * 80)
    
    # Analyze model
    try:
        analysis = model.analyze_model(str(csv_path))
        
        # Performance metrics
        perf = analysis['performance']
        health = analysis['model_health']
        nb_specific = analysis['naive_bayes_specific']
        
        print()
        print("🎯 PERFORMA MODEL:")
        print(f"   Training Accuracy:    {perf['train_accuracy']:.2%}")
        print(f"   CV Mean Accuracy:     {perf['cv_mean_accuracy']:.2%}")
        print(f"   CV Std:               ±{perf['cv_std_accuracy']:.2%}")
        print()
        
        print("🏥 KESEHATAN MODEL:")
        print(f"   Overfitting Score:    {health['overfitting_score']:.2%} ({health['overfitting_status']})")
        print(f"   Bias:                 {health['bias']:.2%}")
        print(f"   Variance:             {health['variance']:.4f}")
        print()
        
        print("🔬 NAIVE BAYES METRICS:")
        print(f"   Vocabulary Size:      {nb_specific['tfidf_vectorizer_stats']['vocabulary_size']}")
        print(f"   Sparsity:             {nb_specific['tfidf_vectorizer_stats']['sparsity']:.2%}")
        print(f"   Independence Violation: {nb_specific['conditional_independence']['violation_ratio']:.2%} ({nb_specific['conditional_independence']['status']})")
        print()
        
        print("📈 PER-CLASS PERFORMANCE:")
        for cls, metrics in analysis['per_class_metrics'].items():
            print(f"   {cls:25} F1: {metrics['f1_score']:.2%}  Precision: {metrics['precision']:.2%}  Recall: {metrics['recall']:.2%}")
        
        print()
        print("🎲 ZERO PROBABILITY FEATURES:")
        for cls, data in nb_specific['zero_probability_features'].items():
            print(f"   {cls:25} {data['count']:3d} features ({data['percentage']:.1f}%)")
        
        print()
        print("=" * 80)
        print("✅ TRAINING v3.0 SELESAI!")
        print("=" * 80)
        print()
        print("📝 Target v3.0:")
        print("   • CV Accuracy: 55% → 68-70%")
        print("   • Animasi F1: 0.33 → 0.55+")
        print("   • Confidence Medium+: 5% → 40%")
        print("   • KL Divergence: 0.03 → 0.15+")
        print("   • Overfitting: 13% → <8%")
        print()
        print("🎯 Key Improvements:")
        print("   ✓ ComplementNB untuk data kecil")
        print("   ✓ Bigram/Trigram lebih spesifik")
        print("   ✓ Animasi feature injection")
        print("   ✓ Aggressive stopwords (overlap culprits)")
        print()
        
        return 0
        
    except Exception as e:
        print(f"❌ Error saat analisis: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
