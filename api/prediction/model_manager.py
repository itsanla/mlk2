import pickle
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class ModelManager:
    """Manage multiple ML model versions"""
    
    def __init__(self):
        self.models_dir = Path(__file__).parent / "models"
        self.models_dir.mkdir(exist_ok=True)
        self.cache = {}  # Cache for loaded models
        self.cache_size = 3
    
    def get_model_path(self, version: str) -> Path:
        """Get path to model directory"""
        return self.models_dir / f"mlk2-{version}"
    
    def list_models(self) -> List[Dict]:
        """List all available models with metadata"""
        models = []
        for model_dir in sorted(self.models_dir.iterdir()):
            if model_dir.is_dir() and model_dir.name.startswith("mlk2-"):
                metadata_file = model_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                        models.append(metadata)
        
        # Sort by version (semantic versioning)
        models.sort(key=lambda x: [int(v) for v in x['version'].split('.')], reverse=True)
        return models
    
    def get_latest_version(self) -> Optional[str]:
        """Get latest model version"""
        models = self.list_models()
        return models[0]['version'] if models else None
    
    def load_model(self, version: str) -> Dict:
        """Load model by version with caching"""
        if version in self.cache:
            return self.cache[version]
        
        model_path = self.get_model_path(version)
        if not model_path.exists():
            raise FileNotFoundError(f"Model version {version} not found")
        
        model_file = model_path / "model.pkl"
        vectorizer_file = model_path / "vectorizer.pkl"
        selector_file = model_path / "selector.pkl"
        
        if not model_file.exists() or not vectorizer_file.exists():
            raise FileNotFoundError(f"Model files incomplete for version {version}")
        
        with open(model_file, 'rb') as f:
            model = pickle.load(f)
        with open(vectorizer_file, 'rb') as f:
            vectorizer = pickle.load(f)
        
        selector = None
        if selector_file.exists():
            with open(selector_file, 'rb') as f:
                selector = pickle.load(f)
        
        model_data = {
            'model': model,
            'vectorizer': vectorizer,
            'selector': selector,
            'version': version
        }
        
        # Cache management (LRU)
        if len(self.cache) >= self.cache_size:
            oldest = next(iter(self.cache))
            del self.cache[oldest]
        
        self.cache[version] = model_data
        logger.info(f"Loaded model version {version}")
        return model_data
    
    def save_model(self, model, vectorizer, selector, version: str, metadata: Dict):
        """Save new model version"""
        model_path = self.get_model_path(version)
        model_path.mkdir(parents=True, exist_ok=True)
        
        # Save model files
        with open(model_path / "model.pkl", 'wb') as f:
            pickle.dump(model, f)
        with open(model_path / "vectorizer.pkl", 'wb') as f:
            pickle.dump(vectorizer, f)
        with open(model_path / "selector.pkl", 'wb') as f:
            pickle.dump(selector, f)
        
        # Save metadata
        metadata.update({
            'version': version,
            'created_at': datetime.now().isoformat(),
            'model_path': str(model_path)
        })
        
        with open(model_path / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Saved model version {version}")
        return metadata
    
    def get_next_version(self, bump_type: str = 'patch') -> str:
        """Calculate next version number"""
        latest = self.get_latest_version()
        
        if not latest:
            return "1.0.0"
        
        major, minor, patch = map(int, latest.split('.'))
        
        if bump_type == 'major':
            return f"{major + 1}.0.0"
        elif bump_type == 'minor':
            return f"{major}.{minor + 1}.0"
        else:  # patch
            return f"{major}.{minor}.{patch + 1}"
    
    def migrate_legacy_model(self):
        """Migrate old model.pkl to versioned structure"""
        legacy_model = Path(__file__).parent / "model.pkl"
        legacy_vectorizer = Path(__file__).parent / "vectorizer.pkl"
        legacy_selector = Path(__file__).parent / "selector.pkl"
        
        if legacy_model.exists() and not self.list_models():
            logger.info("Migrating legacy model to version 1.0.0")
            
            with open(legacy_model, 'rb') as f:
                model = pickle.load(f)
            with open(legacy_vectorizer, 'rb') as f:
                vectorizer = pickle.load(f)
            
            selector = None
            if legacy_selector.exists():
                with open(legacy_selector, 'rb') as f:
                    selector = pickle.load(f)
            
            metadata = {
                'name': 'MLK2 Initial Model',
                'description': 'Migrated from legacy model.pkl',
                'accuracy': 0.0,
                'cv_accuracy': 0.0
            }
            
            self.save_model(model, vectorizer, selector, "1.0.0", metadata)
            logger.info("Migration completed")
