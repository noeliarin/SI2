# tests.py
from django.test import TestCase, Client
from django.urls import reverse
# from .forms import VotoForm, CensoForm, DelVotoForm, GetVotosForm
from django.conf import settings
import psycopg2


class VotoCensoViewsTest(TestCase):
    def setUp(self):
        # create virtual browser
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

        # Set up initial test data
        self.censo_data = {
            'numeroDNI': '39739740E',
            'nombre': 'Jose Moreno Locke',
            'fechaNacimiento': '09/04/66',
            'anioCenso': '2025',
            'codigoAutorizacion': '729'
        }

        # Insert censo data if needed
        self.insertCenso(self.censo_data)
        self.voto_data = {
            'idCircunscripcion': 'CIRC123',
            'idMesaElectoral': 'MESA123',
            'idProcesoElectoral': 'ELEC123',
            'nombreCandidatoVotado': 'Candidate A'
        }

        # URL endpoints for views
        self.aportarinfo_voto_url = reverse('voto')
        self.aportarinfo_censo_url = reverse('censo')
        self.testbd_url = reverse('testbd')
        self.delvoto_url = reverse('delvoto')
        self.getvotos_url = reverse('getvotos')

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

    def test_00_aportarinfo_censo_valid_submission(self):
        # Post valid data to `aportarinfo_voto` view
        response = self.client.post(self.aportarinfo_censo_url,
                                    data=self.censo_data)

        # Check if data is saved in the session
        session_data = self.client.session['numeroDNI']
        self.assertEqual(session_data, self.censo_data['numeroDNI'])
        # Check if redirected to `voto` page
        self.assertRedirects(response, reverse('voto'))

    def test_01_aportarinfo_censo_invalid_submission(self):
        # Submit empty form data
        response = self.client.post(
            self.aportarinfo_censo_url, data={})
        self.assertIn('Error', str(response.content))

    def test_05_aportarinfo_voto_with_valid_censo_data(self):
        # Set up session data with valid censo data
        session = self.client.session
        session['numeroDNI'] = self.censo_data['numeroDNI']
        session.save()

        # Submit valid Voto data
        response = self.client.post(
            self.aportarinfo_voto_url, data=self.voto_data)
        # Check if voto was created
        numeroDNI = self.censo_data['numeroDNI']
        num_rows, voto_id = self.verifyvotoCreation(numeroDNI)
        print("num_rows: ", num_rows)
        print("voto_id: ", voto_id)
        self.assertEqual(num_rows, 1)
        self.assertTemplateUsed(response, 'template_exito.html')

    def test_06_aportarinfo_voto_without_censo_data(self):
        # Submit valid Voto data without censo_data in session
        response = self.client.post(self.aportarinfo_voto_url,
                                    data=self.voto_data)
        # print("response: ", response.content)
        self.assertTemplateUsed(response, 'template_mensaje.html')
        self.assertContains(response, 'Error')

    def test_10_testbd_valid_submission(self):
        # Submit valid data for both Voto and Censo forms
        combined_data = {**self.voto_data, **self.censo_data}
        response = self.client.post(self.testbd_url, data=combined_data)

        # Verify Voto creation
        # Check if voto was created
        numeroDNI = self.censo_data['numeroDNI']
        num_rows, voto_id = self.verifyvotoCreation(numeroDNI)
        self.assertEqual(num_rows, 1)
        self.assertTemplateUsed(response, 'template_exito.html')

    def test_15_delvoto_valid_deletion(self):
        # Create a Voto instance to delete
        voto_data = {**self.voto_data, 
                     'marcaTiempo': '2022-01-01 00:00:00',
                     'codigoRespuesta': '000',
                     'censo_id': self.censo_data['numeroDNI']}
        self.insertVoto(voto_data)
        numeroDNI = self.censo_data['numeroDNI']
        num_rows, voto_id = self.verifyvotoCreation(numeroDNI)

        # Submit the deletion form
        response = self.client.post(self.delvoto_url, data={'id': voto_id})
        num_rows, voto_id = self.verifyvotoCreation(numeroDNI)
        self.assertEqual(num_rows, 0)
        self.assertTemplateUsed(response, 'template_mensaje.html')
        self.assertContains(response, '¡Voto eliminado correctamente!')

    def test_20_delvoto_invalid_id(self):
        # Submit with a non-existing ID
        response = self.client.post(self.delvoto_url, data={'id': 999})
        self.assertTemplateUsed(response, 'template_mensaje.html')
        self.assertContains(response, 'Error:')

    def test_25_getvotos_valid_idProcesoElectoral(self):
        # Create two Voto instances for the same proceso electoral
        voto_data = {**self.voto_data, 
                     'marcaTiempo': '2022-01-01 00:00:00',
                     'codigoRespuesta': '000',
                     'censo_id': self.censo_data['numeroDNI']}
        self.insertVoto(voto_data)
        # Submit a GetVotosForm with a valid idProcesoElectoral
        response = self.client.post(
            self.getvotos_url, data={'idProcesoElectoral': 'ELEC123'})
        self.assertEqual(len(response.context['result']), 1)
        self.assertTemplateUsed(response, 'template_get_votos_result.html')

    def test_30_testbd_invalid_submission(self):
        # Submit empty form data
        response = self.client.post(self.testbd_url, data={})
        self.assertIn('Error', str(response.content))