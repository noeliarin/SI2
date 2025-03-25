# Common code for client applications
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# author: rmarabini

from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from rest_framework import status
import os
import psycopg2


class VotingViewsTest(TestCase):
    """Test suite for the api views and RCP procedures."""
    def setUp(self):
        # if settings.WSGI_APPLICATION == 'Common.wsgi.application':
        #     print("DO NOT RUN THIS TEST FOR COMMON")
        #     print("This test is for the API and RCP client application")

        # Django test client
        self.client = Client()
        # direct access to the database, since
        # the test database is not the same as the one
        # used by the API
        connection_string = settings.DATABASE_SERVER_URL
        self.connection = psycopg2.connect(connection_string)
        self.cursor = self.connection.cursor()

        # delete votes
        self.cursor.execute("DELETE FROM voto;")
        self.connection.commit()

        self.censo_data = {
            'numeroDNI': '23',
            'nombre': '23',
            'fechaNacimiento': '23',
            'anioCenso': '23',
            'codigoAutorizacion': '23'
        }

        # Insert censo data if needed
        self.insertCenso(self.censo_data)

        self.voto_valid_data = {
            "idCircunscripcion": "CIRC123",
            "idMesaElectoral": "MESA123",
            "idProcesoElectoral": "ELEC123",
            "nombreCandidatoVotado": "Candidate A",
            "censo_id": "23"
        }

        self.url_voto_store = reverse('voto')
        self.url_censo_check = reverse('censo')
        self.url_testbd = reverse('testbd')

    def verifyvotoCreation(self, numeroDNI):
        query = f"SELECT * FROM voto where censo_id='{numeroDNI}';"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        if len(rows) == 0:
            return 0, None
        return len(rows), rows[0][0]

    def insertVoto(self, voto_data):
        insert_censo_query = """
        INSERT INTO voto (
            "idCircunscripcion",
            "idMesaElectoral",
            "idProcesoElectoral",
            "nombreCandidatoVotado",
            "marcaTiempo",
            "codigoRespuesta",
            "censo_id"
            )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(
            insert_censo_query, (
                voto_data["idCircunscripcion"],
                voto_data["idMesaElectoral"],
                voto_data["idProcesoElectoral"],
                voto_data["nombreCandidatoVotado"],
                voto_data["marcaTiempo"],
                voto_data["codigoRespuesta"],
                voto_data["censo_id"],
                )
            )
        self.connection.commit()

    def insertCenso(self, cemso_data):
        insert_censo_query = """
            INSERT INTO censo (
                "numeroDNI",
                nombre,
                "fechaNacimiento",
                "anioCenso",
                "codigoAutorizacion")
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT ("numeroDNI") DO NOTHING;
        """
        self.cursor.execute(
            insert_censo_query, (
                cemso_data["numeroDNI"],
                cemso_data["nombre"],
                cemso_data["fechaNacimiento"],
                cemso_data["anioCenso"],
                cemso_data["codigoAutorizacion"]
                )
            )
        self.connection.commit()

    def test_01_aportarinfo_censo_valid_post(self):
        """Check Censo information
        """
        # Form data for valid post request
        data = self.censo_data
        response = self.client.post(reverse('censo'), data)

        # Check redirection to the 'censo' view after successful POST
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, reverse('voto'))
        # test session
        session = self.client.session
        censoID = session['numeroDNI']
        self.assertEqual(censoID, self.censo_data['numeroDNI'])
        # session.save()

    def test_015_aportarinfo_censo_invalid_post(self):
        """check invalid censo entry
        """
        data = self.censo_data
        data['numeroDNI'] = '845rtte34'
        response = self.client.post(reverse('censo'), data)
        # print("response_content", response.content)
        # Check redirection to the 'censo' view after successful POST
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("Error" in str(response.content))

    def test_02_store_voto_valid_post(self):
        """Create and save a 'voto'
        """
        # create censo entry
        # not needed since we are going to use regular database
        # censo = Censo.objects.create(**self.censo_data)

        # set session variable to simulate a previous call to censo
        session = self.client.session
        session['numeroDNI'] = self.censo_data['numeroDNI']
        session.save()

        data = self.voto_valid_data
        response = self.client.post(
            reverse('voto'),
            data=data,  # censo data
            format='json'
        )
        # print("response", response.content)
        # Check result
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        voto = response.context.get('voto')
        # compare voto and voto_valid_data
        for key in self.voto_valid_data:
            if key == 'censo_id':
                continue
            self.assertEqual(
                self.voto_valid_data[key],
                voto[key])

    def test_03_delvoto_valid_post(self):
        """Test deleting an existing Voto object."""
        # create voto entry
        voto_data = {**self.voto_valid_data, 
                     'marcaTiempo': '2022-01-01 00:00:00',
                     'codigoRespuesta': '000',
                     'censo_id': self.censo_data['numeroDNI']}
        self.insertVoto(voto_data)
        numeroDNI = self.censo_data['numeroDNI']
        num_rows, voto_id = self.verifyvotoCreation(numeroDNI)
        data = {'id': voto_id}
        response = self.client.post(reverse('delvoto'), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Voto eliminado correctamente")

    def test_035_delvoto_invalid_post(self):
        """Test deleting an existing Voto object."""
        # create voto entry
        voto_data = {**self.voto_valid_data, 
                     'marcaTiempo': '2022-01-01 00:00:00',
                     'codigoRespuesta': '000',
                     'censo_id': self.censo_data['numeroDNI']}
        self.insertVoto(voto_data)
        data = {'id': 999999998}
        response = self.client.post(reverse('delvoto'), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Error")

    def test_04_getVotos_post(self):
        """Test deleting an existing Voto object."""
        # create censo entry
        self.censo_data['numeroDNI'] = '83583583L'
        self.insertCenso(self.censo_data)
        self.censo_data['numeroDNI'] = '67867868T'
        self.insertCenso(self.censo_data)

        # create voto entry
        voto_data = {**self.voto_valid_data, 
                     'marcaTiempo': '2022-01-01 00:00:00',
                     'codigoRespuesta': '000',
                     'censo_id': self.censo_data['numeroDNI']}
        voto_data['nombreCandidatoVotado'] = 'aaaaa0'
        self.insertVoto(voto_data)
        voto_data['censo_id'] = '83583583L'
        voto_data['idProcesoElectoral'] = 'c0'
        voto_data['nombreCandidatoVotado'] = 'aaaaa1'
        self.insertVoto(voto_data)
        voto_data['censo_id'] = '67867868T'
        voto_data['nombreCandidatoVotado'] = 'aaaaa2'
        self.insertVoto(voto_data)

        data = {'idProcesoElectoral': 'c0'}
        response = self.client.post(reverse('getvotos'), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "aaaaa1")
        self.assertContains(response, "aaaaa2")
        self.assertNotContains(response, "aaaaa0")

    def test_10_testdb_post(self):
        data_censo = self.censo_data
        data_voto = self.voto_valid_data
        data = {**data_censo, **data_voto}

        response = self.client.post(
            reverse('testbd'),
            data=data,  # censo and voto data
            format='json'
        )

        # Check result
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # voto_id = int(response.context.get('voto')['id'])
        # voto = self.voto_valid_data
        voto = response.context.get('voto')
        # compare voto and voto_valid_data
        for key in self.voto_valid_data:
            if key == 'censo_id':
                continue
            self.assertEqual(
                self.voto_valid_data[key],
                voto[key])

    def test_11_testdb_invalid_post(self):
        data_voto = self.voto_valid_data
        data = {**data_voto}

        response = self.client.post(
            reverse('testbd'),
            data=data,  # censo and voto data
            format='json'
        )
        # Check result
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Error")