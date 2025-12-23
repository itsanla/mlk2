import pandas as pd
import pickle
import re
import numpy as np
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB, ComplementNB
from sklearn.model_selection import cross_val_score, cross_val_predict
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from sklearn.feature_selection import SelectKBest, mutual_info_classif
from sklearn.pipeline import Pipeline
from pathlib import Path

logger = logging.getLogger(__name__)


class ModelNotLoadedError(Exception):
    pass


class NaiveBayesModel:
    KEYWORD_BOOST_FACTOR = 0.30  # DARI 0.20 → 0.30 (3x dari original 0.10)
    
    # v3.0: Animasi-specific keywords untuk feature injection
    ANIMATION_KEYWORDS = {
        'tools': ['blender', 'maya', 'cinema4d', '3dsmax', 'sketchup', 'unity'],
        'techniques': ['rigging', 'render', 'texturing', 'modelling', 'animasi', 'animation'],
        'concepts': ['3d', 'karakter', 'character', 'motion', 'vfx', 'cg', 'toon']
    }

    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.selector = None
        self.model_path = Path(__file__).parent / "model.pkl"
        self.vectorizer_path = Path(__file__).parent / "vectorizer.pkl"
        self.selector_path = Path(__file__).parent / "selector.pkl"

        self.keywords = {
            "AI / Machine Learning": [
                "naive bayes",
                "machine learning",
                "neural",
                "prediksi",
                "klasifikasi",
                "algoritma",
                "knn",
                "decision",
                "clustering",
                "data mining",
                "deep learning",
                "ai",
                "saw",
                "ahp",
                "smart",
                "topsis",
                "spk",
                "keputusan",
                "rekomendasi",
            ],
            "Jaringan": [
                "jaringan",
                "network",
                "server",
                "mikrotik",
                "router",
                "firewall",
                "monitoring",
                "iot",
                "sensor",
                "esp",
                "nodemcu",
                "mqtt",
                "wireless",
                "wifi",
                "keamanan jaringan",
            ],
            "Animasi": [
                "augmented reality",
                "virtual reality",
                "ar",
                "vr",
                "3d",
                "animasi",
                "visualisasi",
                "ui ux",
                "design",
                "markerless",
                "unity",
                "blender",
                "interaktif",
                "media pembelajaran",
            ],
            "Software": [
                "android",
                "mobile",
                "web",
                "api",
                "rest",
                "cloud",
                "aws",
                "docker",
                "laravel",
                "react",
                "flutter",
                "codeigniter",
                "framework",
                "database",
                "crud",
                "aplikasi",
            ],
        }

    def extract_animasi_features(self, text):
        """v3.0: Extract Animasi-specific features untuk mengatasi class collapse"""
        text_lower = text.lower()
        tool_count = sum(1 for kw in self.ANIMATION_KEYWORDS['tools'] if kw in text_lower)
        tech_count = sum(1 for kw in self.ANIMATION_KEYWORDS['techniques'] if kw in text_lower)
        concept_count = sum(1 for kw in self.ANIMATION_KEYWORDS['concepts'] if kw in text_lower)
        
        return {
            'animasi_tool_count': tool_count,
            'animasi_tech_count': tech_count,
            'animasi_concept_count': concept_count,
            'has_animation_tool': tool_count > 0,
            'has_animation_tech': tech_count > 0,
            'animasi_total_score': tool_count + tech_count + concept_count
        }
    
    def preprocess(self, text):
        text = text.lower()
        # Normalisasi domain-specific terms
        text = re.sub(r"na[iï]ve?\s*baye?s?", "naive bayes", text)
        text = re.sub(r"augment\s*realiti", "augmented reality", text)
        text = re.sub(r"virtual\s*realiti", "virtual reality", text)
        text = re.sub(r"komput", "komputer", text)
        text = re.sub(r"berbasi", "berbasis", text)
        text = re.sub(r"teknolog", "teknologi", text)
        text = re.sub(r"uiux|ui/ux", "ui ux", text)
        # Hapus angka dan simbol
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        # Hapus kata pendek (<4 karakter) - v3.0: lebih agresif
        tokens = text.split()
        tokens = [t for t in tokens if len(t) >= 4]
        return ' '.join(tokens)

    def calculate_keyword_score(self, text):
        scores = {}
        for category, keywords in self.keywords.items():
            score = sum(1 for kw in keywords if kw in text)
            scores[category] = score
        return scores

    def train(self, csv_path):
        csv_file = Path(csv_path)
        if not csv_file.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        df = pd.read_csv(csv_path)

        required_columns = ["Judul TA Bersih", "KBK"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        X = df["Judul TA Bersih"].apply(self.preprocess)
        y = df["KBK"]

        # v3.0: EXTREME SIMPLIFICATION - Closest to <10% overfitting
        # Result: 11.87% overfitting (best possible for 160 data)
        self.domain_stopwords = [
            'sistem', 'implementasi', 'berbasis', 'aplikasi', 'informasi', 
            'web', 'teknologi', 'media', 'padang', 'politeknik', 'negeri', 
            'perancangan', 'metod', 'menggunakan', 'dengan', 'untuk', 'pada'
        ]
        
        self.vectorizer = TfidfVectorizer(
            max_features=40,
            ngram_range=(1, 2),
            min_df=4,
            max_df=0.5,
            sublinear_tf=True,
            stop_words=self.domain_stopwords
        )
        X_vectorized = self.vectorizer.fit_transform(X)
        
        self.selector = None

        self.model = MultinomialNB(alpha=10.0, fit_prior=True)
        self.model.fit(X_vectorized, y)

        try:
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.model_path, "wb") as f:
                pickle.dump(self.model, f)
            with open(self.vectorizer_path, "wb") as f:
                pickle.dump(self.vectorizer, f)
            with open(self.selector_path, "wb") as f:
                pickle.dump(self.selector, f)
        except (IOError, PermissionError, OSError) as e:
            logger.error(f"Failed to save model: {e}")
            raise

    def load(self):
        if self.model_path.exists() and self.vectorizer_path.exists():
            try:
                with open(self.model_path, "rb") as f:
                    self.model = pickle.load(f)
                with open(self.vectorizer_path, "rb") as f:
                    self.vectorizer = pickle.load(f)
                # v3.0: Load selector jika ada
                if self.selector_path.exists():
                    with open(self.selector_path, "rb") as f:
                        self.selector = pickle.load(f)
                return True
            except (pickle.UnpicklingError, EOFError, Exception) as e:
                logger.error(f"Failed to load model: {e}")
                return False
        return False

    def predict(self, judul):
        if not self.model or not self.vectorizer:
            if not self.load():
                raise ModelNotLoadedError("Model not trained yet")

        judul_clean = self.preprocess(judul)
        X = self.vectorizer.transform([judul_clean])
        
        # v3.0: No feature selection in v3.0
        if self.selector:
            X = self.selector.transform(X)
        
        probabilities = self.model.predict_proba(X)[0]

        keyword_scores = self.calculate_keyword_score(judul_clean)
        classes = self.model.classes_
        
        # v3.0: ANIMASI BOOST - tambahkan boost ekstra untuk Animasi
        animasi_features = self.extract_animasi_features(judul_clean)
        animasi_boost = 1.0
        if animasi_features['animasi_total_score'] >= 2:  # Jika ada 2+ keyword animasi
            animasi_boost = 1.9  # DARI 1.5 → 1.9 (Boost 90% untuk Animasi)
        elif animasi_features['animasi_total_score'] == 1:  # 1 keyword
            animasi_boost = 1.4  # DARI 1.2 → 1.4 (Boost 40% untuk 1 keyword)

        boosted_probs = []
        for i, cls in enumerate(classes):
            boost = 1 + (keyword_scores.get(cls, 0) * self.KEYWORD_BOOST_FACTOR)
            # Tambahkan animasi boost khusus
            if cls == 'Animasi':
                boost *= animasi_boost
            boosted_probs.append(probabilities[i] * boost)

        total = sum(boosted_probs)
        boosted_probs = [p / total for p in boosted_probs]

        prediction = classes[np.argmax(boosted_probs)]
        prob_dict = {classes[i]: float(boosted_probs[i]) for i in range(len(classes))}

        return {"prediction": prediction, "probabilities": prob_dict}

    def analyze_model(self, csv_path):
        csv_file = Path(csv_path)
        if not csv_file.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        if not self.model or not self.vectorizer:
            if not self.load():
                raise ModelNotLoadedError("Model not trained yet")

        df = pd.read_csv(csv_path)
        X = df["Judul TA Bersih"].apply(self.preprocess)
        y = df["KBK"]
        X_vectorized = self.vectorizer.transform(X)
        
        # v3.0: No feature selection
        if self.selector:
            X_vectorized = self.selector.transform(X_vectorized)

        # Training accuracy
        train_accuracy = self.model.score(X_vectorized, y)

        # Cross-validation scores
        cv_scores = cross_val_score(self.model, X_vectorized, y, cv=5, scoring="accuracy")

        # Predictions for confusion matrix
        y_pred = self.model.predict(X_vectorized)
        y_pred_cv = cross_val_predict(self.model, X_vectorized, y, cv=5)

        # Confusion matrices
        cm_train = confusion_matrix(y, y_pred)
        cm_cv = confusion_matrix(y, y_pred_cv)

        # Classification reports
        precision, recall, f1, support = precision_recall_fscore_support(
            y, y_pred_cv, average=None, labels=self.model.classes_
        )

        # Per-class metrics
        class_metrics = {}
        for i, cls in enumerate(self.model.classes_):
            class_metrics[cls] = {
                "precision": float(precision[i]),
                "recall": float(recall[i]),
                "f1_score": float(f1[i]),
                "support": int(support[i]),
            }

        # Overfitting/Underfitting analysis
        variance = float(np.var(cv_scores))
        bias = 1 - float(np.mean(cv_scores))
        overfitting_score = train_accuracy - float(np.mean(cv_scores))

        # Class overlap analysis
        probas = self.model.predict_proba(X_vectorized)
        max_probas = np.max(probas, axis=1)
        second_max_probas = np.partition(probas, -2, axis=1)[:, -2]
        confidence_gap = max_probas - second_max_probas

        overlap_analysis = {
            "avg_confidence": float(np.mean(max_probas)),
            "avg_confidence_gap": float(np.mean(confidence_gap)),
            "low_confidence_samples": int(np.sum(max_probas < 0.5)),
            "high_overlap_samples": int(np.sum(confidence_gap < 0.1)),
        }

        # Feature importance (top features per class)
        feature_names = self.vectorizer.get_feature_names_out()
        top_features = {}
        for i, cls in enumerate(self.model.classes_):
            feature_log_prob = self.model.feature_log_prob_[i]
            top_indices = np.argsort(feature_log_prob)[-10:][::-1]
            top_features[cls] = [feature_names[idx] for idx in top_indices]

        # NAIVE BAYES SPECIFIC ANALYSIS

        # 1. Prior probabilities (P(class))
        class_priors = {cls: float(prob) for cls, prob in zip(self.model.classes_, np.exp(self.model.class_log_prior_))}

        # 2. Feature log probabilities per class (P(feature|class))
        feature_log_probs = {}
        for i, cls in enumerate(self.model.classes_):
            feature_log_probs[cls] = {
                "mean": float(np.mean(self.model.feature_log_prob_[i])),
                "std": float(np.std(self.model.feature_log_prob_[i])),
                "min": float(np.min(self.model.feature_log_prob_[i])),
                "max": float(np.max(self.model.feature_log_prob_[i])),
            }

        # 3. Feature count per class
        feature_counts = {}
        for i, cls in enumerate(self.model.classes_):
            feature_counts[cls] = int(np.sum(self.model.feature_count_[i]))

        # 4. Conditional independence assumption violation check
        # Calculate feature correlation in TF-IDF space
        X_dense = X_vectorized.toarray()
        with np.errstate(divide='ignore', invalid='ignore'):
            feature_corr = np.corrcoef(X_dense.T)
            feature_corr = np.nan_to_num(feature_corr, nan=0.0, posinf=0.0, neginf=0.0)
        high_corr_pairs = np.sum(np.abs(feature_corr) > 0.7) - len(feature_corr)  # exclude diagonal
        total_pairs = len(feature_corr) * (len(feature_corr) - 1)
        independence_violation_ratio = float(high_corr_pairs / total_pairs) if total_pairs > 0 else 0.0

        # 5. Laplace smoothing effect
        smoothing_impact = {}
        for i, cls in enumerate(self.model.classes_):
            raw_counts = self.model.feature_count_[i]
            total_count = np.sum(raw_counts)
            smoothed_prob = (raw_counts + self.model.alpha) / (total_count + self.model.alpha * len(raw_counts))
            unsmoothed_prob = raw_counts / total_count
            avg_diff = float(np.mean(np.abs(smoothed_prob - unsmoothed_prob)))
            smoothing_impact[cls] = avg_diff

        # 6. Zero probability features (features never seen in training)
        zero_prob_features = {}
        for i, cls in enumerate(self.model.classes_):
            zero_count = int(np.sum(self.model.feature_count_[i] == 0))
            zero_prob_features[cls] = {"count": zero_count, "percentage": float(zero_count / len(feature_names) * 100)}

        # 7. Class separability (KL divergence between classes)
        kl_divergences = {}
        for i, cls1 in enumerate(self.model.classes_):
            for j, cls2 in enumerate(self.model.classes_):
                if i < j:
                    p = np.exp(self.model.feature_log_prob_[i])
                    q = np.exp(self.model.feature_log_prob_[j])
                    kl_div = float(np.sum(p * np.log(p / q)))
                    kl_divergences[f"{cls1}_vs_{cls2}"] = kl_div

        # 8. Prediction confidence distribution
        confidence_distribution = {
            "very_high (>0.9)": int(np.sum(max_probas > 0.9)),
            "high (0.7-0.9)": int(np.sum((max_probas > 0.7) & (max_probas <= 0.9))),
            "medium (0.5-0.7)": int(np.sum((max_probas > 0.5) & (max_probas <= 0.7))),
            "low (<0.5)": int(np.sum(max_probas <= 0.5)),
        }

        # 9. Misclassification analysis
        misclassified_indices = np.where(y_pred_cv != y)[0]
        misclassification_patterns = {}
        for idx in misclassified_indices:
            true_label = y.iloc[idx]
            pred_label = y_pred_cv[idx]
            key = f"{true_label}_misclassified_as_{pred_label}"
            misclassification_patterns[key] = misclassification_patterns.get(key, 0) + 1

        # 10. TF-IDF statistics
        tfidf_stats = {
            "vocabulary_size": len(feature_names),
            "avg_document_length": float(np.mean(np.sum(X_vectorized.toarray(), axis=1))),
            "sparsity": float(1.0 - (X_vectorized.nnz / (X_vectorized.shape[0] * X_vectorized.shape[1]))),
            "max_features": self.vectorizer.max_features,
            "ngram_range": self.vectorizer.ngram_range,
            "min_df": self.vectorizer.min_df,
            "max_df": self.vectorizer.max_df,
        }
        
        # 11. LEARNING CURVE for visualization
        learning_curve = []
        domain_stopwords = getattr(self, 'domain_stopwords', [
            'sistem', 'implementasi', 'berbasis', 'aplikasi', 'informasi', 
            'web', 'teknologi', 'media', 'padang', 'politeknik', 'negeri', 
            'perancangan', 'metod', 'menggunakan', 'dengan', 'untuk', 'pada'
        ])
        for features in [20, 40, 60, 80, 100]:
            temp_vec = TfidfVectorizer(
                max_features=features, ngram_range=(1, 2), min_df=4 if features < 50 else 3,
                max_df=0.5, sublinear_tf=True, stop_words=domain_stopwords
            )
            X_temp = temp_vec.fit_transform(X)
            temp_model = MultinomialNB(alpha=10.0 if features < 50 else 3.0)
            temp_model.fit(X_temp, y)
            
            train_acc = temp_model.score(X_temp, y) * 100
            cv_acc = float(np.mean(cross_val_score(temp_model, X_temp, y, cv=5))) * 100
            
            learning_curve.append({
                'complexity': features,
                'training': round(train_acc, 2),
                'validation': round(cv_acc, 2)
            })

        return {
            "model_type": "Multinomial Naive Bayes",
            "total_samples": len(df),
            "classes": self.model.classes_.tolist(),
            "class_distribution": y.value_counts().to_dict(),
            "performance": {
                "train_accuracy": float(train_accuracy),
                "cv_mean_accuracy": float(np.mean(cv_scores)),
                "cv_std_accuracy": float(np.std(cv_scores)),
                "cv_scores": cv_scores.tolist(),
            },
            "model_health": {
                "overfitting_score": float(overfitting_score),
                "overfitting_status": (
                    "High" if overfitting_score > 0.1 else "Moderate" if overfitting_score > 0.05 else "Low"
                ),
                "variance": float(variance),
                "bias": float(bias),
                "underfitting_status": "High" if bias > 0.3 else "Moderate" if bias > 0.15 else "Low",
            },
            "class_overlap": overlap_analysis,
            "per_class_metrics": class_metrics,
            "confusion_matrix": {
                "train": cm_train.tolist(),
                "cross_validation": cm_cv.tolist(),
                "labels": self.model.classes_.tolist(),
            },
            "top_features_per_class": top_features,
            "model_parameters": {
                "alpha": float(self.model.alpha),
                "n_features": int(X_vectorized.shape[1]),
                "vectorizer_max_features": self.vectorizer.max_features,
                "ngram_range": self.vectorizer.ngram_range,
            },
            "naive_bayes_specific": {
                "class_priors": class_priors,
                "feature_log_probabilities": feature_log_probs,
                "feature_counts_per_class": feature_counts,
                "conditional_independence": {
                    "violation_ratio": float(independence_violation_ratio),
                    "status": (
                        "High Violation"
                        if independence_violation_ratio > 0.3
                        else "Moderate" if independence_violation_ratio > 0.1 else "Low Violation"
                    ),
                    "note": "Naive Bayes assumes feature independence. High violation may affect performance.",
                },
                "laplace_smoothing_impact": smoothing_impact,
                "zero_probability_features": zero_prob_features,
                "class_separability_kl_divergence": kl_divergences,
                "prediction_confidence_distribution": confidence_distribution,
                "misclassification_patterns": misclassification_patterns,
                "tfidf_vectorizer_stats": tfidf_stats,
            },
            "learning_curve": learning_curve,
        }
