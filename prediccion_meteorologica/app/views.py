from django.shortcuts import render
from django.http import JsonResponse
import joblib

# Ruta del modelo
MODEL_PATH = 'app/ml_models/svm_model1M2.pkl'

# Cargar el modelo
modelo = joblib.load(MODEL_PATH)

# Diccionario de mapeo para la predicción
WEATHER_MAPPING = {
    1: "Rain",
    2: "Storm",
    3: "Cloudy",
    4: "Fog",
    5: "Sun"
}

def landing_view(request):
    return render(request, 'app/index.html')

def predict_weather(request):
    if request.method == 'POST':
        try:
            # Obtén los datos enviados por el usuario
            data = request.POST
            precipitation = float(data.get('precipitation', 0))
            temp_max = float(data.get('temp_max', 0))
            wind = float(data.get('wind', 0))
            humidity = float(data.get('humidity', 0))
            solar_radiation = float(data.get('solar_radiation', 0))
            visibility = float(data.get('visibility', 0))
            cloudiness_id = int(data.get('cloudiness_description'))
            season_id = int(data.get('season_description'))


            # Construye el array de entrada
            input_data = [[
                solar_radiation, wind, visibility, temp_max, season_id, precipitation, humidity, cloudiness_id
            ]]
            print(input_data)
            # Realiza la predicción
            prediction = modelo.predict(input_data)[0]  # Obtén la predicción

            # Obtén la descripción asociada a la predicción
            prediction_text = WEATHER_MAPPING.get(int(prediction), "Unknown")

            # Devuelve la descripción en lugar del número
            print(prediction_text, prediction)
            print(modelo.predict(input_data))
            return JsonResponse({'prediction': prediction_text})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
