from django.urls import path
from . import views

urlpatterns = [
    path("predict/", views.predict_kbk, name="predict_kbk"),
    path("train/", views.train_model, name="train_model"),
    path("analyze/", views.analyze_model, name="analyze_model"),
]
