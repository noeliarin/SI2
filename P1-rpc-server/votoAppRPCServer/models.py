# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# author: rmarabini
"""Modelos de la aplicación de votación"""
from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.core.validators import MinLengthValidator


class CodigoRespuesta(models.TextChoices):
    """Enum para los códigos de respuesta"""
    RESPUESTA_OK = '000', 'Respuesta OK'
    RESPUESTA_ERR = 'ERR', 'Error'
    # Agrega más opciones aquí si es necesario


class Censo(models.Model):
    """Definición del modelo para representar un censo"""
    numeroDNI = models.CharField(max_length=9, primary_key=True)
    nombre = models.CharField(max_length=128)
    fechaNacimiento = models.CharField(max_length=8)
    anioCenso = models.CharField(max_length=4)
    codigoAutorizacion = models.CharField(max_length=3)

    def __str__(self):
        return f"{self.nombre} (DNI: {self.numeroDNI})"

    class Meta:
        db_table = 'censo'


class Voto(models.Model):
    """Definición del modelo para registrar un voto"""
    # use min_lentgh=1 to avoid empty strings
    # since "" is a valid string in Python
    idCircunscripcion = models.CharField(max_length=16)
    idMesaElectoral = models.CharField(max_length=16)
    idProcesoElectoral = models.CharField(max_length=16)
    nombreCandidatoVotado = models.CharField(
        max_length=16, blank=False, null=False,
        validators=[MinLengthValidator(1)])
    censo = models.ForeignKey(Censo, on_delete=models.CASCADE)
    marcaTiempo = models.DateTimeField(auto_now=True)
    codigoRespuesta = models.CharField(max_length=3,
                                       default=CodigoRespuesta.RESPUESTA_OK)

    class Meta:
        # Garantiza que cada persona (numeroDNI) solo pueda emitir
        # un voto por cada proceso electoral (idProcesoElectoral)
        constraints = [UniqueConstraint(fields=['censo',
                                                'idProcesoElectoral'],
                                        name='unique_blocking_voto')]
        db_table = 'voto'

    def __str__(self):
        return "Voto para " +\
               f"{self.nombreCandidatoVotado} en proceso " +\
               f"{self.idProcesoElectoral}"
