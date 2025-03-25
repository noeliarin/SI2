from django import forms


class VotoForm(forms.Form):
    idProcesoElectoral = forms.CharField(
        label='ID Proceso Electoral', required=True)
    idCircunscripcion = forms.CharField(
        label='ID Circunscripcion', required=True)
    idMesaElectoral = forms.CharField(
        label='ID Mesa Electoral', required=True)
    nombreCandidatoVotado = forms.CharField(
        label='Nombre Candidato Votado', required=True)


class CensoForm(forms.Form):
    numeroDNI = forms.CharField(label="Número de DNI", required=True)
    nombre = forms.CharField(label="Nombre", required=True)
    fechaNacimiento = forms.CharField(
        label="Fecha de Nacimiento", required=True)
    codigoAutorizacion = forms.CharField(
        label="Código de Autorización", required=True)


class DelVotoForm(forms.Form):
    id = forms.CharField(label="ID del Voto", required=True)


class GetVotosForm(forms.Form):
    idProcesoElectoral = forms.CharField(
        label='ID del Proceso Electoral', required=True)
