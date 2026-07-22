from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import User, Department, Role, Permission
from .serializers import (
    UserSerializer,
    UserCreateUpdateSerializer,
    DoctorListSerializer,
    RoleSerializer,
    DepartmentSerializer,
    PermissionSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    """
    Manage hospital staff members (User CRUD).
    Filterable by department, role, status, and search query.
    """
    queryset = User.objects.select_related('department', 'role').all().order_by('-created_at')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UserCreateUpdateSerializer
        return UserSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(department_id=department)

        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role_id=role)

        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status__iexact=status_param)

        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() in ['true', '1'])

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(username__icontains=search) |
                Q(employee_id__icontains=search) |
                Q(phone__icontains=search)
            )

        return queryset

    @extend_schema(
        request=None,
        responses={200: UserSerializer},
        description="Toggle staff account status between Active and Inactive."
    )
    @action(detail=True, methods=['post'], url_path='toggle-status')
    def toggle_status(self, request, pk=None):
        user = self.get_object()
        user.is_active = not user.is_active
        user.status = 'Active' if user.is_active else 'Inactive'
        user.save()
        return Response({
            'message': f"User account is now {'active' if user.is_active else 'inactive'}.",
            'data': UserSerializer(user).data
        })


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


class RoleViewSet(viewsets.ModelViewSet):
    """Manage hospital roles and permissions."""
    queryset = Role.objects.prefetch_related('permissions', 'users').all().order_by('name')
    serializer_class = RoleSerializer
    search_fields = ['name', 'code']


class DepartmentViewSet(viewsets.ModelViewSet):
    """Manage hospital departments."""
    queryset = Department.objects.prefetch_related('users').all().order_by('name')
    serializer_class = DepartmentSerializer
    search_fields = ['name', 'description']


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """List available system permissions."""
    queryset = Permission.objects.all().order_by('module', 'code')
    serializer_class = PermissionSerializer
    search_fields = ['code', 'name', 'module']
