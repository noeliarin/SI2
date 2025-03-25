# your_app/management/commands/populate.py

import csv
import os
from django.core.management.base import BaseCommand
from votoAppRPCServer.models import Censo, Voto


class Command(BaseCommand):
    help = 'Populate the database with data from a CSV file'

    def handle(self, *args, **kwargs):
        self.cleanDataBase()
        self.populateDataBase()

    def cleanDataBase(self):
        # Delete all existing records from the database
        Censo.objects.all().delete()
        Voto.objects.all().delete()
        print("Database cleaned successfully")

    def populateDataBase(self):
        """Populate the database with data from a CSV file
        numeroDNI,nombre,fechaNacimiento,anioCenso,codigoAutorizacion
        39739740E,Jose Moreno Locke,09/04/66,2025,729
        """
        csv_file_path = os.path.join(os.path.dirname(__file__), 'data2.csv')
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            # Iterating over each row in the CSV
            for row in reader:
                # Create or update the Censo instance based on the numeroDNI
                Censo.objects.update_or_create(
                    numeroDNI=row['numeroDNI'],
                    defaults={
                        'nombre': row['nombre'],
                        'fechaNacimiento': row['fechaNacimiento'],
                        'anioCenso': row['anioCenso'],
                        'codigoAutorizacion': row['codigoAutorizacion']
                    }
                )
        print("Censo objects created successfully")
