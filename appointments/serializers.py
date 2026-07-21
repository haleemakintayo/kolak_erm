import uuid
from datetime import date
from django.utils import timezone
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Appointment, QueueEntry
from patients.models import Patient
from django.conf import settings


class AppointmentPatientBriefSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ['id', 'patient_id', 'first_name', 'last_name', 'full_name', 'phone']

    @extend_schema_field(serializers.CharField())
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class DoctorBriefSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    full_name = serializers.SerializerMethodField()
    employee_id = serializers.CharField()

    @extend_schema_field(serializers.CharField())
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class AppointmentSerializer(serializers.ModelSerializer):
    patient_detail = AppointmentPatientBriefSerializer(source='patient', read_only=True)
    doctor_detail = DoctorBriefSerializer(source='doctor', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_detail', 'doctor', 'doctor_detail',
            'reference_number', 'appointment_type', 'appointment_date',
            'start_time', 'end_time', 'chief_complaint', 'status',
            'arrived_at', 'cancelled_at', 'cancellation_reason'
        ]
        read_only_fields = ['reference_number', 'arrived_at', 'cancelled_at']

    def validate(self, attrs):
        doctor = attrs.get('doctor')
        appointment_date = attrs.get('appointment_date')
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError({
                'end_time': 'End time must be after start time.'
            })

        # Check for double-booking (same doctor, same date, overlapping times)
        if doctor and appointment_date and start_time and end_time:
            overlapping = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date,
                status__in=['Scheduled', 'Confirmed'],
                start_time__lt=end_time,
                end_time__gt=start_time,
            )
            if self.instance:
                overlapping = overlapping.exclude(pk=self.instance.pk)
            if overlapping.exists():
                raise serializers.ValidationError(
                    'This doctor already has an appointment during this time slot.'
                )

        return attrs

    def create(self, validated_data):
        # Auto-generate reference number
        validated_data['reference_number'] = f"APT-{uuid.uuid4().hex[:8].upper()}"
        return super().create(validated_data)


class AppointmentCancelSerializer(serializers.Serializer):
    cancellation_reason = serializers.CharField(required=False, allow_blank=True)


class QueueEntrySerializer(serializers.ModelSerializer):
    patient_detail = AppointmentPatientBriefSerializer(source='patient', read_only=True)
    doctor_detail = DoctorBriefSerializer(source='doctor', read_only=True)

    class Meta:
        model = QueueEntry
        fields = [
            'id', 'patient', 'patient_detail', 'appointment',
            'doctor', 'doctor_detail', 'ticket_number', 'priority',
            'status', 'queue_date', 'arrived_at', 'called_at'
        ]
        read_only_fields = ['ticket_number', 'arrived_at', 'called_at']

    def create(self, validated_data):
        queue_date = validated_data.get('queue_date', date.today())
        # Auto-increment ticket_number per queue_date
        last_ticket = QueueEntry.objects.filter(
            queue_date=queue_date
        ).order_by('-ticket_number').values_list('ticket_number', flat=True).first()
        validated_data['ticket_number'] = (last_ticket or 0) + 1
        validated_data['arrived_at'] = timezone.now()
        return super().create(validated_data)
