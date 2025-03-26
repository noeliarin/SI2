import requests
from django.conf import settings
from rest_framework import status


def verificar_censo(censo_data):
    """ Function to verify if a voter is registered in the database"""
    if bool(censo_data) is False:
        return False
    path = f"{settings.RESTAPIBASEURL}censo/"
    response = requests.post(path, json=censo_data)
    if response.status_code == status.HTTP_200_OK:
        return True
    print(f"Error: Verificando censo: status code {response.status_code}")
    return False


def registrar_voto(voto_dict):
    """ Function to register a vote in the database"""
    path = f"{settings.RESTAPIBASEURL}voto/"
    response = requests.post(path, json=voto_dict)
    if response.status_code == status.HTTP_200_OK:
        return response.json()
    print(f"Error: Registrando voto: status code {response.status_code}")
    return None


def eliminar_voto(idVoto):
    """ Function to delete a vote from the database """
    path = f"{settings.RESTAPIBASEURL}voto/{idVoto}/"
    response = requests.delete(path)
    if response.status_code == status.HTTP_200_OK:
        return True
    print(f"Error: Eliminando voto: status code {response.status_code}")
    return False


def get_votos_from_db(idProcesoElectoral):
    """ Function to get votes from the database """
    path = f"{settings.RESTAPIBASEURL}procesoelectoral/{idProcesoElectoral}/"
    response = requests.get(path)
    if response.status_code == status.HTTP_200_OK:
        return response.json()
    print(f"Error: Obteniendo votos de la base de datos: status code {response.status_code}")
    return []