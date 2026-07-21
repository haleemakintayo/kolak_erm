from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from .models import Encounter, VitalSign, Diagnosis


class VitalSignInline(StackedInline):
    model = VitalSign
    extra = 0


class DiagnosisInline(TabularInline):
    model = Diagnosis
    extra = 1


@admin.register(Encounter)
class EncounterAdmin(ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'encounter_type', 'encounter_date', 'status', 'signed_at', 'signed_by')
    list_filter = ('encounter_type', 'status', 'encounter_date')
    search_fields = ('patient__patient_id', 'patient__first_name', 'patient__last_name', 'doctor__first_name', 'doctor__last_name')
    inlines = [VitalSignInline, DiagnosisInline]
    readonly_fields = ('signed_at', 'signed_by')

    fieldsets = (
        ('Overview', {'fields': ('patient', 'doctor', 'appointment', 'queue_entry', 'encounter_type', 'encounter_date', 'status')}),
        ('SOAP Notes', {'fields': ('chief_complaint', 'subjective_note', 'objective_note', 'assessment_note', 'plan_note')}),
        ('Signatures', {'fields': ('signed_at', 'signed_by')}),
    )


@admin.register(VitalSign)
class VitalSignAdmin(ModelAdmin):
    list_display = ('patient', 'encounter', 'systolic_bp', 'diastolic_bp', 'heart_rate', 'temperature', 'oxygen_saturation', 'recorded_at')
    list_filter = ('recorded_at',)
    search_fields = ('patient__patient_id', 'patient__first_name', 'patient__last_name')


@admin.register(Diagnosis)
class DiagnosisAdmin(ModelAdmin):
    list_display = ('icd10_code', 'icd10_name', 'patient', 'encounter', 'diagnosis_type', 'onset_date')
    list_filter = ('diagnosis_type', 'onset_date')
    search_fields = ('icd10_code', 'icd10_name', 'patient__patient_id', 'patient__first_name', 'patient__last_name')
