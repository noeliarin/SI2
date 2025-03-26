# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# author: rmarabini
"Interface with the dataabse"
from votoAppWSServer.models import Censo, Voto


def verificar_censo(censo_data):
    """ Check if the voter is registered in the Censo
    :param censo_dict: dictionary with the voter data
                       (as provided by CensoForm)
    :return True or False if censo_data is not valid
    """
    if bool(censo_data) is False or not\
       Censo.objects.filter(**censo_data).exists():
        return False
    return True


def registrar_voto(voto_dict):
    """ Register a vote in the database
    :param voto_dict: dictionary with the vote data (as provided by VotoForm)
      plus de censo_id (numeroDNI) of the voter
    :return new voto info if succesful, None otherwise
    """
    try:
        voto = Voto.objects.create(**voto_dict)
        # get default values from voto
        voto = Voto.objects.get(pk=voto.pk)
    except Exception as e:
        print("Error: Registrando voto: ", e)
        return None
    return voto


def eliminar_voto(idVoto):
    """ Delete a vote in the database
    :param idVoto: id of the vote to be deleted
    :return True if succesful,
     False otherwise
     """
    try:
        voto = Voto.objects.get(id=idVoto)
    except Voto.DoesNotExist:
        return False
    voto.delete()
    return True


def get_votos_from_db(idProcesoElectoral):
    """ Gets votes in the database correspondint to some electoral processs
    :param idProcesoElectoral: id of the vote to be deleted
    :return list of votes found
     """
    votos = Voto.objects.filter(idProcesoElectoral=idProcesoElectoral)
    return votos
