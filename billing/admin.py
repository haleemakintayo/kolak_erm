from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import HMOProvider, PatientHMOEnrollment, Invoice, InvoiceItem, Payment, InsuranceClaim


class InvoiceItemInline(TabularInline):
    model = InvoiceItem
    extra = 1


class PaymentInline(TabularInline):
    model = Payment
    extra = 0


@admin.register(HMOProvider)
class HMOProviderAdmin(ModelAdmin):
    list_display = ('name', 'code', 'contact_email', 'contact_phone', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code', 'contact_email')


@admin.register(PatientHMOEnrollment)
class PatientHMOEnrollmentAdmin(ModelAdmin):
    list_display = ('patient', 'hmo_provider', 'hmo_number', 'plan_name', 'valid_from', 'valid_until', 'is_active')
    list_filter = ('is_active', 'hmo_provider')
    search_fields = ('patient__patient_id', 'patient__first_name', 'patient__last_name', 'hmo_number', 'plan_name')


@admin.register(Invoice)
class InvoiceAdmin(ModelAdmin):
    list_display = ('invoice_number', 'patient', 'invoice_date', 'subtotal', 'discount_amount', 'hmo_amount', 'patient_amount', 'paid_amount', 'balance_due', 'status')
    list_filter = ('status', 'invoice_date')
    search_fields = ('invoice_number', 'patient__patient_id', 'patient__first_name', 'patient__last_name')
    inlines = [InvoiceItemInline, PaymentInline]


@admin.register(InvoiceItem)
class InvoiceItemAdmin(ModelAdmin):
    list_display = ('description', 'invoice', 'item_type', 'quantity', 'unit_price', 'total', 'hmo_covered', 'patient_total')
    list_filter = ('item_type',)
    search_fields = ('description', 'invoice__invoice_number')


@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ('receipt_number', 'patient', 'invoice', 'amount', 'payment_method', 'processed_by', 'created_at')
    list_filter = ('payment_method', 'created_at')
    search_fields = ('receipt_number', 'reference_number', 'patient__patient_id', 'patient__first_name', 'patient__last_name')


@admin.register(InsuranceClaim)
class InsuranceClaimAdmin(ModelAdmin):
    list_display = ('claim_number', 'patient', 'invoice', 'hmo_provider', 'amount_claimed', 'amount_approved', 'amount_paid', 'status', 'submitted_at')
    list_filter = ('status', 'hmo_provider', 'submitted_at')
    search_fields = ('claim_number', 'patient__patient_id', 'patient__first_name', 'patient__last_name')
