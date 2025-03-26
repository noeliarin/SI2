from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect, render
from django.forms.models import model_to_dict
from django.utils.timezone import now
from .models import Censo, Voto
from votoAppWSServer.forms import VotoForm, CensoForm, DelVotoForm, GetVotosForm
from votoAppWSServer.votoDB import verificar_censo, registrar_voto, eliminar_voto, get_votos_from_db

TITLE = '(votoSite)'

def testbd(request):
    if request.method == 'POST':
        voto_form = VotoForm(request.POST)
        censo_form = CensoForm(request.POST)
        censo_form.get_context()
        voto_form.get_context()

        if not verificar_censo(censo_form.cleaned_data):
            return render(request, 'template_mensaje.html', {'mensaje': '¡Error: Votante no registrado en el Censo!', 'title': TITLE})

        data = voto_form.cleaned_data
        data['censo_id'] = censo_form.cleaned_data['numeroDNI']

        voto = registrar_voto(data)
        if voto is None:
            return render(request, 'template_mensaje.html', {'mensaje': 'Error al registrar voto!', 'title': TITLE})

        return render(request, 'template_exito.html', {'voto': voto, 'title': TITLE})

    return render(request, 'template_test_bd.html', {
        'voto_form': VotoForm(),
        'censo_form': CensoForm(),
        'del_voto_form': DelVotoForm(),
        'get_votos_form': GetVotosForm(),
        'title': TITLE
    })


class CensoView(APIView):
    """Validación de la existencia del votante en el censo"""

    def get(self, request):
        """Evita error 405"""
        return Response({'message': 'Método GET no implementado en esta API, usa POST.'}, status=status.HTTP_200_OK)

    def post(self, request):
        print(f"Datos crudos recibidos: {request.body}")  # Debug
        print(f"Headers: {request.headers}")

        # Soporte para JSON y form-data
        numeroDNI = request.data.get('numeroDNI') or request.POST.get('numeroDNI')
        nombre = request.data.get('nombre') or request.POST.get('nombre')
        fechaNacimiento = request.data.get('fechaNacimiento') or request.POST.get('fechaNacimiento')
        codigoAutorizacion = request.data.get('codigoAutorizacion') or request.POST.get('codigoAutorizacion')

        print(f"Datos extraídos: DNI={numeroDNI}, Nombre={nombre}, Fecha={fechaNacimiento}, Código={codigoAutorizacion}")

        if not all([numeroDNI, nombre, fechaNacimiento, codigoAutorizacion]):
            return Response({'message': 'Faltan datos obligatorios'}, status=status.HTTP_400_BAD_REQUEST)

        if Censo.objects.filter(
            numeroDNI=numeroDNI,
            nombre=nombre,
            fechaNacimiento=fechaNacimiento,
            codigoAutorizacion=codigoAutorizacion
        ).exists():
            request.session['numeroDNI'] = numeroDNI
            return redirect('/restapiserver/voto/')            

        return Response({'message': 'Error: Usuario no encontrado en el censo'}, status=status.HTTP_404_NOT_FOUND)

class VotoView(APIView):
    """Emisión y eliminación de un voto"""

    def post(self, request):
        print(f"Datos recibidos: {request.data}")  # Debug

        dni_votante = request.data.get('numeroDNI') or request.POST.get('numeroDNI')
        id_proceso = request.data.get('idProcesoElectoral') or request.POST.get('idProcesoElectoral')
        id_circunscripcion = request.data.get('idCircunscripcion') or request.POST.get('idCircunscripcion')
        id_mesa = request.data.get('idMesaElectoral') or request.POST.get('idMesaElectoral')
        opcion = request.data.get('nombreCandidatoVotado') or request.POST.get('nombreCandidatoVotado')
        codigo_respuesta = request.data.get('codigoRespuesta') or request.POST.get('codigoRespuesta')

        if not all([dni_votante, id_proceso, id_circunscripcion, id_mesa, opcion, codigo_respuesta]):
            return Response({'message': 'Faltan datos obligatorios'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            votante = Censo.objects.get(numeroDNI=dni_votante)
        except Censo.DoesNotExist:
            return Response({'message': 'Votante no encontrado en el censo.'}, status=status.HTTP_404_NOT_FOUND)

        if Voto.objects.filter(censo=votante, idProcesoElectoral=id_proceso).exists():
            return Response({'message': 'El votante ya ha emitido un voto en este proceso electoral.'},
                            status=status.HTTP_400_BAD_REQUEST)

        voto = Voto.objects.create(
            censo=votante,
            idProcesoElectoral=id_proceso,
            idCircunscripcion=id_circunscripcion,
            idMesaElectoral=id_mesa,
            nombreCandidatoVotado=opcion,
            marcaTiempo=now(),
            codigoRespuesta=codigo_respuesta
        )

        voto_dict = model_to_dict(voto)
        voto_dict['censo_id'] = votante.numeroDNI

        # Renderizamos el template incluyendo 'mensaje' con "Voto Registrado"
        context = {'voto': voto_dict, 'title': TITLE, 'mensaje': 'Voto Registrado'}
        return render(request, 'template_exito.html', context)

class ProcesoElectoralView(APIView):
    """Consulta de votos por proceso electoral"""

    def get(self, request, idProcesoElectoral):
        votos = Voto.objects.filter(idProcesoElectoral=idProcesoElectoral)
        if not votos.exists():
            return Response({'message': 'No hay votos para este proceso.'}, status=status.HTTP_404_NOT_FOUND)

        votos_list = [model_to_dict(voto) for voto in votos]
        return Response(votos_list, status=status.HTTP_200_OK)
