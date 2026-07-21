import uuid
from django.db import models
from django.conf import settings


class Encounter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='encounters')
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctor_encounters'
    )
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='encounters'
    )
    queue_entry = models.ForeignKey(
        'appointments.QueueEntry',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='encounters'
    )
    encounter_type = models.CharField(max_length=100, blank=True, null=True)
    encounter_date = models.DateTimeField()
    status = models.CharField(max_length=50, default='In-Progress')
    chief_complaint = models.TextField(blank=True, null=True)
    subjective_note = models.TextField(blank=True, null=True)
    objective_note = models.TextField(blank=True, null=True)
    assessment_note = models.TextField(blank=True, null=True)
    plan_note = models.TextField(blank=True, null=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    signed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='signed_encounters'
    )

    def __str__(self):
        return f"Encounter {self.id} - {self.patient}"


class VitalSign(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    encounter = models.ForeignKey(Encounter, on_delete=models.CASCADE, related_name='vital_signs')
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='vital_signs')
    systolic_bp = models.IntegerField(null=True, blank=True)
    diastolic_bp = models.IntegerField(null=True, blank=True)
    heart_rate = models.IntegerField(null=True, blank=True)
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    respiratory_rate = models.IntegerField(null=True, blank=True)
    oxygen_saturation = models.IntegerField(null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    bmi = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorded_vitals'
    )
    recorded_at = models.DateTimeField()

    def __str__(self):
        return f"Vitals for {self.patient} at {self.recorded_at}"


class Diagnosis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    encounter = models.ForeignKey(Encounter, on_delete=models.CASCADE, related_name='diagnoses')
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='diagnoses')
    icd10_code = models.CharField(max_length=50, blank=True, null=True)
    icd10_name = models.CharField(max_length=255, blank=True, null=True)
    diagnosis_type = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    onset_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.icd10_code} - {self.icd10_name}"
