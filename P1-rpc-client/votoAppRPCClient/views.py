from django.shortcuts import redirect, render
from votoAppRPCClient.forms import VotoForm, CensoForm, DelVotoForm, GetVotosForm
from votoAppRPCClient.votoDB import (verificar_censo, registrar_voto,
                            eliminar_voto, get_votos_from_db)


TITLE = '(votoSite)'


# Create your views here.

def aportarinfo_voto(request):
    if request.method == 'POST':
        # data from form
        voto_form = VotoForm(request.POST)
        voto_form.get_context()

        # recoger variable de session

        if 'numeroDNI' in request.session:
            numeroDNI = request.session['numeroDNI']
        else:
            return render(
                request, 'template_mensaje.html',
                {'mensaje': '¡Error: DNI no encontrado en la sesión!',
                 'title': TITLE})
        voto_data = voto_form.cleaned_data
        # add numeroDNI to data
        voto_data['censo_id'] = numeroDNI
        # save voto and get updated voto
        voto = registrar_voto(voto_data)
        if voto is None:
            return render(request, 'template_mensaje.html',
                          {'mensaje': '¡Error: al registrar voto!',
                           'title': TITLE})
        context_dict = {'voto': voto, 'title': TITLE}
        return render(request, 'template_exito.html', context_dict)
    else:
        voto_form = VotoForm()
        context_dict = {'form': voto_form, 'title': TITLE}
        return render(request, 'template_voto.html', context_dict)


def aportarinfo_censo(request):

    if request.method == 'POST':

        censo_form = CensoForm(request.POST)
        censo_form.get_context()

        if verificar_censo(censo_form.cleaned_data) is False:
            return render(
                request, 'template_mensaje.html',
                {'mensaje': '¡Error: Votante no registrado en el Censo!',
                 'title': TITLE})

        # Guardamos el DNI
        request.session['numeroDNI'] = censo_form.cleaned_data['numeroDNI']
        return redirect('voto')

    else:

        censo_form = CensoForm()
        context_dict = {'form': censo_form, 'title': TITLE}

        return render(request, 'template_censo.html', context_dict)


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


def delvoto(request):

    if request.method == 'POST':
        del_voto_form = DelVotoForm(request.POST)
        if del_voto_form.is_valid():
            id = del_voto_form.cleaned_data['id']
            if eliminar_voto(id) is False:
                return render(request, 'template_mensaje.html',
                              {'mensaje': '¡Error: al elminar voto!',
                               'title': TITLE})
            return render(request, 'template_mensaje.html',
                          {'mensaje': '¡Voto eliminado correctamente!',
                           'title': TITLE})


def getvotos(request):
    if request.method == 'POST':
        get_votos_form = GetVotosForm(request.POST)
        if get_votos_form.is_valid():
            idProcesoElectoral =\
                get_votos_form.cleaned_data['idProcesoElectoral']
            votos = get_votos_from_db(idProcesoElectoral)
            return render(request, 'template_get_votos_result.html',
                          {'result': votos, 'title': TITLE})
