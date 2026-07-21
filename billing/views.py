from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import HMOProvider, PatientHMOEnrollment
from .serializers import HMOProviderSerializer, PatientHMOEnrollmentSerializer


class HMOProviderViewSet(viewsets.ModelViewSet):
    queryset = HMOProvider.objects.all().order_by('name')
    serializer_class = HMOProviderSerializer
    search_fields = ['name', 'code', 'contact_email']

    def get_queryset(self):
        queryset = super().get_queryset()
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() in ['true', '1'])
        return queryset


class PatientHMOEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = PatientHMOEnrollment.objects.select_related('patient', 'hmo_provider').all().order_by('-id')
    serializer_class = PatientHMOEnrollmentSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Query filters
        patient_param = self.request.query_params.get('patient')
        if patient_param:
            queryset = queryset.filter(
                models_q_patient(patient_param)
            )

        hmo_provider_param = self.request.query_params.get('hmo_provider')
        if hmo_provider_param:
            queryset = queryset.filter(hmo_provider_id=hmo_provider_param)

        is_active_param = self.request.query_params.get('is_active')
        if is_active_param is not None:
            queryset = queryset.filter(is_active=is_active_param.lower() in ['true', '1'])

        search_param = self.request.query_params.get('search')
        if search_param:
            queryset = queryset.filter(
                models_q_search(search_param)
            )

        return queryset

    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        enrollment = self.get_object()
        enrollment.is_active = not enrollment.is_active
        enrollment.save()
        serializer = self.get_serializer(enrollment)
        return Response({
            "message": f"Enrollment is now {'active' if enrollment.is_active else 'inactive'}.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


def models_q_patient(param):
    from django.db.models import Q
    import uuid
    try:
        val = uuid.UUID(param)
        return Q(patient__id=val)
    except (ValueError, AttributeError):
        return Q(patient__patient_id__iexact=param)


def models_q_search(query):
    from django.db.models import Q
    return (
        Q(hmo_number__icontains=query) |
        Q(plan_name__icontains=query) |
        Q(patient__first_name__icontains=query) |
        Q(patient__last_name__icontains=query) |
        Q(patient__patient_id__icontains=query)
    )
