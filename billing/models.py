import uuid
from django.db import models
from django.conf import settings


class HMOProvider(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, blank=True, null=True)
    portal_url = models.URLField(max_length=500, blank=True, null=True)
    api_key = models.CharField(max_length=255, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class PatientHMOEnrollment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='hmo_enrollments')
    hmo_provider = models.ForeignKey(HMOProvider, on_delete=models.CASCADE, related_name='enrollments')
    hmo_number = models.CharField(max_length=100)
    plan_name = models.CharField(max_length=100, blank=True, null=True)
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.patient} - {self.hmo_provider.name} ({self.hmo_number})"


class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_date = models.DateField()
    encounter = models.ForeignKey(
        'clinical.Encounter',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices'
    )
    admission = models.ForeignKey(
        'admissions.Admission',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices'
    )
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    hmo_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    patient_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=50, default='Unpaid')

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.patient}"


class InvoiceItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=255)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    hmo_covered = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    patient_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reference_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.description} - Inv {self.invoice.invoice_number}"


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='payments')
    receipt_number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_payments'
    )
    receipt_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receipt {self.receipt_number} ({self.amount}) - {self.patient}"


class InsuranceClaim(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='insurance_claims')
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='insurance_claims')
    hmo_provider = models.ForeignKey(HMOProvider, on_delete=models.CASCADE, related_name='insurance_claims')
    claim_number = models.CharField(max_length=50, unique=True)
    amount_claimed = models.DecimalField(max_digits=12, decimal_places=2)
    amount_approved = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=50, default='Submitted')
    submitted_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Claim {self.claim_number} - {self.hmo_provider.name}"
