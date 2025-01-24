from django.db import connection
from django.shortcuts import render
from django.http import JsonResponse
import joblib
import pandas as pd
import numpy as np

# Rutas a tu modelo y scaler
MODEL_PATH = 'app/ml_models/svm_model1M3.pkl'
SCALER_PATH = 'app/ml_models/scaler2.pkl'

# Cargamos el scaler (MinMaxScaler) y el modelo entrenado
scaler = joblib.load(SCALER_PATH)
modelo = joblib.load(MODEL_PATH)

# Diccionario de mapeo para la predicción (numérico -> texto)
WEATHER_MAPPING = {
    1: "Rain",
    2: "Storm",
    3: "Cloudy",
    4: "Fog",
    5: "Sun"
}

# Orden EXACTO de columnas que el modelo espera
final_cols = [
    'temp_max',       # num
    'cloudiness_id',  # cat
    'precipitation',  # num
    'wind',           # num
    'visibility',     # num
    'humidity',       # num
    'season_id',      # cat
    'solar_radiation' # num
]

# Separación de columnas numéricas y categóricas
# (en el ORDEN en que deben aparecer en 'final_cols')
numerical_cols = [
    'solar_radiation', 'wind', 'visibility', 'temp_max', 'precipitation', 'humidity'
]

def landing_view(request):
    return render(request, 'app/index.html', {'active_page': 'index'})

def consultas_view(request):
    return render(request, 'app/consultas.html', {'active_page': 'consultas'})

def predict_weather(request):
    """
    Vista para recibir los valores del formulario y predecir con el modelo SVM.
    """
    if request.method == 'POST':
        try:
            # 1) Obtener datos del request.POST
            data = request.POST
            temp_max        = float(data.get('temp_max', 0))
            cloudiness_id   = int(data.get('cloudiness_description'))
            precipitation   = float(data.get('precipitation', 0))
            wind            = float(data.get('wind', 0))
            visibility      = float(data.get('visibility', 0))
            humidity        = float(data.get('humidity', 0))
            season_id       = int(data.get('season_description'))
            solar_radiation = float(data.get('solar_radiation', 0))

            # 2) Construir DataFrame con las columnas en el ORDEN FINAL
            X = pd.DataFrame([[
                temp_max,
                cloudiness_id,
                precipitation,
                wind,
                visibility,
                humidity,
                season_id,
                solar_radiation
            ]], columns=final_cols)

            print("nummmmmmmmmmm: ", X[numerical_cols])
            X[numerical_cols] = scaler.transform(X[numerical_cols])
            
            print(X)


            # 6) Predicción con el modelo
            prediction = modelo.predict(X)[0]
            prediction_text = WEATHER_MAPPING.get(int(prediction), "Unknown")

            # 7) Devolvemos JSON con la predicción
            return JsonResponse({'prediction': prediction_text})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def mi_vista(request):
    """
    Otra vista que realiza una consulta en BD y devuelve un JSON
    """
    if request.method == 'GET':
        try:
            consulta = "SELECT * FROM v_observations"
            parametros = []
            filtros = []

            # Filtros en la query
            weather_filter = request.GET.get('weather')
            if weather_filter:
                filtros.append("weather_name LIKE %s")
                parametros.append(f"%{weather_filter}%")

            season_filter = request.GET.get('season')
            if season_filter:
                filtros.append("season_name = %s")
                parametros.append(season_filter)

            cloudiness_filter = request.GET.get('cloudiness')
            if cloudiness_filter:
                filtros.append("cloudiness_name = %s")
                parametros.append(cloudiness_filter)

            if filtros:
                consulta += " WHERE " + " AND ".join(filtros)

            consulta += " LIMIT 20"

            with connection.cursor() as cursor:
                cursor.execute(consulta, parametros)
                resultados = cursor.fetchall()
                columnas = [col[0] for col in cursor.description]
                resultados_serializados = [dict(zip(columnas, fila)) for fila in resultados]

            return JsonResponse({'resultados': resultados_serializados})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
