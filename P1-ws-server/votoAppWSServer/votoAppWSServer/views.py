from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Censo, Voto
from django.forms.models import model_to_dict
from django.utils.timezone import now


from django.shortcuts import redirect, render
from votoAppWSServer.forms import VotoForm, CensoForm, DelVotoForm, GetVotosForm
from votoAppWSServer.votoDB import (verificar_censo, registrar_voto,
                            eliminar_voto, get_votos_from_db)

TITLE = '(votoSite)'

def testbd(request):

    if request.method == 'POST':

        voto_form = VotoForm(request.POST)
        censo_form = CensoForm(request.POST)
        censo_form.get_context()
        voto_form.get_context()

        if verificar_censo(censo_form.cleaned_data) is False:
            return render(
                request, 'template_mensaje.html',
                {'mensaje': '¡Error: Votante no registrado en el Censo!',
                 'title': TITLE})

        data = voto_form.cleaned_data
        data['censo_id'] = censo_form.cleaned_data['numeroDNI']

        # save voto

        voto = registrar_voto(data)

        if voto is None:
            return render(
                request, 'template_mensaje.html',
                {'mensaje': 'Error al registrar voto!',
                 'title': TITLE})

        context_dict = {'voto': voto, 'title': TITLE}

        return render(request, 'template_exito.html', context_dict)
    else:
        voto_form = VotoForm()
        del_voto_form = DelVotoForm()
        censo_form = CensoForm()
        get_votos_form = GetVotosForm()

        return render(request, 'template_test_bd.html',
                      {'voto_form': voto_form,
                       'censo_form': censo_form,
                       'del_voto_form': del_voto_form,
                       'get_votos_form': get_votos_form,
                       'title': TITLE})



#{
#    "numeroDNI": "94994994D",
#    "nombre": "Sofia Poza Gracia",
#    "fechaNacimiento": "06/07/76",
#    "anioCenso": "2025",
#    "codigoAutorizacion": "104"
#}
class CensoView(APIView):
    """Validación de la existencia del votante en el censo"""
    
    def get(self, request):
        """Permite que GET no genere error 405"""
        return Response({'message': 'Método GET no implementado en esta API, usa POST.'}, status=status.HTTP_200_OK)

    def post(self, request):
        print(f"Datos recibidos: {request.data}")  

        numeroDNI = request.data.get('numeroDNI', '').strip()
        nombre = request.data.get('nombre', '').strip()
        fechaNacimiento = request.data.get('fechaNacimiento', '').strip()
        codigoAutorizacion = request.data.get('codigoAutorizacion', '').strip()

        if not all([numeroDNI, nombre, fechaNacimiento, codigoAutorizacion]):
            return Response(
                {'message': 'Faltan datos obligatorios'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if Censo.objects.filter(
            numeroDNI=numeroDNI,
            nombre=nombre,
            fechaNacimiento=fechaNacimiento,
            codigoAutorizacion=codigoAutorizacion
        ).exists():
            request.session['numeroDNI'] = numeroDNI
            return redirect('/restapiserver/voto/')            

        return Response({'message': 'Error.'}, status=status.HTTP_404_NOT_FOUND)
    
class VotoView(APIView):
    """Emisión y eliminación de un voto"""

    #{
    #  "numeroDNI": "39739740E",     <-- Se obtiene de sesión (del Censo)
    #  "idProcesoElectoral": "2025",
    #  "idCircunscripcion": "06/07/76",   <-- Se usará el valor de fechaNacimiento enviado
    #  "idMesaElectoral": "104",         <-- Se usará el valor de codigoAutorizacion enviado
    #  "nombreCandidatoVotado": "Maria González",  <-- se usará el valor de 'nombre'
    #  "codigoRespuesta": "200"          <-- se fija a "200"
    #}
    
    def get(self, request):
        """Permite que GET no genere error 405"""
        return Response({'message': 'Método GET no implementado en esta API, usa POST.'}, status=status.HTTP_200_OK)

    def post(self, request):
        print(f"Datos recibidos: {request.data}")  # Depuración

        # Obtener el número de DNI del votante desde la sesión
        numeroDNI = request.session.get('numeroDNI')
        if not numeroDNI:
            return Response(
                {'message': 'No se ha validado el censo (número de DNI ausente).'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener los datos enviados por JMeter
        id_proceso = request.data.get('idProcesoElectoral', '').strip()
        # Se usará "nombre" para el nombre del candidato votado
        nombreCandidatoVotado = request.data.get('nombre', '').strip()
        # Se usa "fechaNacimiento" para el idCircunscripcion
        id_circunscripcion = request.data.get('fechaNacimiento', '').strip()
        # Se usa "codigoAutorizacion" para el idMesaElectoral
        id_mesa = request.data.get('codigoAutorizacion', '').strip()
        
        # Acortar id_mesa si supera 16 caracteres
        if len(id_mesa) > 16:
            id_mesa = id_mesa[:16]
        
        # Se fija un código de respuesta (se fija a "200")
        codigoRespuesta = "200"
        
        # Verificar que todos los datos obligatorios estén presentes
        if not all([numeroDNI, id_proceso, id_circunscripcion, id_mesa, nombreCandidatoVotado, codigoRespuesta]):
            return Response(
                {'message': 'Faltan datos obligatorios'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Buscar al votante en el Censo
        try:
            votante = Censo.objects.get(numeroDNI=numeroDNI)
        except Censo.DoesNotExist:
            return Response({'message': 'Votante no encontrado en el censo.'}, status=status.HTTP_404_NOT_FOUND)

        # Verificar si el votante ya ha emitido un voto en este proceso electoral
        if Voto.objects.filter(censo=votante, idProcesoElectoral=id_proceso).exists():
            return Response(
                {'message': 'El votante ya ha emitido un voto en este proceso electoral.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear un nuevo voto usando los valores mapeados
        voto = Voto.objects.create(
            censo=votante,
            idProcesoElectoral=id_proceso,
            idCircunscripcion=id_circunscripcion,
            idMesaElectoral=id_mesa,
            nombreCandidatoVotado=nombreCandidatoVotado,
            marcaTiempo=now(),  # Marca de tiempo actual
            codigoRespuesta=codigoRespuesta
        )

        # Incluir el identificador del censo en la respuesta y el mensaje que espera JMeter
        voto_dict = model_to_dict(voto)
        voto_dict['censo_id'] = votante.numeroDNI
        voto_dict['mensaje'] = "Voto Registrado"

        # Retornar la respuesta con los detalles del voto creado
        return Response(voto_dict, status=status.HTTP_200_OK)
        
class ProcesoElectoralView(APIView):
    """Consulta de votos por proceso electoral"""
    def get(self, request, idProcesoElectoral):
        
        votos = Voto.objects.filter(idProcesoElectoral=idProcesoElectoral)

        if not votos.exists():
            return Response({'message': 'No hay votos para este proceso.'}, status=status.HTTP_404_NOT_FOUND)

        votos_list = [model_to_dict(voto) for voto in votos]
        return Response(votos_list, status=status.HTTP_200_OK)