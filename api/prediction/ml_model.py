import pandas as pd
import pickle
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from pathlib import Path

class NaiveBayesModel:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.model_path = Path(__file__).parent / 'model.pkl'
        self.vectorizer_path = Path(__file__).parent / 'vectorizer.pkl'
        
        self.keywords = {
            'AI / Machine Learning': ['naive bayes', 'machine learning', 'neural', 'prediksi', 'klasifikasi', 'algoritma', 'knn', 'decision', 'clustering', 'data mining', 'deep learning', 'ai', 'saw', 'ahp', 'smart', 'topsis', 'spk', 'keputusan', 'rekomendasi'],
            'Jaringan': ['jaringan', 'network', 'server', 'mikrotik', 'router', 'firewall', 'monitoring', 'iot', 'sensor', 'esp', 'nodemcu', 'mqtt', 'wireless', 'wifi', 'keamanan jaringan'],
            'Animasi': ['augmented reality', 'virtual reality', 'ar', 'vr', '3d', 'animasi', 'visualisasi', 'ui ux', 'design', 'markerless', 'unity', 'blender', 'interaktif', 'media pembelajaran'],
            'Software': ['android', 'mobile', 'web', 'api', 'rest', 'cloud', 'aws', 'docker', 'laravel', 'react', 'flutter', 'codeigniter', 'framework', 'database', 'crud', 'aplikasi']
        }
    
    def preprocess(self, text):
        text = text.lower()
        text = re.sub(r'naã¯v\s*baiy?', 'naive bayes', text)
        text = re.sub(r'augment\s*realiti', 'augmented reality', text)
        text = re.sub(r'virtual\s*realiti', 'virtual reality', text)
        text = re.sub(r'komput', 'komputer', text)
        text = re.sub(r'berbasi', 'berbasis', text)
        text = re.sub(r'teknolog', 'teknologi', text)
        text = re.sub(r'uiux|ui/ux', 'ui ux', text)
        return text
    
    def calculate_keyword_score(self, text):
        scores = {}
        for category, keywords in self.keywords.items():
            score = sum(1 for kw in keywords if kw in text)
            scores[category] = score
        return scores
        
    def train(self, csv_path):
        df = pd.read_csv(csv_path)
        X = df['Judul TA Bersih'].apply(self.preprocess)
        y = df['KBK']
        
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 3),
            min_df=2,
            max_df=0.8,
            sublinear_tf=True
        )
        X_vectorized = self.vectorizer.fit_transform(X)
        
        self.model = MultinomialNB(alpha=0.1)
        self.model.fit(X_vectorized, y)
        
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        with open(self.vectorizer_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
    
    def load(self):
        if self.model_path.exists() and self.vectorizer_path.exists():
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            with open(self.vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            return True
        return False
    
    def predict(self, judul):
        if not self.model or not self.vectorizer:
            if not self.load():
                raise Exception("Model not trained yet")
        
        judul_clean = self.preprocess(judul)
        X = self.vectorizer.transform([judul_clean])
        probabilities = self.model.predict_proba(X)[0]
        
        keyword_scores = self.calculate_keyword_score(judul_clean)
        classes = self.model.classes_
        
        boosted_probs = []
        for i, cls in enumerate(classes):
            boost = 1 + (keyword_scores.get(cls, 0) * 0.15)
            boosted_probs.append(probabilities[i] * boost)
        
        total = sum(boosted_probs)
        boosted_probs = [p / total for p in boosted_probs]
        
        prediction = classes[np.argmax(boosted_probs)]
        prob_dict = {classes[i]: float(boosted_probs[i]) for i in range(len(classes))}
        
        return {
            'prediction': prediction,
            'probabilities': prob_dict
        }
