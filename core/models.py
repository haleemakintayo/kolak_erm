import uuid
from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    user_name = models.CharField(max_length=255, blank=True, null=True)
    user_role = models.CharField(max_length=100, blank=True, null=True)
    action = models.CharField(max_length=100)
    resource = models.CharField(max_length=100)
    resource_id = models.CharField(max_length=100, blank=True, null=True)
    before_data = models.JSONField(default=dict, blank=True, null=True)
    after_data = models.JSONField(default=dict, blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=50, default='Success')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Audit: {self.action} on {self.resource} by {self.user_name or self.user}"