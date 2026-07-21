import uuid
from django.db import models
from django.conf import settings


class Appointment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctor_appointments'
    )
    reference_number = models.CharField(max_length=50, unique=True)
    appointment_type = models.CharField(max_length=100, blank=True, null=True)
    appointment_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    chief_complaint = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default='Scheduled')
    arrived_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Appt {self.reference_number} - {self.patient}"


class QueueEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='queue_entries')
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='queue_entries'
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctor_queue_entries'
    )
    ticket_number = models.IntegerField()
    priority = models.CharField(max_length=50, default='Normal')
    status = models.CharField(max_length=50, default='Waiting')
    queue_date = models.DateField()
    arrived_at = models.DateTimeField(null=True, blank=True)
    called_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Queue #{self.ticket_number} - {self.patient}"
