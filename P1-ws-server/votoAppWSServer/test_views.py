from copy import deepcopy
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Censo, Voto
from .serializers import VotoSerializer
# from django.forms.models import model_to_dict


class ApiViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url_voto_store = reverse('voto')
        self.url_censo_check = reverse('censo')
        # self.url_testbd = reverse('testbd')

        self.voto_valid_data = {
            "idCircunscripcion": "CIRC123",
            "idMesaElectoral": "MESA123",
            "idProcesoElectoral": "ELEC123",
            "nombreCandidatoVotado": "Candidate A",
            "censo_id": "123456789"
        }

        self.voto_invalid_data = {
            "idCircunscripcion": "CIRC123",
            "idMesaElectoral": "MESA123",
            # Missing 'idProcesoElectoral'
            "nombreCandidatoVotado": "Candidate A"
        }

        self.censo_data = {
            'numeroDNI': '39739740E',
            'nombre': 'Jose Moreno Locke',
            'fechaNacimiento': '09/04/66',
            'codigoAutorizacion': '729'
        }
        self.censo = Censo.objects.create(**self.censo_data)

    def test_01_censo_check_valid_data(self):
        # Test storing valid data
        response = self.client.post(
            self.url_censo_check,
            data=self.censo_data,  # voto data
            format='json'
        )
        # Check if the response is 200 OK and the message matches
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(), {'message': 'Datos encontrados en Censo.'})

    def test_02_censo_check_invalid_data(self):
        # Test checking censo with  invalid data (missing fields)
        self.censo_data['numeroDNI'] = '1234'
        response = self.client.post(
            self.url_censo_check,
            data=self.censo_data,  # voto data
            format='json'
        )
        # Check if the response is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Confirm that no 'voto_data' was saved in the session
        self.assertEqual(
            response.json(), {'message': 'Datos no encontrados en Censo.'})

    def test_05_list_votos(self):
        # create another censo entry. There is one with id=39739740E
        # stored in self.censo
        self.voto_valid_data.pop('censo_id')
        self.censo_data['numeroDNI'] = '123456789'
        censo2 = Censo.objects.create(**self.censo_data)
        # create voto entry
        _ = Voto.objects.create(**self.voto_valid_data, censo=self.censo)
        # create another voto entry
        self.voto_valid_data['nombreCandidatoVotado'] = 'Candidate B'
        _ = Voto.objects.create(**self.voto_valid_data, censo=censo2)
        another_voto = deepcopy(self.voto_valid_data)
        another_voto['idProcesoElectoral'] = 'another process'
        _ = Voto.objects.create(**another_voto, censo=censo2)

        url = reverse(
            'procesoelectoral',
            args=[self.voto_valid_data['idProcesoElectoral']])
        response = self.client.get(url)

        # Ensure the request was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the response data
        votos = Voto.objects.filter(
            idProcesoElectoral=self.voto_valid_data['idProcesoElectoral'])
        serializer = VotoSerializer(votos, many=True)
        self.assertEqual(response.data, serializer.data)

    def test_10_voto_store(self):

        # Test storing valid data
        # self.voto_valid_data['numeroDNI'] = '39739740E'
        self.voto_valid_data['censo_id'] = '39739740E'
        response = self.client.post(
            reverse('voto'),
            data=self.voto_valid_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for k, v in self.voto_valid_data.items():
            if k == 'censo_id':
                break
            self.assertEqual(v, response.data[k])

    def test_20_delete_existing_voto(self):
        """Test deleting an existing Voto object."""
        # create voto entry
        voto = Voto.objects.create(**self.voto_valid_data, censo=self.censo)
        # Build the delete URL using the ID of the created Voto instance
        url = reverse('voto', args=[voto.id])
        _ = self.client.delete(url)

        # Verify that the Voto instance has been deleted from the database
        self.assertFalse(Voto.objects.filter(id=voto.id).exists())

    def test_21_delete_nonexistent_voto(self):
        """Test attempting to delete a Voto object that does not exist."""
        # Build the delete URL using an ID that doesn't exist
        url = reverse('voto', args=[1234567])
        response = self.client.delete(url)

        # Check that the response status is 404 Not Found
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # def test_30_TestBD(self):
    #     censo_data = model_to_dict(self.censo)
    #     data = {**censo_data, **self.voto_valid_data}
    #     # Test storing valid data
    #     response = self.client.post(
    #         self.url_testbd,
    #         data=data,
    #         format='json'
    #     )
    #     # Check if the response is 200 OK and the message matches
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     return_dict = response.json()
    #     for k, v in self.voto_valid_data.items():
    #         self.assertEqual(v, return_dict[k])
    #     self.assertTrue(Voto.objects.exists())

    # def test_31_TestBD_with_invalid_vote(self):
    #     censo_data = model_to_dict(self.censo)
    #     data = {**censo_data}
    #     # Test storing valid data
    #     response = self.client.post(
    #         self.url_testbd,
    #         data=data,
    #         format='json'
    #     )
    #     # Check if the response is 200 OK and the message matches
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)