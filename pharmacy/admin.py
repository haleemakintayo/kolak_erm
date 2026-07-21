from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Drug, Prescription, PrescriptionItem, InventoryItem, InventoryBatch, StockMovement


class PrescriptionItemInline(TabularInline):
    model = PrescriptionItem
    extra = 1


class InventoryBatchInline(TabularInline):
    model = InventoryBatch
    extra = 1


@admin.register(Drug)
class DrugAdmin(ModelAdmin):
    list_display = ('name', 'generic_name', 'brand_name', 'strength', 'dosage_form', 'category', 'is_controlled', 'is_active')
    list_filter = ('category', 'is_controlled', 'is_active', 'dosage_form')
    search_fields = ('name', 'generic_name', 'brand_name', 'atc_code')


@admin.register(Prescription)
class PrescriptionAdmin(ModelAdmin):
    list_display = ('rx_number', 'patient', 'encounter', 'prescribed_by', 'status', 'signed_at')
    list_filter = ('status', 'signed_at')
    search_fields = ('rx_number', 'patient__patient_id', 'patient__first_name', 'patient__last_name', 'prescribed_by__username')
    inlines = [PrescriptionItemInline]


@admin.register(PrescriptionItem)
class PrescriptionItemAdmin(ModelAdmin):
    list_display = ('drug_name', 'prescription', 'dose', 'frequency', 'quantity', 'dispensed_quantity', 'is_substituted', 'dispensed_by', 'dispensed_at')
    list_filter = ('is_substituted', 'dispensed_at')
    search_fields = ('drug_name', 'prescription__rx_number', 'batch_number')


@admin.register(InventoryItem)
class InventoryItemAdmin(ModelAdmin):
    list_display = ('item_name', 'item_type', 'unit_of_measure', 'current_stock', 'reorder_level', 'cost_price', 'selling_price', 'department')
    list_filter = ('item_type', 'department')
    search_fields = ('item_name', 'drug__name')
    inlines = [InventoryBatchInline]


@admin.register(InventoryBatch)
class InventoryBatchAdmin(ModelAdmin):
    list_display = ('batch_number', 'inventory_item', 'quantity', 'remaining', 'expiry_date', 'cost_price', 'received_at')
    list_filter = ('expiry_date', 'received_at')
    search_fields = ('batch_number', 'lot_number', 'inventory_item__item_name')


@admin.register(StockMovement)
class StockMovementAdmin(ModelAdmin):
    list_display = ('inventory_item', 'batch', 'movement_type', 'quantity', 'balance_after', 'performed_by', 'performed_at')
    list_filter = ('movement_type', 'performed_at')
    search_fields = ('inventory_item__item_name', 'reference_id', 'reason')
