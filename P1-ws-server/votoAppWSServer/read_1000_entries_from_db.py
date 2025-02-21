# connect to the database, read the first 1000 entries
# then perform 1000 queries retrieving each one of the entries
# one by one. Measure the time requiered for the 1000 queries
#
#import psycopg2
#import time
#
## Configuracion de la base de datos
#db_config = {
#    'dbname': 'voto',  # Nombre de la base de datos
#    'user': 'voto_owner',  # Reemplaza con tu usuario de PostgreSQL
#    'password': 'npg_YksxB1dlch0j',  # Reemplaza con tu contrasegna
#    'host': 'ep-divine-cloud-a89rnswt-pooler.eastus2.azure.neon.tech',  # Cambia si el host es diferente
#    'port': 5432,  # Cambia si tu puerto es diferente
#}
#
#try:
#    # Conexion a la base de datos
#    conn = psycopg2.connect(**db_config)
#    cursor = conn.cursor()
#
#    # Leer las primeras 1000 entradas de la tabla censo
#    query_fetch_1000 = "SELECT * FROM censo LIMIT 1000"
#    cursor.execute(query_fetch_1000)
#    rows = cursor.fetchall()
#
#    # Preparar para las busquedas individuales
#    search_query = 'SELECT * FROM censo WHERE "numeroDNI" = %s'  # Asumiendo que hay una columna 'id' para identificar las filas
#
#    # Medir el tiempo de inicio
#    start_time = time.time()
#
#    # Realizar busquedas una a una
#    for row in rows:
#        id_value = row[0]  # Suponiendo que la primera columna es el ID
#        cursor.execute(search_query, (id_value,))
#        cursor.fetchone()  # Obtener la fila encontrada
#
#    # Medir el tiempo de finalizacion
#    end_time = time.time()
#
#    # Mostrar los resultados
#    print(f"Tiempo invertido en buscar las 1000 entradas una a una: {end_time - start_time:.6f} segundos")
#
#except Exception as e:
#    print(f"Error: {e}")
#
#finally:
#    # Cerrar el cursor y la conexion
#    if 'cursor' in locals():
#        cursor.close()
#    if 'conn' in locals():
#        conn.close()
#
import time
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "votoSite.settings")  
django.setup()

from votoAppWSServer.models import Voto

try:
    # Leer las primeras 1000 entradas de la tabla 'Voto'
    rows = Voto.objects.all()[:1000]  

    # Medir el tiempo inicio
    start_time = time.time()

    for row in rows:
        id_value = row.censo.numeroDNI  # Accedemos al 'numeroDNI' a través de la relación 'censo'
        Voto.objects.get(censo__numeroDNI=id_value)  # Hacemos la búsqueda usando 'censo__numeroDNI'

    end_time = time.time()

    print(f"Tiempo invertido en buscar las 1000 entradas una a una con ORM: {end_time - start_time:.6f} segundos")

except Exception as e:
    print(f"Error: {e}")
