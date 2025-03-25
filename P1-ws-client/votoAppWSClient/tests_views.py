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
# get calling file
# import inspect


class VotingViewsTest(TestCase):
    """Test suite for the api views and RCP procedures."""
    def setUp(self):
        # if settings.WSGI_APPLICATION == 'Common.wsgi.application':
        #     print("DO NOT RUN THIS TEST FOR COMMON")
        #     print("This test is for the API and RCP client application")

        # Django test client
        self.client = Client()
        # base_url = None  # Default value, overridden in subclasses

        self.voto_valid_data = {
            "idCircunscripcion": "CIRC123",
            "idMesaElectoral": "MESA123",
            "idProcesoElectoral": "ELEC123",
            "nombreCandidatoVotado": "Candidate A",
            "censo_id": "23"
        }

        self.censo_data = {
            'numeroDNI': '23',
            'nombre': '23',
            'fechaNacimiento': '23',
            'anioCenso': '23',
            'codigoAutorizacion': '23'
        }
        self.url_voto_store = reverse('voto')
        self.url_censo_check = reverse('censo')
        self.url_testbd = reverse('testbd')

        # since we use an API the test database is not the one
        # in which data is going to be saved, so we better reset the
        # database to a known state
        print("deleting votes")
        # this is a horrible hack but I do not know how to delete
        # data in the orignal database (used by restapi_server
        # and not in the test one) Other options seems to conflict
        # with the way the tests are run.
        # NOTE that the test creates the test_$DATABASE_CLIENT_URL database and
        # any acces to models will be in this database
        # but the database accesed by restapi_server is $DATABASE_SERVER_URL
        self.DATABASE_SERVER_URL = settings.DATABASE_SERVER_URL
        self.vototable = 'voto'
        os.system(f"echo 'delete from \"{self.vototable}\"'"
                  f" | psql {self.DATABASE_SERVER_URL}")

        print(f"""This test only works if (1) {settings.RESTAPIBASEURL}
              server is up and running and (2) the database is populated.
              Very likely in the future ths test should be done with mocks
              and not real calls to the server.""")

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
        # print("voto", voto)
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
        command = f"""echo "INSERT into {self.vototable}
            (\\"id\\", \\"idCircunscripcion\\", \\"idMesaElectoral\\",
             \\"idProcesoElectoral\\", \\"nombreCandidatoVotado\\",
             \\"marcaTiempo\\", \\"codigoRespuesta\\", \\"censo_id\\")
        VALUES (999999999, 'a', 'b', 'c', 'd', now(), '000', 23);" |
        psql {self.DATABASE_SERVER_URL}"""
        # print(command)
        _ = os.system(command)
        data = {'id': 999999999}
        response = self.client.post(reverse('delvoto'), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Voto eliminado correctamente")

    def test_035_delvoto_invalid_post(self):
        """Test deleting an existing Voto object."""
        # create voto entry
        command = f"""echo "INSERT into {self.vototable}
            (\\"id\\", \\"idCircunscripcion\\", \\"idMesaElectoral\\",
             \\"idProcesoElectoral\\", \\"nombreCandidatoVotado\\",
             \\"marcaTiempo\\", \\"codigoRespuesta\\", \\"censo_id\\")
        VALUES (999999999, 'a', 'b', 'c', 'd', now(), '000', 23);" |
        psql {self.DATABASE_SERVER_URL}"""
        _ = os.system(command)
        data = {'id': 999999998}
        response = self.client.post(reverse('delvoto'), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Error")

    def test_04_getVotos_post(self):
        """Test deleting an existing Voto object."""
        # create voto entry
        command = f"""echo "INSERT into {self.vototable}
            (\\"id\\", \\"idCircunscripcion\\", \\"idMesaElectoral\\",
             \\"idProcesoElectoral\\", \\"nombreCandidatoVotado\\",
             \\"marcaTiempo\\", \\"codigoRespuesta\\", \\"censo_id\\")
        VALUES (999999990, 'aaaaa0', 'b0', 'c0', 'd0',
        now(), '000', '39739740E');" | psql {self.DATABASE_SERVER_URL}"""
        os.system(command)
        command = f"""echo "INSERT into {self.vototable}
            (\\"id\\", \\"idCircunscripcion\\", \\"idMesaElectoral\\",
             \\"idProcesoElectoral\\", \\"nombreCandidatoVotado\\",
             \\"marcaTiempo\\", \\"codigoRespuesta\\", \\"censo_id\\")
        VALUES (999999991, 'aaaaa1', 'b1', 'c0', 'd1',
        now(), '000', '83583583L');" | psql {self.DATABASE_SERVER_URL}"""
        os.system(command)
        command = f"""echo "INSERT into {self.vototable}
            (\\"id\\", \\"idCircunscripcion\\", \\"idMesaElectoral\\",
             \\"idProcesoElectoral\\", \\"nombreCandidatoVotado\\",
             \\"marcaTiempo\\", \\"codigoRespuesta\\", \\"censo_id\\")
        VALUES (999999992, 'aaaaa2', 'b2', 'c2', 'd2',
        now(), '000', '67867868T');" | psql {self.DATABASE_SERVER_URL}"""
        os.system(command)
        data = {'idProcesoElectoral': 'c0'}
        response = self.client.post(reverse('getvotos'), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "aaaaa0")
        self.assertContains(response, "aaaaa1")
        self.assertNotContains(response, "aaaaa2")

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
