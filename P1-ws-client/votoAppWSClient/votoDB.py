import requests
from django.conf import settings

# Verificar si el votante está en el censo
def verificar_censo(censo_data):
    """Check if the voter is registered in the Censo."""
    try:
        api_url = settings.RESTAPIBASEURL + 'censo/'
        # Usamos POST y enviamos el payload en formato JSON
        response = requests.post(api_url, json=censo_data)
        response.raise_for_status()

        data_response = response.json()
        return bool(data_response)
    except requests.exceptions.RequestException as e:
        print(f"Error en verificar_censo: {e}")
        return False

# Registrar un voto en la API REST
def registrar_voto(voto_dict):
    """Register a vote in the API REST."""
    try:
        api_url = settings.RESTAPIBASEURL + 'voto/'
        response = requests.post(api_url, json=voto_dict)
        response.raise_for_status()

        if response.status_code in (200, 201):
            return response.json()
        else:
            return None
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

