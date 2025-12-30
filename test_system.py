#!/usr/bin/env python3

import requests
import json
import sys
import os

# Add Django project to path
sys.path.append('/media/anla/DATA_B/project/SEMESTER5/matkul-machine-learning/mlk2/api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from prediction.redis_client import RedisHistoryManager
from prediction.model_manager import ModelManager

def test_redis_connection():
    """Test Redis container connection"""
    print("🔍 Testing Redis connection...")
    try:
        history_manager = RedisHistoryManager()
        result = history_manager.health_check()
        print(f"✅ Redis connection: {'OK' if result else 'FAILED'}")
        return result
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def test_model_manager():
    """Test model manager"""
    print("\n🤖 Testing Model Manager...")
    try:
        mm = ModelManager()
        models = mm.list_models()
        print(f"✅ Found {len(models)} models:")
        for model in models:
            print(f"   - v{model['version']}: {model['name']}")
        return True
    except Exception as e:
        print(f"❌ Model manager failed: {e}")
        return False

def test_history_operations():
    """Test history CRUD operations"""
    print("\n📜 Testing History operations...")
    try:
        history_manager = RedisHistoryManager()
        session_id = "test-session-123"
        
        # Add test history
        test_data = {
            "judul": "Test implementasi naive bayes",
            "predicted_kbk": "AI / Machine Learning",
            "probabilities": {"AI / Machine Learning": 0.8, "Software": 0.2},
            "model_version": "1.0.0"
        }
        
        history_id = history_manager.add_history(session_id, test_data)
        print(f"✅ Added history: {history_id}")
        
        # Get history
        history = history_manager.get_history(session_id)
        print(f"✅ Retrieved {len(history)} history items")
        
        # Clear history
        count = history_manager.clear_history(session_id)
        print(f"✅ Cleared {count} history items")
        
        return True
    except Exception as e:
        print(f"❌ History operations failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\n🌐 Testing API endpoints...")
    base_url = "http://localhost:8000/api"
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check: {data['status']}")
            print(f"   Redis: {data['redis']}")
            print(f"   Models: {data['models_available']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
        # Test models list
        response = requests.get(f"{base_url}/models/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Models endpoint: {data['total']} models")
        else:
            print(f"❌ Models endpoint failed: {response.status_code}")
            
        return True
    except requests.exceptions.ConnectionError:
        print("❌ API server not running. Start with: python manage.py runserver")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 MLK2 Multi-Model System Test\n")
    
    redis_ok = test_redis_connection()
    model_ok = test_model_manager()
    history_ok = test_history_operations() if redis_ok else False
    api_ok = test_api_endpoints()
    
    print(f"\n📊 Test Results:")
    print(f"   Redis: {'✅' if redis_ok else '❌'}")
    print(f"   Models: {'✅' if model_ok else '❌'}")
    print(f"   History: {'✅' if history_ok else '❌'}")
    print(f"   API: {'✅' if api_ok else '❌'}")
    
    if all([redis_ok, model_ok, history_ok]):
        print(f"\n🎉 Backend ready! Start server with:")
        print(f"   cd api && . venv/bin/activate && python manage.py runserver")
    else:
        print(f"\n⚠️  Some components failed. Check logs above.")