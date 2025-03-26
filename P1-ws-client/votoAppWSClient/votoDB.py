import requests
from django.conf import settings

# Verificar si el votante está en el censo
def verificar_censo(censo_data):
    try:
        api_url = settings.RESTAPIBASEURL + 'censo/'
        response = requests.post(api_url, json=censo_data)
        # Si el código es 200 o 302, consideramos que el censo es válido.
        if response.status_code in (200, 302):
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error en verificar_censo: {e}")
        return False

def registrar_voto(voto_dict):
    """Register a vote in the API REST."""
    try:
        api_url = settings.RESTAPIBASEURL + 'voto/'
        response = requests.post(api_url, json=voto_dict)
        response.raise_for_status()  # Lanza una excepción si el código de respuesta es 4xx o 5xx
        
        if response.status_code in (200, 201):
            return response.json()  # Devolver el JSON si la creación fue exitosa
        else:
            print(f"Error en registrar voto: {response.status_code}")
            return None  # Retornar None si la respuesta no es exitosa
    except requests.exceptions.RequestException as e:
        print(f"Error en registrar_voto: {e}")
        return None

# Eliminar un voto a través de la API REST
def eliminar_voto(idVoto):
    """Delete a vote from the API."""
    try:
        api_url = settings.RESTAPIBASEURL + f'voto/{idVoto}/'
        response = requests.delete(api_url)
        response.raise_for_status()
        
        # Acepta 200 o 204 como operación exitosa
        return response.status_code in (200, 204)
    except requests.exceptions.RequestException as e:
        print(f"Error en eliminar_voto: {e}")
        return False

# Obtener votos de un proceso electoral desde la API REST
def get_votos_from_db(idProcesoElectoral):
    """Gets votes from the API REST corresponding to some electoral process."""
    try:
        api_url = settings.RESTAPIBASEURL + 'voto/'
        response = requests.get(api_url, params={'idProcesoElectoral': idProcesoElectoral})
        response.raise_for_status()
        
        return response.json() if response.status_code == 200 else []
    except requests.exceptions.RequestException as e:
        print(f"Error en get_votos_from_db: {e}")
        return []
    


