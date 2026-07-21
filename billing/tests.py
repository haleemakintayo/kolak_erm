import datetime
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from patients.models import Patient
from billing.models import HMOProvider, PatientHMOEnrollment


class PatientHMOEnrollmentAPITests(APITestCase):

    def setUp(self):
        self.patient = Patient.objects.create(
            patient_id="PAT-10001",
            first_name="Jane",
            last_name="Doe",
            gender="Female",
            phone="08012345678"
        )
        self.hmo_provider = HMOProvider.objects.create(
            name="Hygeia HMO",
            code="HYG-01",
            contact_email="info@hygeia.com",
            is_active=True
        )
        self.enrollment = PatientHMOEnrollment.objects.create(
            patient=self.patient,
            hmo_provider=self.hmo_provider,
            hmo_number="HYG-PAT-998",
            plan_name="Gold Plan",
            valid_from=datetime.date(2025, 1, 1),
            valid_until=datetime.date(2026, 12, 31),
            is_active=True
        )

    def test_list_hmo_providers(self):
        url = reverse('hmo-provider-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], "Hygeia HMO")

    def test_list_enrollments(self):
        url = reverse('patient-hmo-enrollment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['hmo_number'], "HYG-PAT-998")

    def test_filter_enrollment_by_patient(self):
        url = reverse('patient-hmo-enrollment-list')
        response = self.client.get(url, {'patient': 'PAT-10001'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_create_enrollment(self):
        url = reverse('patient-hmo-enrollment-list')
        data = {
            "patient": str(self.patient.id),
            "hmo_provider": str(self.hmo_provider.id),
            "hmo_number": "HYG-PAT-999",
            "plan_name": "Platinum Plan",
            "valid_from": "2026-01-01",
            "valid_until": "2026-12-31",
            "is_active": True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['hmo_number'], "HYG-PAT-999")

    def test_date_validation_error(self):
        url = reverse('patient-hmo-enrollment-list')
        data = {
            "patient": str(self.patient.id),
            "hmo_provider": str(self.hmo_provider.id),
            "hmo_number": "HYG-PAT-ERR",
            "plan_name": "Basic Plan",
            "valid_from": "2026-12-31",
            "valid_until": "2025-01-01",
            "is_active": True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('valid_until', response.data)

    def test_toggle_active_action(self):
        url = reverse('patient-hmo-enrollment-toggle-active', kwargs={'pk': str(self.enrollment.id)})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['data']['is_active'])

        # Toggle back
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['data']['is_active'])

    def test_nested_patient_enrollments_endpoint(self):
        url = reverse('patient-enrollments', kwargs={'pk': str(self.patient.id)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['hmo_number'], "HYG-PAT-998")

        # Create enrollment via nested endpoint
        post_data = {
            "hmo_provider": str(self.hmo_provider.id),
            "hmo_number": "HYG-PAT-NESTED",
            "plan_name": "Silver Plan",
            "is_active": True
        }
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['hmo_number'], "HYG-PAT-NESTED")
