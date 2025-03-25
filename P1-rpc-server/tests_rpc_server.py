from django.test import TestCase, Client
from django.urls import reverse
import json
from .models import Censo, Voto
from copy import deepcopy
from rest_framework import status


class RpcEndpointTestCase(TestCase):
    def setUp(self):
        # Initialize the test client
        self.client = Client()

        self.censo_data = {
            'numeroDNI': '39739740E',
            'nombre': 'Jose Moreno Locke',
            'fechaNacimiento': '09/04/66',
            'codigoAutorizacion': '729'
        }

        self.voto_data = {
            "idCircunscripcion": "CIRC123",
            "idMesaElectoral": "MESA123",
            "idProcesoElectoral": "ELEC123",
            "nombreCandidatoVotado": "Candidate A",
            # Assuming this is an existing primary key in Censo
            # "censo_id": "123456789"
        }

    def disable_test_rpc_addition(self):  # Done
        # Define the URL for the RPC endpoint
        # Use the correct name for your RPC endpoint if it's not rpc
        url = reverse('rpc')

        # Define the payload matching your example
        payload = {
            "id": 2,
            "method": "test_add",
            "params": [5, 9],
            "jsonrpc": "2.0"
        }

        # Make the POST request to the RPC endpoint
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json")

        # Parse the JSON response
        response_data = response.json()

        # Check the HTTP status code
        self.assertEqual(response.status_code, 200)

        # Verify that the JSON-RPC response is correct
        expected_result = 14  # The expected result for test_add(5, 9)
        self.assertEqual(response_data.get('result'), expected_result)
        self.assertEqual(response_data.get('id'), payload['id'])
        self.assertEqual(response_data.get('jsonrpc'), "2.0")

    def test_00_rpc_voto(self):
        "create voto using rpc call"
        # Define the URL for the RPC endpoint
        url = reverse('rpc')

        # create censo entry
        _ = Censo.objects.create(**self.censo_data)

        # Define the payload matching your example
        data = self.voto_data
        # add foreign key
        data['censo_id'] = self.censo_data['numeroDNI']
        payload = {
            "id": 2,
            "method": "registrar_voto",
            "params": {'voto_dict': data},
            "jsonrpc": "2.0"
        }
        # Make the POST request to the RPC endpoint
        response = self.client.post(
            url, data=json.dumps(payload),
            content_type="application/json")

        # Parse the JSON response
        response_data = response.json()
        voto = response_data['result']
        for k, v in data.items():
            if k == 'censo_id':
                continue
            self.assertEqual(voto[k], v)

    def test_01_rpc_censo(self):
        "check censo using rpc call"
        # Define the URL for the RPC endpoint
        url = reverse('rpc')

        data = self.censo_data
        _ = Censo.objects.create(**data)
        # Define the payload matching your example
        payload = {
            "id": 2,
            "method": "verificar_censo",
            "params": {'censo_data': data},
            "jsonrpc": "2.0"
        }
        # Make the POST request to the RPC endpoint
        response = self.client.post(
            url, data=json.dumps(payload), content_type="application/json")

        # Parse the JSON response
        response_data = response.json()
        result = response_data.get('result')
        # print("result", result)
        self.assertTrue(result)
        # self.assertEqual(result[1], data['numeroDNI'])

    def test_10_del(self):
        "delete vote using rcp call"
        data = self.censo_data
        censo = Censo.objects.create(**data)
        data_voto = self.voto_data
        # create Voto
        voto = Voto.objects.create(**data_voto, censo=censo)
        voto_id = voto.id

        url = reverse('rpc')
        payload = {
            "id": 10,
            "method": "eliminar_voto",
            "params": [voto_id],
            "jsonrpc": "2.0"
        }
        # Make the POST request to the RPC endpoint
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json")

        # Parse the JSON response
        response_data = response.json()
        status = response_data.get('result')
        self.assertTrue(status)

    def test_20_list(self):
        # create censo entry
        censo = Censo.objects.create(**self.censo_data)
        # create another censo entry
        self.censo_data['numeroDNI'] = '123456789'
        censo2 = Censo.objects.create(**self.censo_data)

        # create voto entry
        _ = Voto.objects.create(**self.voto_data, censo=censo)
        # create another voto entry
        self.voto_data['nombreCandidatoVotado'] = 'Candidate B'
        _ = Voto.objects.create(**self.voto_data, censo=censo2)
        another_voto = deepcopy(self.voto_data)
        another_voto['idProcesoElectoral'] = 'another process'
        _ = Voto.objects.create(**another_voto, censo=censo2)

        url = reverse('rpc')
        payload = {
            "id": 10,
            "method": "get_votos_from_db",
            "params": [self.voto_data['idProcesoElectoral']],
            "jsonrpc": "2.0"
        }
        # Make the POST request to the RPC endpoint
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        result = response_data.get('result')
        self.assertEqual(len(result), 2)

    # def test_30_testdb(self):
    #     " create voto and check censo with a single call"
    #     data = self.censo_data
    #     censo = Censo.objects.create(**data)
    #     voto_data = self.voto_data
    #     censo_data = self.censo_data
    #     all_data = {**voto_data, **censo_data}

    #     url = reverse('rpc')
    #     payload = {
    #         "id": 30,
    #         "method": "TestBDProcedure",
    #         "params": list(all_data.values()),
    #         "jsonrpc": "2.0"
    #     }
    #     # Make the POST request to the RPC endpoint
    #     response = self.client.post(
    #         url,
    #         data=json.dumps(payload),
    #         content_type="application/json")
    #     # Parse the JSON response
    #     response_data = response.json()
    #     status, result = response_data.get('result')
    #     self.assertTrue(status)
    #     self.assertEqual(result['idCircunscripcion'],
    #                      voto_data['idCircunscripcion'])
    #     self.assertEqual(result['idMesaElectoral'],
    #                      voto_data['idMesaElectoral'])
    #     self.assertEqual(result['idProcesoElectoral'],
    #                      voto_data['idProcesoElectoral'])
    #     self.assertEqual(result['nombreCandidatoVotado'],
    #                      voto_data['nombreCandidatoVotado'])
