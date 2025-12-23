from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle
from .ml_model import NaiveBayesModel, ModelNotLoadedError
import logging
import threading

logger = logging.getLogger(__name__)
model = NaiveBayesModel()
training_lock = threading.Lock()


@api_view(["POST"])
@throttle_classes([AnonRateThrottle])
def predict_kbk(request):
    judul = request.data.get("judul", "")

    if not judul:
        return Response({"error": "Judul is required"}, status=status.HTTP_400_BAD_REQUEST)

    if not isinstance(judul, str):
        return Response({"error": "Judul must be a string"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        result = model.predict(judul)
        return Response(
            {"judul": judul, "predicted_kbk": result["prediction"], "probabilities": result["probabilities"]}
        )
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

        with training_lock:
            model.train(str(csv_path))

        return Response({"message": "Model trained successfully"})
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

        analysis = model.analyze_model(str(csv_path))
        return Response(analysis)
    except ModelNotLoadedError:
        logger.error("Model not loaded for analysis")
        return Response(
            {"error": "Model not available. Please train the model first."}, status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except FileNotFoundError as e:
        logger.error(f"Analysis data not found: {e}")
        return Response({"error": "Training data not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return Response({"error": "An error occurred during analysis"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
