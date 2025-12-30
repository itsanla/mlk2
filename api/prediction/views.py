from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle
from .ml_model import NaiveBayesModel, ModelNotLoadedError
from .model_manager import ModelManager
from .redis_client import RedisHistoryManager
import logging
import threading

logger = logging.getLogger(__name__)
model = NaiveBayesModel()
model_manager = ModelManager()
history_manager = RedisHistoryManager()
training_lock = threading.Lock()

# Migrate legacy model on startup
try:
    model_manager.migrate_legacy_model()
except Exception as e:
    logger.warning(f"Legacy model migration skipped: {e}")


@api_view(["POST"])
@throttle_classes([AnonRateThrottle])
def predict_kbk(request):
    judul = request.data.get("judul", "")
    model_version = request.data.get("model_version")  # Optional
    session_id = request.data.get("session_id")  # Optional for history

    if not judul:
        return Response({"error": "Judul is required"}, status=status.HTTP_400_BAD_REQUEST)

    if not isinstance(judul, str):
        return Response({"error": "Judul must be a string"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Use specified version or latest
        if not model_version:
            model_version = model_manager.get_latest_version()
            if not model_version:
                # Fallback to legacy model
                result = model.predict(judul)
                response_data = {
                    "judul": judul,
                    "predicted_kbk": result["prediction"],
                    "probabilities": result["probabilities"],
                    "model_version": "legacy"
                }
                return Response(response_data)
        
        # Load versioned model
        model_data = model_manager.load_model(model_version)
        model.model = model_data['model']
        model.vectorizer = model_data['vectorizer']
        model.selector = model_data['selector']
        
        result = model.predict(judul)
        
        response_data = {
            "judul": judul,
            "predicted_kbk": result["prediction"],
            "probabilities": result["probabilities"],
            "model_version": model_version
        }
        
        # Save to history if session_id provided
        if session_id:
            try:
                history_manager.add_history(session_id, response_data)
            except Exception as e:
                logger.warning(f"Failed to save history: {e}")
        
        return Response(response_data)
        
    except FileNotFoundError as e:
        logger.error(f"Model not found: {e}")
        return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
    except ModelNotLoadedError:
        logger.error("Model not loaded")
        return Response({"error": "Model not available"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return Response({"error": "An error occurred during prediction"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def train_model(request):
    try:
        from pathlib import Path

        csv_path = Path(__file__).parent.parent / "data.csv"
        bump_type = request.data.get("bump_type", "patch")  # major, minor, patch
        model_name = request.data.get("name", "MLK2 Model")
        description = request.data.get("description", "")

        with training_lock:
            # Train model
            model.train(str(csv_path))
            
            # Get analysis for metadata
            analysis = model.analyze_model(str(csv_path))
            
            # Calculate next version
            new_version = model_manager.get_next_version(bump_type)
            
            # Save versioned model
            metadata = {
                'name': model_name,
                'description': description,
                'accuracy': analysis['performance']['train_accuracy'],
                'cv_accuracy': analysis['performance']['cv_mean_accuracy'],
                'overfitting_score': analysis['model_health']['overfitting_score'],
                'total_samples': analysis['total_samples']
            }
            
            model_manager.save_model(
                model.model,
                model.vectorizer,
                model.selector,
                new_version,
                metadata
            )

        return Response({
            "message": "Model trained successfully",
            "version": new_version,
            "metadata": metadata
        })
    except FileNotFoundError as e:
        logger.error(f"Training file not found: {e}")
        return Response({"error": "Training data not found"}, status=status.HTTP_404_NOT_FOUND)
    except ValueError as e:
        logger.error(f"Training data validation error: {e}")
        return Response({"error": "Invalid training data format"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Training error: {e}")
        return Response({"error": "An error occurred during training"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def analyze_model(request):
    try:
        from pathlib import Path

        csv_path = Path(__file__).parent.parent / "data.csv"
        model_version = request.query_params.get("model_version")
        
        # Load specific version if requested
        if model_version:
            model_data = model_manager.load_model(model_version)
            model.model = model_data['model']
            model.vectorizer = model_data['vectorizer']
            model.selector = model_data['selector']

        analysis = model.analyze_model(str(csv_path), model_version=model_version)
        analysis['model_version'] = model_version or 'current'
        return Response(analysis)
    except FileNotFoundError as e:
        logger.error(f"Model or data not found: {e}")
        return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
    except ModelNotLoadedError:
        logger.error("Model not loaded for analysis")
        return Response(
            {"error": "Model not available. Please train the model first."}, status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return Response({"error": "An error occurred during analysis"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def list_models(request):
    """List all available model versions"""
    try:
        models = model_manager.list_models()
        return Response({
            "models": models,
            "total": len(models),
            "latest": model_manager.get_latest_version()
        })
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return Response({"error": "Failed to list models"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def get_history(request):
    """Get prediction history for session"""
    session_id = request.query_params.get("session_id")
    
    if not session_id:
        return Response({"error": "session_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        limit = int(request.query_params.get("limit", 50))
        history = history_manager.get_history(session_id, limit)
        return Response({
            "session_id": session_id,
            "history": history,
            "count": len(history)
        })
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return Response({"error": "Failed to get history"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def clear_history(request):
    """Clear all history for session"""
    session_id = request.data.get("session_id")
    
    if not session_id:
        return Response({"error": "session_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        count = history_manager.clear_history(session_id)
        return Response({
            "message": "History cleared",
            "deleted_count": count
        })
    except Exception as e:
        logger.error(f"Error clearing history: {e}")
        return Response({"error": "Failed to clear history"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["DELETE"])
def delete_history_item(request, history_id):
    """Delete specific history item"""
    session_id = request.query_params.get("session_id")
    
    if not session_id:
        return Response({"error": "session_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        success = history_manager.delete_history(session_id, history_id)
        if success:
            return Response({"message": "History item deleted"})
        else:
            return Response({"error": "History item not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error deleting history: {e}")
        return Response({"error": "Failed to delete history"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def health_check(request):
    """Health check for Redis and models"""
    redis_status = history_manager.health_check()
    models_count = len(model_manager.list_models())
    
    return Response({
        "status": "healthy" if redis_status else "degraded",
        "redis": "connected" if redis_status else "disconnected",
        "models_available": models_count
    })
