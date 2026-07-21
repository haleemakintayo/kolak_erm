from datetime import date
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Appointment, QueueEntry
from .serializers import (
    AppointmentSerializer,
    AppointmentCancelSerializer,
    QueueEntrySerializer,
)


class AppointmentViewSet(viewsets.ModelViewSet):
    """Manage patient appointments — booking, cancellation, and check-in."""
    queryset = Appointment.objects.select_related('patient', 'doctor').all().order_by('-appointment_date', '-start_time')
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        patient = self.request.query_params.get('patient')
        if patient:
            from django.db.models import Q
            import uuid as _uuid
            try:
                val = _uuid.UUID(patient)
                queryset = queryset.filter(patient__id=val)
            except (ValueError, AttributeError):
                queryset = queryset.filter(patient__patient_id__iexact=patient)

        doctor = self.request.query_params.get('doctor')
        if doctor:
            queryset = queryset.filter(doctor_id=doctor)

        appointment_date = self.request.query_params.get('appointment_date')
        if appointment_date:
            queryset = queryset.filter(appointment_date=appointment_date)

        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status__iexact=status_param)

        appointment_type = self.request.query_params.get('appointment_type')
        if appointment_type:
            queryset = queryset.filter(appointment_type__icontains=appointment_type)

        return queryset

    @extend_schema(
        request=AppointmentCancelSerializer,
        responses={200: AppointmentSerializer},
        description='Cancel an appointment with an optional reason.'
    )
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        if appointment.status == 'Cancelled':
            return Response(
                {'error': 'This appointment is already cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = AppointmentCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment.status = 'Cancelled'
        appointment.cancelled_at = timezone.now()
        appointment.cancellation_reason = serializer.validated_data.get('cancellation_reason', '')
        appointment.save()
        return Response({
            'message': 'Appointment cancelled successfully.',
            'data': AppointmentSerializer(appointment).data
        })

    @extend_schema(
        request=None,
        responses={200: AppointmentSerializer},
        description='Check-in a patient for their appointment and auto-create a queue entry.'
    )
    @action(detail=True, methods=['post'], url_path='check-in')
    def check_in(self, request, pk=None):
        appointment = self.get_object()
        if appointment.status == 'Cancelled':
            return Response(
                {'error': 'Cannot check-in a cancelled appointment.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if appointment.arrived_at:
            return Response(
                {'error': 'Patient has already checked in for this appointment.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        appointment.arrived_at = timezone.now()
        appointment.status = 'Checked-In'
        appointment.save()

        # Auto-create queue entry
        queue_date = appointment.appointment_date or date.today()
        last_ticket = QueueEntry.objects.filter(
            queue_date=queue_date
        ).order_by('-ticket_number').values_list('ticket_number', flat=True).first()

        queue_entry = QueueEntry.objects.create(
            patient=appointment.patient,
            appointment=appointment,
            doctor=appointment.doctor,
            ticket_number=(last_ticket or 0) + 1,
            priority='Normal',
            status='Waiting',
            queue_date=queue_date,
            arrived_at=timezone.now(),
        )

        return Response({
            'message': 'Patient checked in and added to queue.',
            'appointment': AppointmentSerializer(appointment).data,
            'queue_entry': QueueEntrySerializer(queue_entry).data
        })


class QueueEntryViewSet(viewsets.ModelViewSet):
    """Manage the patient waiting queue — walk-ins, calling next, and completing."""
    queryset = QueueEntry.objects.select_related('patient', 'doctor', 'appointment').all().order_by('queue_date', 'ticket_number')
    serializer_class = QueueEntrySerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        doctor = self.request.query_params.get('doctor')
        if doctor:
            queryset = queryset.filter(doctor_id=doctor)

        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status__iexact=status_param)

        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority__iexact=priority)

        queue_date = self.request.query_params.get('queue_date')
        if queue_date:
            queryset = queryset.filter(queue_date=queue_date)
        else:
            # Default to today's queue
            queryset = queryset.filter(queue_date=date.today())

        return queryset

    @extend_schema(
        request=None,
        responses={200: QueueEntrySerializer},
        description='Call the next patient — sets called_at timestamp and updates status to In-Consultation.'
    )
    @action(detail=True, methods=['post'], url_path='call-next')
    def call_next(self, request, pk=None):
        entry = self.get_object()
        if entry.status != 'Waiting':
            return Response(
                {'error': f'Cannot call a queue entry with status "{entry.status}".'},
                status=status.HTTP_400_BAD_REQUEST
            )
        entry.called_at = timezone.now()
        entry.status = 'In-Consultation'
        entry.save()
        return Response({
            'message': f'Patient (Ticket #{entry.ticket_number}) called for consultation.',
            'data': QueueEntrySerializer(entry).data
        })

    @extend_schema(
        request=None,
        responses={200: QueueEntrySerializer},
        description='Mark a queue entry as completed.'
    )
    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        entry = self.get_object()
        if entry.status == 'Completed':
            return Response(
                {'error': 'This queue entry is already completed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        entry.status = 'Completed'
        entry.save()
        return Response({
            'message': f'Queue entry (Ticket #{entry.ticket_number}) marked as completed.',
            'data': QueueEntrySerializer(entry).data
        })
