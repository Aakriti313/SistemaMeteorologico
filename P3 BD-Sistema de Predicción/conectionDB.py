import mysql.connector # type: ignore

# Conexión a la base de datos MySQL
def obtener_conexion():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="meteorologic_prediction"
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error de conexión: {err}")
        return None