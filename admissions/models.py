import uuid
from django.db import models
from django.conf import settings


class Ward(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=100, blank=True, null=True)
    capacity = models.IntegerField(default=0)
    head_nurse = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_wards'
    )
    floor = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Bed(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='beds')
    bed_number = models.CharField(max_length=50)
    room_number = models.CharField(max_length=50, blank=True, null=True)
    bed_type = models.CharField(max_length=100, blank=True, null=True)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=50, default='Available')

    def __str__(self):
        return f"Bed {self.bed_number} ({self.ward.name})"


class Admission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='admissions')
    bed = models.ForeignKey(Bed, on_delete=models.SET_NULL, null=True, blank=True, related_name='admissions')
    ward = models.ForeignKey(Ward, on_delete=models.SET_NULL, null=True, blank=True, related_name='admissions')
    admission_number = models.CharField(max_length=50, unique=True)
    admission_type = models.CharField(max_length=100, blank=True, null=True)
    admitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admitted_admissions'
    )
    attending_doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attending_admissions'
    )
    admission_date = models.DateTimeField()
    actual_discharge_date = models.DateTimeField(null=True, blank=True)
    provisional_diagnosis = models.TextField(blank=True, null=True)
    discharge_summary = models.TextField(blank=True, null=True)
    discharge_instructions = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default='Admitted')

    def __str__(self):
        return f"Admission {self.admission_number} - {self.patient}"
