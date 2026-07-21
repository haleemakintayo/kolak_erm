from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ('title', 'type', 'priority', 'recipient_user', 'in_app_sent', 'sms_status', 'email_status', 'read_at')
    list_filter = ('type', 'priority', 'in_app_sent', 'sms_status', 'email_status', 'read_at')
    search_fields = ('title', 'message', 'recipient_user__username', 'recipient_phone', 'recipient_email')
    readonly_fields = ('read_at',)
