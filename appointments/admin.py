from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Appointment, QueueEntry


@admin.register(Appointment)
class AppointmentAdmin(ModelAdmin):
    list_display = ('reference_number', 'patient', 'doctor', 'appointment_type', 'appointment_date', 'start_time', 'end_time', 'status')
    list_filter = ('appointment_type', 'status', 'appointment_date')
    search_fields = ('reference_number', 'patient__patient_id', 'patient__first_name', 'patient__last_name', 'doctor__first_name', 'doctor__last_name')
    readonly_fields = ('arrived_at', 'cancelled_at')

    fieldsets = (
        ('General Information', {'fields': ('reference_number', 'patient', 'doctor', 'appointment_type', 'status')}),
        ('Schedule', {'fields': ('appointment_date', 'start_time', 'end_time')}),
        ('Clinical Information', {'fields': ('chief_complaint',)}),
        ('Status & Audit', {'fields': ('arrived_at', 'cancelled_at', 'cancellation_reason')}),
    )


@admin.register(QueueEntry)
class QueueEntryAdmin(ModelAdmin):
    list_display = ('ticket_number', 'patient', 'doctor', 'priority', 'status', 'queue_date', 'arrived_at', 'called_at')
    list_filter = ('priority', 'status', 'queue_date')
    search_fields = ('ticket_number', 'patient__patient_id', 'patient__first_name', 'patient__last_name', 'doctor__first_name', 'doctor__last_name')
    readonly_fields = ('arrived_at', 'called_at')
