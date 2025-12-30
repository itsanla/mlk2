from django.urls import path
from . import views

urlpatterns = [
    path("predict/", views.predict_kbk, name="predict_kbk"),
    path("train/", views.train_model, name="train_model"),
    path("analyze/", views.analyze_model, name="analyze_model"),
    path("models/", views.list_models, name="list_models"),
    path("history/", views.get_history, name="get_history"),
    path("history/clear/", views.clear_history, name="clear_history"),
    path("history/<str:history_id>/", views.delete_history_item, name="delete_history_item"),
    path("health/", views.health_check, name="health_check"),
]
