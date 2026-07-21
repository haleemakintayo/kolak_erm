import datetime
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from patients.models import Patient
from users.models import User, Role, Department
from appointments.models import Appointment, QueueEntry


class AppointmentAPITests(APITestCase):

    def setUp(self):
        self.department = Department.objects.create(name="General Medicine")
        self.role = Role.objects.create(name="Doctor", code="DOCTOR")
        self.doctor = User.objects.create_user(
            username="dr_ade",
            email="dr.ade@kolak.com",
            password="testpass123",
            first_name="Ade",
            last_name="Bakare",
            role=self.role,
            department=self.department,
        )
        self.patient = Patient.objects.create(
            patient_id="PAT-00001",
            first_name="Jane",
            last_name="Doe",
            phone="08099999999"
        )

    def test_create_appointment(self):
        url = reverse('appointment-list')
        data = {
            "patient": str(self.patient.id),
            "doctor": str(self.doctor.id),
            "appointment_type": "Consultation",
            "appointment_date": "2026-07-25",
            "start_time": "09:00",
            "end_time": "09:30",
            "chief_complaint": "Headache",
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['reference_number'].startswith('APT-'))
        self.assertEqual(response.data['status'], 'Scheduled')

    def test_double_booking_prevention(self):
        url = reverse('appointment-list')
        base_data = {
            "patient": str(self.patient.id),
            "doctor": str(self.doctor.id),
            "appointment_type": "Consultation",
            "appointment_date": "2026-07-25",
            "start_time": "10:00",
            "end_time": "10:30",
        }
        # First booking should succeed
        response = self.client.post(url, base_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Second overlapping booking should fail
        patient2 = Patient.objects.create(
            patient_id="PAT-00002",
            first_name="John",
            last_name="Smith"
        )
        overlap_data = base_data.copy()
        overlap_data['patient'] = str(patient2.id)
        overlap_data['start_time'] = '10:15'
        overlap_data['end_time'] = '10:45'
        response = self.client.post(url, overlap_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancel_appointment(self):
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            reference_number="APT-TESTCANCEL",
            appointment_date=datetime.date(2026, 7, 25),
            start_time=datetime.time(11, 0),
            end_time=datetime.time(11, 30),
            status='Scheduled',
        )
        url = reverse('appointment-cancel', kwargs={'pk': str(appointment.id)})
        response = self.client.post(url, {'cancellation_reason': 'Patient request'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['status'], 'Cancelled')

    def test_check_in_creates_queue_entry(self):
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            reference_number="APT-TESTCHECKIN",
            appointment_date=datetime.date.today(),
            start_time=datetime.time(14, 0),
            end_time=datetime.time(14, 30),
            status='Scheduled',
        )
        url = reverse('appointment-check-in', kwargs={'pk': str(appointment.id)})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['appointment']['status'], 'Checked-In')
        self.assertIsNotNone(response.data['queue_entry'])
        self.assertEqual(response.data['queue_entry']['ticket_number'], 1)
        self.assertEqual(response.data['queue_entry']['status'], 'Waiting')


class QueueEntryAPITests(APITestCase):

    def setUp(self):
        self.department = Department.objects.create(name="General Medicine")
        self.role = Role.objects.create(name="Doctor", code="DOCTOR")
        self.doctor = User.objects.create_user(
            username="dr_chidi",
            email="dr.chidi@kolak.com",
            password="testpass123",
            first_name="Chidi",
            last_name="Nwosu",
            role=self.role,
            department=self.department,
        )
        self.patient = Patient.objects.create(
            patient_id="PAT-Q0001",
            first_name="Mary",
            last_name="Johnson",
            phone="08077777777"
        )
        self.queue_entry = QueueEntry.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            ticket_number=1,
            priority='Normal',
            status='Waiting',
            queue_date=datetime.date.today(),
            arrived_at=timezone.now(),
        )

    def test_list_todays_queue(self):
        url = reverse('queue-entry-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_call_next_patient(self):
        url = reverse('queue-entry-call-next', kwargs={'pk': str(self.queue_entry.id)})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['status'], 'In-Consultation')
        self.assertIsNotNone(response.data['data']['called_at'])

    def test_complete_queue_entry(self):
        self.queue_entry.status = 'In-Consultation'
        self.queue_entry.called_at = timezone.now()
        self.queue_entry.save()

        url = reverse('queue-entry-complete', kwargs={'pk': str(self.queue_entry.id)})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['status'], 'Completed')

    def test_walk_in_queue_entry(self):
        """Test creating a walk-in queue entry (no appointment)."""
        url = reverse('queue-entry-list')
        data = {
            "patient": str(self.patient.id),
            "doctor": str(self.doctor.id),
            "priority": "Urgent",
            "queue_date": str(datetime.date.today()),
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['ticket_number'], 2)  # After existing ticket 1
        self.assertEqual(response.data['priority'], 'Urgent')


class DoctorLookupAPITests(APITestCase):

    def setUp(self):
        self.dept1 = Department.objects.create(name="Cardiology")
        self.dept2 = Department.objects.create(name="Neurology")
        self.role = Role.objects.create(name="Doctor", code="DOCTOR2")
        self.doc1 = User.objects.create_user(
            username="dr_cardiac",
            email="cardiac@kolak.com",
            password="testpass123",
            first_name="Cardiac",
            last_name="Specialist",
            role=self.role,
            department=self.dept1,
        )
        self.doc2 = User.objects.create_user(
            username="dr_neuro",
            email="neuro@kolak.com",
            password="testpass123",
            first_name="Neuro",
            last_name="Specialist",
            role=self.role,
            department=self.dept2,
        )

    def test_list_doctors(self):
        url = reverse('doctor-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_filter_doctors_by_department(self):
        url = reverse('doctor-list')
        response = self.client.get(url, {'department': str(self.dept1.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['first_name'], 'Cardiac')

    def test_search_doctors(self):
        url = reverse('doctor-list')
        response = self.client.get(url, {'search': 'Neuro'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['first_name'], 'Neuro')
