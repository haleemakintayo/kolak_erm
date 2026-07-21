import uuid
from django.db import models
from django.conf import settings


class LabTestCatalog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    sample_type = models.CharField(max_length=100, blank=True, null=True)
    turnaround_hours = models.IntegerField(default=24)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class LabRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='lab_requests')
    encounter = models.ForeignKey(
        'clinical.Encounter',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lab_requests'
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lab_requests'
    )
    urgency = models.CharField(max_length=50, default='Routine')
    clinical_indication = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default='Requested')
    specimen_id = models.CharField(max_length=100, blank=True, null=True)
    barcode = models.CharField(max_length=100, blank=True, null=True)
    has_critical = models.BooleanField(default=False)
    report_url = models.URLField(max_length=500, blank=True, null=True)
    released_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"LabReq {self.id} - {self.patient}"


class LabRequestTest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lab_request = models.ForeignKey(LabRequest, on_delete=models.CASCADE, related_name='request_tests')
    test_catalog = models.ForeignKey(
        LabTestCatalog,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='request_tests'
    )
    test_name = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='Pending')

    def __str__(self):
        return f"{self.test_name} - {self.lab_request}"


class LabResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lab_request = models.ForeignKey(LabRequest, on_delete=models.CASCADE, related_name='results')
    lab_request_test = models.ForeignKey(LabRequestTest, on_delete=models.CASCADE, related_name='results')
    analyte_name = models.CharField(max_length=255)
    value = models.CharField(max_length=255, blank=True, null=True)
    numeric_value = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    reference_min = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    reference_max = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    flag = models.CharField(max_length=50, blank=True, null=True)
    is_critical = models.BooleanField(default=False)
    comments = models.TextField(blank=True, null=True)
    entered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='entered_lab_results'
    )
    entered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.analyte_name}: {self.value}"
