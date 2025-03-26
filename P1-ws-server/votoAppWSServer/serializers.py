from rest_framework import serializers
from .models import Censo, Voto

class CensoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Censo
        fields = ['numeroDNI', 'nombre', 'fechaNacimiento', 'anioCenso', 'codigoAutorizacion']

    def create(self, validated_data):
        return validated_data

    

class VotoSerializer(serializers.ModelSerializer):
    censo = serializers.CharField(source='censo.numeroDNI')
    codigoRespuesta = serializers.CharField()

    class Meta:
        model = Voto
        fields = ['id','idCircunscripcion', 'idMesaElectoral', 'idProcesoElectoral', 'nombreCandidatoVotado', 'censo', 'codigoRespuesta']
