from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .ml_model import NaiveBayesModel

model = NaiveBayesModel()

@api_view(['POST'])
def predict_kbk(request):
    judul = request.data.get('judul', '')
    
    if not judul:
        return Response({'error': 'Judul is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        result = model.predict(judul)
        return Response({
            'judul': judul,
            'predicted_kbk': result['prediction'],
            'probabilities': result['probabilities']
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def train_model(request):
    try:
        from pathlib import Path
        csv_path = Path(__file__).parent.parent / 'data.csv'
        model.train(str(csv_path))
        return Response({'message': 'Model trained successfully'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
