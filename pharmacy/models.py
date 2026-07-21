import uuid
from django.db import models
from django.conf import settings


class Drug(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    generic_name = models.CharField(max_length=255, blank=True, null=True)
    brand_name = models.CharField(max_length=255, blank=True, null=True)
    strength = models.CharField(max_length=100, blank=True, null=True)
    dosage_form = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    therapeutic_class = models.CharField(max_length=100, blank=True, null=True)
    atc_code = models.CharField(max_length=50, blank=True, null=True)
    is_controlled = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Prescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='prescriptions')
    encounter = models.ForeignKey(
        'clinical.Encounter',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prescriptions'
    )
    prescribed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prescribed_prescriptions'
    )
    rx_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=50, default='Pending')
    signed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Rx {self.rx_number} - {self.patient}"


class PrescriptionItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    drug = models.ForeignKey(Drug, on_delete=models.SET_NULL, null=True, blank=True, related_name='prescription_items')
    drug_name = models.CharField(max_length=255)
    strength = models.CharField(max_length=100, blank=True, null=True)
    dosage_form = models.CharField(max_length=100, blank=True, null=True)
    dose = models.CharField(max_length=100, blank=True, null=True)
    frequency = models.CharField(max_length=100, blank=True, null=True)
    route = models.CharField(max_length=100, blank=True, null=True)
    duration_days = models.IntegerField(null=True, blank=True)
    quantity = models.IntegerField(default=1)
    dispensed_quantity = models.IntegerField(default=0)
    is_substituted = models.BooleanField(default=False)
    batch_number = models.CharField(max_length=100, blank=True, null=True)
    dispensed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dispensed_prescription_items'
    )
    dispensed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.drug_name} ({self.quantity}) - Rx {self.prescription.rx_number}"


class InventoryItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    drug = models.ForeignKey(Drug, on_delete=models.SET_NULL, null=True, blank=True, related_name='inventory_items')
    item_name = models.CharField(max_length=255)
    item_type = models.CharField(max_length=100, blank=True, null=True)
    unit_of_measure = models.CharField(max_length=50, blank=True, null=True)
    current_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reorder_level = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reorder_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    department = models.ForeignKey(
        'users.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_items'
    )

    def __str__(self):
        return self.item_name


class InventoryBatch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='batches')
    batch_number = models.CharField(max_length=100)
    lot_number = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    remaining = models.DecimalField(max_digits=12, decimal_places=2)
    expiry_date = models.DateField()
    supplier_id = models.CharField(max_length=100, blank=True, null=True)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2)
    received_at = models.DateTimeField()

    def __str__(self):
        return f"{self.inventory_item.item_name} - Batch {self.batch_number}"


class StockMovement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='movements')
    batch = models.ForeignKey(InventoryBatch, on_delete=models.SET_NULL, null=True, blank=True, related_name='movements')
    movement_type = models.CharField(max_length=50)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    reference_id = models.CharField(max_length=100, blank=True, null=True)
    reference_type = models.CharField(max_length=100, blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='performed_stock_movements'
    )
    performed_at = models.DateTimeField()

    def __str__(self):
        return f"{self.movement_type} {self.quantity} of {self.inventory_item.item_name}"
