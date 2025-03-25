import pika
import sys

def cancelar_voto(hostname, port, id_voto): 

    try:
        # 1: Crear una conexión con el servidor RabbitMQ
        
        credentials = pika.PlainCredentials('alumnomq', 'alumnomq')
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=hostname, port=port, credentials=credentials))
        channel = connection.channel()

    except Exception as e:
        print("Error al conectar al host remoto: ")
        exit()

    # 2: Crear una cola de mensajes
    if channel.queue_declare(queue='voto_cancelacion'):
        print("Cola de mensajes creada con éxito")


    # 3: Envío de mensaje
    channel.basic_publish(exchange='', routing_key='voto_cancelacion', body=id_voto)

    # Por último, cerramos la conexión
    channel.close()


def main():

    if len(sys.argv) != 4:
        print("Debe indicar el host, el numero de puerto, y el ID del voto a cancelar como un argumento.")
        exit()

    cancelar_voto(sys.argv[1], sys.argv[2], sys.argv[3])

if __name__ == "__main__":
    main()
