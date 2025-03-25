# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# author: rmarabini
"Interface with the dataabse"
from django.conf import settings
from xmlrpc.client import ServerProxy


def verificar_censo(censo_data):
    """ Check if the voter is registered in the Censo
    :param censo_dict: dictionary with the voter data
                       (as provided by CensoForm)
    :return True or False if censo_data is not valid
    """
    with ServerProxy(settings.RPCAPIBASEURL) as proxy:
        return proxy.verificar_censo(censo_data)


def registrar_voto(voto_dict):
    """ Register a vote in the database
    :param voto_dict: dictionary with the vote data (as provided by VotoForm)
      plus de censo_id (numeroDNI) of the voter
    :return new voto info if succesful, None otherwise
    """
    with ServerProxy(settings.RPCAPIBASEURL) as proxy:
        return proxy.registrar_voto(voto_dict)


def eliminar_voto(idVoto):
    """ Delete a vote in the database
    :param idVoto: id of the vote to be deleted
    :return True if succesful,
     False otherwise
     """
    with ServerProxy(settings.RPCAPIBASEURL) as proxy:
        return proxy.eliminar_voto(idVoto)


def get_votos_from_db(idProcesoElectoral):
    """ Gets votes in the database correspondint to some electoral processs
    :param idProcesoElectoral: id of the vote to be deleted
    :return list of votes found
     """
    with ServerProxy(settings.RPCAPIBASEURL) as proxy:
        return proxy.get_votos_from_db(idProcesoElectoral)
    

<<<<<<< HEAD
=======
    
>>>>>>> 767df54 (Guardando cambios locales antes de hacer pull)
