import datetime
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from patients.models import Patient, PatientAllergy, PatientNextOfKin


class PatientRegistrationTests(APITestCase):

    def test_register_patient_with_allergies_and_nok(self):
        """Test full patient registration with nested allergies and next-of-kin."""
        url = reverse('patient-list')
        data = {
            "first_name": "Chinedu",
            "last_name": "Okafor",
            "gender": "Male",
            "date_of_birth": "1990-05-15",
            "phone": "08012345678",
            "blood_group": "O+",
            "genotype": "AA",
            "address": "123 Lagos Road",
            "city": "Lagos",
            "state": "Lagos",
            "allergies": [
                {"allergen": "Penicillin", "allergen_type": "Drug", "severity": "High", "reaction": "Rash"},
                {"allergen": "Peanuts", "allergen_type": "Food", "severity": "Low"},
            ],
            "next_of_kin": [
                {"name": "Ada Okafor", "relationship": "Wife", "phone": "08098765432", "is_primary": True},
            ],
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['patient_id'].startswith('PAT-'))
        self.assertEqual(len(response.data['allergies']), 2)
        self.assertEqual(len(response.data['next_of_kin']), 1)

    def test_register_patient_auto_generates_patient_id(self):
        """Test that patient_id is auto-generated when not provided."""
        url = reverse('patient-list')
        data = {
            "first_name": "Bola",
            "last_name": "Adeyemi",
            "phone": "08022222222",
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['patient_id'].startswith('PAT-'))

    def test_search_patients(self):
        """Test the quick search endpoint for front desk lookup."""
        Patient.objects.create(
            patient_id="PAT-00001",
            first_name="Jane",
            last_name="Doe",
            phone="08099999999"
        )
        Patient.objects.create(
            patient_id="PAT-00002",
            first_name="John",
            last_name="Smith",
            phone="08088888888"
        )

        url = reverse('patient-search-patients')
        response = self.client.get(url, {'q': 'Jane'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['first_name'], 'Jane')

    def test_search_patients_requires_query(self):
        """Test that search endpoint returns error without query param."""
        url = reverse('patient-search-patients')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_patients_by_gender(self):
        """Test filtering patients by gender."""
        Patient.objects.create(patient_id="PAT-F001", first_name="Ada", last_name="Eze", gender="Female")
        Patient.objects.create(patient_id="PAT-M001", first_name="Chidi", last_name="Nwachukwu", gender="Male")

        url = reverse('patient-list')
        response = self.client.get(url, {'gender': 'Female'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['first_name'], 'Ada')
