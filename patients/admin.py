from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Patient, PatientAllergy, PatientNextOfKin


class PatientAllergyInline(TabularInline):
    model = PatientAllergy
    extra = 1


class PatientNextOfKinInline(TabularInline):
    model = PatientNextOfKin
    extra = 1


@admin.register(Patient)
class PatientAdmin(ModelAdmin):
    list_display = ('patient_id', 'first_name', 'last_name', 'gender', 'phone', 'blood_group', 'status', 'is_vip', 'is_deceased', 'created_at')
    list_filter = ('gender', 'blood_group', 'genotype', 'status', 'is_vip', 'is_deceased', 'created_at')
    search_fields = ('patient_id', 'first_name', 'last_name', 'phone', 'email', 'national_id')
    inlines = [PatientAllergyInline, PatientNextOfKinInline]
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Patient Identity', {'fields': ('patient_id', 'first_name', 'last_name', 'other_names', 'photo_url')}),
        ('Demographics', {'fields': ('date_of_birth', 'gender', 'blood_group', 'genotype', 'national_id')}),
        ('Contact Information', {'fields': ('phone', 'alt_phone', 'email', 'address', 'city', 'state', 'lga')}),
        ('Status & Flags', {'fields': ('status', 'is_vip', 'is_deceased', 'registered_by')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(PatientAllergy)
class PatientAllergyAdmin(ModelAdmin):
    list_display = ('patient', 'allergen', 'allergen_type', 'severity')
    list_filter = ('allergen_type', 'severity')
    search_fields = ('allergen', 'patient__patient_id', 'patient__first_name', 'patient__last_name')


@admin.register(PatientNextOfKin)
class PatientNextOfKinAdmin(ModelAdmin):
    list_display = ('name', 'patient', 'relationship', 'phone', 'is_primary')
    list_filter = ('relationship', 'is_primary')
    search_fields = ('name', 'phone', 'patient__patient_id', 'patient__first_name', 'patient__last_name')
