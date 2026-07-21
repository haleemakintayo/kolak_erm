from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django.db.models import Q
from .models import User
from .serializers import DoctorListSerializer


class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve doctors/specialists available in the hospital."""
    serializer_class = DoctorListSerializer

    def get_queryset(self):
        queryset = User.objects.filter(
            is_active=True, status='Active'
        ).select_related('department', 'role').order_by('first_name', 'last_name')

        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(department_id=department)

        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role_id=role)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(employee_id__icontains=search) |
                Q(email__icontains=search)
            )

        return queryset
