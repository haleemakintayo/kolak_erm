import uuid
from django.db import models
from django.conf import settings


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=100, blank=True, null=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    priority = models.CharField(max_length=50, default='Normal')
    recipient_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    recipient_phone = models.CharField(max_length=20, blank=True, null=True)
    recipient_email = models.EmailField(blank=True, null=True)
    channels = models.JSONField(default=list, blank=True)
    in_app_sent = models.BooleanField(default=False)
    sms_status = models.CharField(max_length=50, blank=True, null=True)
    email_status = models.CharField(max_length=50, blank=True, null=True)
    read_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    link = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"[{self.priority}] {self.title} -> {self.recipient_user}"
