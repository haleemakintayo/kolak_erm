from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import LabTestCatalog, LabRequest, LabRequestTest, LabResult


class LabRequestTestInline(TabularInline):
    model = LabRequestTest
    extra = 1


class LabResultInline(TabularInline):
    model = LabResult
    extra = 0


@admin.register(LabTestCatalog)
class LabTestCatalogAdmin(ModelAdmin):
    list_display = ('code', 'name', 'category', 'sample_type', 'turnaround_hours', 'unit_price', 'is_active')
    list_filter = ('category', 'sample_type', 'is_active')
    search_fields = ('code', 'name')


@admin.register(LabRequest)
class LabRequestAdmin(ModelAdmin):
    list_display = ('id', 'patient', 'encounter', 'requested_by', 'urgency', 'status', 'specimen_id', 'has_critical', 'released_at')
    list_filter = ('urgency', 'status', 'has_critical', 'released_at')
    search_fields = ('patient__patient_id', 'patient__first_name', 'patient__last_name', 'specimen_id', 'barcode')
    inlines = [LabRequestTestInline, LabResultInline]


@admin.register(LabRequestTest)
class LabRequestTestAdmin(ModelAdmin):
    list_display = ('test_name', 'lab_request', 'test_catalog', 'status')
    list_filter = ('status',)
    search_fields = ('test_name', 'lab_request__specimen_id')


@admin.register(LabResult)
class LabResultAdmin(ModelAdmin):
    list_display = ('analyte_name', 'value', 'numeric_value', 'unit', 'flag', 'is_critical', 'entered_by', 'entered_at')
    list_filter = ('flag', 'is_critical', 'entered_at')
    search_fields = ('analyte_name', 'lab_request__specimen_id')
