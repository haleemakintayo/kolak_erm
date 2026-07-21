from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Ward, Bed, Admission


class BedInline(TabularInline):
    model = Bed
    extra = 1


@admin.register(Ward)
class WardAdmin(ModelAdmin):
    list_display = ('name', 'type', 'capacity', 'head_nurse', 'floor', 'is_active')
    list_filter = ('type', 'floor', 'is_active')
    search_fields = ('name',)
    inlines = [BedInline]


@admin.register(Bed)
class BedAdmin(ModelAdmin):
    list_display = ('bed_number', 'ward', 'room_number', 'bed_type', 'daily_rate', 'status')
    list_filter = ('status', 'bed_type', 'ward')
    search_fields = ('bed_number', 'room_number', 'ward__name')


@admin.register(Admission)
class AdmissionAdmin(ModelAdmin):
    list_display = ('admission_number', 'patient', 'bed', 'ward', 'admission_type', 'attending_doctor', 'admission_date', 'actual_discharge_date', 'status')
    list_filter = ('admission_type', 'status', 'ward', 'admission_date')
    search_fields = ('admission_number', 'patient__patient_id', 'patient__first_name', 'patient__last_name')
