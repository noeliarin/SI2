from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Censo, Voto
from django.forms.models import model_to_dict
from django.utils.timezone import now



#{
#    "numeroDNI": "94994994D",
#    "nombre": "Sofia Poza Gracia",
#    "fechaNacimiento": "06/07/76",
#    "anioCenso": "2025",
#    "codigoAutorizacion": "104"
#}
class CensoView(APIView):
    """Validación de la existencia del votante en el censo"""
    
    def post(self, request):
        print(f"Datos recibidos: {request.data}")  # 👈 Depuración en la terminal

        numeroDNI = request.data.get('numeroDNI')
        nombre = request.data.get('nombre')
        fechaNacimiento = request.data.get('fechaNacimiento')
        anioCenso = request.data.get('anioCenso')
        codigoAutorizacion = request.data.get('codigoAutorizacion')

        if not all([numeroDNI, nombre, fechaNacimiento, anioCenso, codigoAutorizacion]):
            return Response(
                {'message': 'Faltan datos obligatorios'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if Censo.objects.filter(
            numeroDNI=numeroDNI,
            nombre=nombre,
            fechaNacimiento=fechaNacimiento,
            anioCenso=anioCenso,
            codigoAutorizacion=codigoAutorizacion
        ).exists():
            return Response({'message': 'Usuario encontrado en el censo.'}, status=status.HTTP_200_OK)

        return Response({'message': 'Datos no encontrados en Censo.'}, status=status.HTTP_404_NOT_FOUND)


class VotoView(APIView):
    """Emisión y eliminación de un voto"""

    #{
    #  "numeroDNI": "39739740E",
    #  "idProcesoElectoral": "2025",
    #  "idCircunscripcion": "729",
    #  "idMesaElectoral": "10",
    #  "nombreCandidatoVotado": "Maria González",
    #  "codigoRespuesta": "200"
    #}
    def post(self, request):
        print(f"Datos recibidos: {request.data}")  # Depuración

        # Obtener los datos del voto desde el cuerpo de la solicitud
        dni_votante = request.data.get('numeroDNI')
        id_proceso = request.data.get('idProcesoElectoral')
        id_circunscripcion = request.data.get('idCircunscripcion')
        id_mesa = request.data.get('idMesaElectoral')
        opcion = request.data.get('nombreCandidatoVotado')
        codigo_respuesta = request.data.get('codigoRespuesta')

        # Verificar que todos los campos obligatorios estén presentes
        if not all([dni_votante, id_proceso, id_circunscripcion, id_mesa, opcion, codigo_respuesta]):
            return Response(
                {'message': 'Faltan datos obligatorios'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Buscar al votante en el Censo
        try:
            votante = Censo.objects.get(numeroDNI=dni_votante)
        except Censo.DoesNotExist:
            return Response({'message': 'Votante no encontrado en el censo.'}, status=status.HTTP_404_NOT_FOUND)

        # Verificar si el votante ya ha emitido un voto en este proceso electoral
        if Voto.objects.filter(censo=votante, idProcesoElectoral=id_proceso).exists():
            return Response({'message': 'El votante ya ha emitido un voto en este proceso electoral.'}, status=status.HTTP_400_BAD_REQUEST)

        # Crear un nuevo voto
        voto = Voto.objects.create(
            censo=votante,
            idProcesoElectoral=id_proceso,
            idCircunscripcion=id_circunscripcion,
            idMesaElectoral=id_mesa,
            nombreCandidatoVotado=opcion,
            marcaTiempo=now(),  # Marca de tiempo actual
            codigoRespuesta=codigo_respuesta
        )

        # Incluir el identificador del censo en la respuesta
        voto_dict = model_to_dict(voto)
        voto_dict['censo_id'] = votante.numeroDNI  # Agregar el número de DNI (censo_id)

        # Retornar la respuesta con los detalles del voto creado
        return Response(voto_dict, status=status.HTTP_200_OK)


    def delete(self, request, id_voto):
        """Eliminar un voto por ID"""
        try:
            voto = Voto.objects.get(id=id_voto)
            voto.delete()
            return Response({'message': 'Voto eliminado correctamente.'}, status=status.HTTP_200_OK)
        except Voto.DoesNotExist:
            return Response({'message': 'Voto no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        
        
class ProcesoElectoralView(APIView):
    """Consulta de votos por proceso electoral"""
    def get(self, request, idProcesoElectoral):
        
        votos = Voto.objects.filter(idProcesoElectoral=idProcesoElectoral)

        if not votos.exists():
            return Response({'message': 'No hay votos para este proceso.'}, status=status.HTTP_404_NOT_FOUND)

        votos_list = [model_to_dict(voto) for voto in votos]
        return Response(votos_list, status=status.HTTP_200_OK)