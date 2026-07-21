from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import User, Department, Role


class DepartmentBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']


class RoleBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'code']


class DoctorListSerializer(serializers.ModelSerializer):
    department_detail = DepartmentBriefSerializer(source='department', read_only=True)
    role_detail = RoleBriefSerializer(source='role', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'employee_id', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'department', 'department_detail',
            'role', 'role_detail', 'status'
        ]

    @extend_schema_field(serializers.CharField())
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
