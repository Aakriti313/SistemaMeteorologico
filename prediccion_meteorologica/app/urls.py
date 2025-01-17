# app/urls.py
from django.urls import path
from .views import landing_view, predict_weather

urlpatterns = [
    path('', landing_view, name='index'),
    path('predict/', predict_weather, name='predict_weather'),  # Ruta para la página de inicio de la app
]
