from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(ModelAdmin):
    list_display = ('action', 'resource', 'resource_id', 'user_name', 'user_role', 'ip_address', 'status', 'created_at')
    list_filter = ('action', 'resource', 'status', 'created_at')
    search_fields = ('action', 'resource', 'resource_id', 'user_name', 'user_role', 'ip_address')
    readonly_fields = ('id', 'user', 'user_name', 'user_role', 'action', 'resource', 'resource_id', 'before_data', 'after_data', 'ip_address', 'user_agent', 'status', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
