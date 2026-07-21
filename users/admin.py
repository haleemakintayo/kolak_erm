from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from unfold.forms import UserChangeForm, UserCreationForm, AdminPasswordChangeForm
from .models import Department, Permission, Role, User


@admin.register(Department)
class DepartmentAdmin(ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Permission)
class PermissionAdmin(ModelAdmin):
    list_display = ('code', 'name', 'module')
    list_filter = ('module',)
    search_fields = ('code', 'name', 'module')


@admin.register(Role)
class RoleAdmin(ModelAdmin):
    list_display = ('name', 'code', 'is_system')
    list_filter = ('is_system',)
    search_fields = ('name', 'code')
    filter_horizontal = ('permissions',)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'department', 'status', 'is_staff', 'is_active')
    list_filter = ('status', 'role', 'department', 'is_staff', 'is_active', 'two_factor_enabled')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'employee_id', 'phone')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'employee_id')}),
        ('Organization & Roles', {'fields': ('role', 'department', 'status')}),
        ('Security & 2FA', {'fields': ('two_factor_enabled', 'two_factor_secret', 'failed_login_attempts', 'locked_until', 'must_change_password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'last_login_at', 'date_joined', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at', 'last_login_at')
