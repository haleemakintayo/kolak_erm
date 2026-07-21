import uuid
from django.db import models
from django.conf import settings


class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    other_names = models.CharField(max_length=150, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    blood_group = models.CharField(max_length=10, blank=True, null=True)
    genotype = models.CharField(max_length=10, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    alt_phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    lga = models.CharField(max_length=100, blank=True, null=True)
    national_id = models.CharField(max_length=50, blank=True, null=True)
    photo_url = models.URLField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=20, default='Active')
    is_vip = models.BooleanField(default=False)
    is_deceased = models.BooleanField(default=False)
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registered_patients'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient_id} - {self.first_name} {self.last_name}"


class PatientAllergy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='allergies')
    allergen = models.CharField(max_length=255)
    allergen_type = models.CharField(max_length=100, blank=True, null=True)
    severity = models.CharField(max_length=50, blank=True, null=True)
    reaction = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.patient.patient_id} - {self.allergen}"


class PatientNextOfKin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='next_of_kin')
    name = models.CharField(max_length=255)
    relationship = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.relationship}) - {self.patient.patient_id}"
