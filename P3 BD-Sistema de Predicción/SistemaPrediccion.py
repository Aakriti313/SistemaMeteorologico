from conectionDB import obtener_conexion
import pandas as pd # type: ignore
import statsmodels.api as sm # type: ignore
from sklearn.model_selection import train_test_split # type: ignore
from sklearn.metrics import mean_squared_error, r2_score # type: ignore

# Obtener la conexión a la base de datos
def cargar_datos():
    conn = obtener_conexion()
    if conn is None:
        return None

    query = """ SELECT * FROM v_observations"""

    observations_df = pd.read_sql(query, conn)
    conn.close()
    return observations_df
    


# Cargar los datos desde la base de datos
observations_cleaned_df = cargar_datos()

# Verificar si los datos fueron cargados correctamente
if observations_cleaned_df is not None:
    # 1. Definir variables dependientes e independientes para la regresión
    X = observations_cleaned_df[['temp_max', 'temp_min', 'wind', 'humidity', 'pressure', 'solar_radiation', 'visibility', 'weather_id', 'cloudiness_id', 'season_id']]
    y = observations_cleaned_df['precipitation']

    # 2. Agregar la constante para el modelo (intercepto)
    X = sm.add_constant(X)

    # 3. Dividir en conjuntos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 4. Ajustar el modelo de regresión lineal
    model = sm.OLS(y_train, X_train).fit()

    # 5. Ver los resultados
    print(model.summary())

    # 6. Predicciones
    y_pred = model.predict(X_test)

    # 7. Evaluar el modelo
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print("MSE:", mse)
    print("R2:", r2)
else:
    print("No se pudo cargar los datos desde la base de datos.")