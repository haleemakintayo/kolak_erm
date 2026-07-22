from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from drf_spectacular.utils import extend_schema_field
from django.contrib.auth import get_user_model
from .models import Department, Role, Permission

User = get_user_model()


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'code', 'name', 'module']


class DepartmentBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']


class DepartmentSerializer(serializers.ModelSerializer):
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'user_count']

    @extend_schema_field(serializers.IntegerField())
    def get_user_count(self, obj):
        return obj.users.count()


class RoleBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'code']


class RoleSerializer(serializers.ModelSerializer):
    permissions_detail = PermissionSerializer(source='permissions', many=True, read_only=True)
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ['id', 'name', 'code', 'permissions', 'permissions_detail', 'is_system', 'user_count']

    @extend_schema_field(serializers.IntegerField())
    def get_user_count(self, obj):
        return obj.users.count()


class UserSerializer(serializers.ModelSerializer):
    department_detail = DepartmentBriefSerializer(source='department', read_only=True)
    role_detail = RoleBriefSerializer(source='role', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'employee_id', 'role', 'role_detail', 'department',
            'department_detail', 'status', 'two_factor_enabled',
            'failed_login_attempts', 'locked_until', 'last_login_at',
            'must_change_password', 'is_active', 'is_staff', 'is_superuser',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'last_login_at',
            'failed_login_attempts', 'locked_until'
        ]

    @extend_schema_field(serializers.CharField())
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


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


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=6)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'first_name', 'last_name',
            'phone', 'employee_id', 'role', 'department', 'status',
            'is_active', 'is_staff', 'must_change_password'
        ]
        extra_kwargs = {
            'username': {'required': False, 'allow_blank': True},
            'email': {'required': True},
        }

    def _generate_employee_id(self):
        last_emp = User.objects.exclude(employee_id__isnull=True).order_by('-created_at').first()
        if last_emp and last_emp.employee_id and last_emp.employee_id.startswith('EMP-'):
            try:
                num = int(last_emp.employee_id.split('-')[1])
                return f"EMP-{num + 1:04d}"
            except (ValueError, IndexError):
                pass
        return f"EMP-{User.objects.count() + 1:04d}"

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        if not validated_data.get('username'):
            validated_data['username'] = validated_data['email']
        if not validated_data.get('employee_id'):
            validated_data['employee_id'] = self._generate_employee_id()

        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    def to_representation(self, instance):
        return UserSerializer(instance, context=self.context).data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT Serializer returning user details alongside access & refresh tokens.
    Supports login via either username or email.
    """
    def validate(self, attrs):
        username_or_email = attrs.get(self.username_field)
        if username_or_email and '@' in username_or_email:
            try:
                user_obj = User.objects.get(email__iexact=username_or_email)
                attrs[self.username_field] = user_obj.username
            except User.DoesNotExist:
                pass

        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=6)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value
