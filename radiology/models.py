import uuid
from django.db import models
from django.conf import settings


class RadiologyRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='radiology_requests')
    encounter = models.ForeignKey(
        'clinical.Encounter',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='radiology_requests'
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='radiology_requests'
    )
    modality = models.CharField(max_length=100)
    body_part = models.CharField(max_length=100, blank=True, null=True)
    urgency = models.CharField(max_length=50, default='Routine')
    clinical_indication = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default='Requested')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    image_urls = models.JSONField(default=list, blank=True)
    report_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.modality} ({self.body_part}) - {self.patient}"


class RadiologyReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    radiology_request = models.ForeignKey(RadiologyRequest, on_delete=models.CASCADE, related_name='reports')
    findings = models.TextField(blank=True, null=True)
    impression = models.TextField(blank=True, null=True)
    recommendation = models.TextField(blank=True, null=True)
    critical_finding = models.BooleanField(default=False)
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='radiology_reports'
    )
    reported_at = models.DateTimeField(null=True, blank=True)
    digitally_signed = models.BooleanField(default=False)

    def __str__(self):
        return f"RadReport for {self.radiology_request}"
