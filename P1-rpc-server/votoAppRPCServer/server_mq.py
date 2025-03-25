# Uses rabbitMQ as the server

import os
import sys
import django
import pika

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'votoSite.settings')
django.setup()

from votoAppRPCServer.models import Censo, Voto

def main():

    if len(sys.argv) != 3:
        print("Debe indicar el host y el puerto")
        exit()

    hostname = sys.argv[1]
    port = sys.argv[2]

    # 1: Crear una conexión conel servidor RabbitMQ

    # se crean las credenciales con nombre y contraseña especificados
    credentials = pika.PlainCredentials('alumnomq', 'alumnomq')

    # se crea la conexión con el host y puerto recibidos como argumentos
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=hostname, port=port, credentials=credentials))
    
    # se crea el canal de comunicación
    channel = connection.channel()


    # 2: Crear una cola de mensajes:
    channel.queue_declare(queue='voto_cancelacion')
    
    # 3: Crear y registrar función Callback
    def callback(ch, method, properties, body):    
        voto_id_string= body.decode('utf-8')
        print(f" [x] Received {body}")


        try:
            # se busca el voto con el id recibido
            voto_id= int(voto_id_string)
            voto= Voto.objects.get(id= voto_id)
            # actualizamos el voto a '111'
            voto.codigoRespuesta= '111'
            voto.save()

            #eliminamos el voto
            voto.delete()

            print(f" [:)] Voto con id {voto_id} actualizado a '111' y eliminado")
            response = f"Voto con id {voto_id} cancelado correctamente"

        except ValueError:
            print(f" [!] Error: voto_id '{voto_id_string}' no es un número válido")
            response = f"Error: voto_id '{voto_id_string}' no es un número válido"

        except Voto.DoesNotExist:
            print(f" [:(] Voto con id {voto_id} no encontrado")
            response = f"Error: voto con id {voto_id} no encontrado"

    # 4:Registrar función de callback y comienzo de consumo de mensajes:
    # registramos la función de callback
    channel.basic_consume(queue='voto_cancelacion', on_message_callback=callback, auto_ack=True)
    
    print(' [*] Waiting for messages. To exit press CTRL+C')
    # consumo de mensajes
    channel.start_consuming()
       
if __name__ == '__main__':

    main()
