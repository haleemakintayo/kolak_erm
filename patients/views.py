from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Patient
from .serializers import PatientSerializer
from billing.models import PatientHMOEnrollment
from billing.serializers import PatientHMOEnrollmentSerializer


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all().order_by('-created_at')
    serializer_class = PatientSerializer
    search_fields = ['patient_id', 'first_name', 'last_name', 'phone', 'email', 'national_id']

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
