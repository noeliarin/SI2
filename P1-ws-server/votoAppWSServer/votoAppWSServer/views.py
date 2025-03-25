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
    
    def post(self, request):
        
        
        print(f"Datos recibidos: {request.data}")  

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
            # Redirigir en lugar de devolver 200
            request.session['numeroDNI'] = numeroDNI

            return redirect('/restapiserver/voto/')            
        return Response({'message': 'Error.'}, status=status.HTTP_404_NOT_FOUND)

class VotoView(APIView):
    """Emisión y eliminación de un voto"""

    def post(self, request):
        print(f"Datos recibidos: {request.data}")  # Depuración

        # Usar el valor 'censo_id' si no se envía 'numeroDNI', o incluso obtenerlo de la sesión
        dni_votante = (request.data.get('numeroDNI') or
                       request.data.get('censo_id') or
                       request.session.get('numeroDNI'))
        id_proceso = request.data.get('idProcesoElectoral')
        id_circunscripcion = request.data.get('idCircunscripcion')
        id_mesa = request.data.get('idMesaElectoral')
        opcion = request.data.get('nombreCandidatoVotado')
        # Si no se envía, se asigna '200' por defecto
        codigo_respuesta = request.data.get('codigoRespuesta', '200')

        # Verificar que los campos obligatorios estén presentes
        if not all([dni_votante, id_proceso, id_circunscripcion, id_mesa, opcion]):
            return Response(
                {'message': 'Faltan datos obligatorios'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Buscar al votante en el Censo usando el DNI obtenido
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
        voto_dict['censo_id'] = votante.numeroDNI  # Agregar el número de DNI como 'censo_id'

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