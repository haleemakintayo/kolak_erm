from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Patient
from .serializers import (
    PatientSerializer,
    PatientRegistrationSerializer,
    PatientSearchSerializer,
)
from billing.models import PatientHMOEnrollment
from billing.serializers import PatientHMOEnrollmentSerializer


class PatientViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for patients. Supports registration with nested
    allergies & next-of-kin, search, and HMO enrollment management.
    """
    queryset = Patient.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'create':
            return PatientRegistrationSerializer
        if self.action == 'search_patients':
            return PatientSearchSerializer
        return PatientSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        gender = self.request.query_params.get('gender')
        if gender:
            queryset = queryset.filter(gender__iexact=gender)

        blood_group = self.request.query_params.get('blood_group')
        if blood_group:
            queryset = queryset.filter(blood_group__iexact=blood_group)

        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status__iexact=status_param)

        is_vip = self.request.query_params.get('is_vip')
        if is_vip is not None:
            queryset = queryset.filter(is_vip=is_vip.lower() in ['true', '1'])

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(patient_id__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(phone__icontains=search) |
                Q(email__icontains=search) |
                Q(national_id__icontains=search)
            )

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(name='q', type=str, required=True, description='Search term (name, phone, patient_id)'),
        ],
        responses={200: PatientSearchSerializer(many=True)},
        description='Quick search endpoint for front desk patient lookup.',
    )
    @action(detail=False, methods=['get'], url_path='search')
    def search_patients(self, request):
        q = request.query_params.get('q', '').strip()
        if not q:
            return Response(
                {'error': 'Query parameter "q" is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        patients = Patient.objects.filter(
            Q(patient_id__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(phone__icontains=q) |
            Q(email__icontains=q) |
            Q(national_id__icontains=q)
        ).order_by('first_name', 'last_name')[:20]
        serializer = PatientSearchSerializer(patients, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'], url_path='enrollments')
    def enrollments(self, request, pk=None):
        patient = self.get_object()

        if request.method == 'GET':
            enrollments = PatientHMOEnrollment.objects.filter(patient=patient).select_related('hmo_provider')
            is_active = request.query_params.get('is_active')
            if is_active is not None:
                enrollments = enrollments.filter(is_active=is_active.lower() in ['true', '1'])
            serializer = PatientHMOEnrollmentSerializer(enrollments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'POST':
            data = request.data.copy()
            data['patient'] = str(patient.id)
            serializer = PatientHMOEnrollmentSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
