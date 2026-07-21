from django.contrib import admin
from unfold.admin import ModelAdmin, StackedInline
from .models import RadiologyRequest, RadiologyReport


class RadiologyReportInline(StackedInline):
    model = RadiologyReport
    extra = 0


@admin.register(RadiologyRequest)
class RadiologyRequestAdmin(ModelAdmin):
    list_display = ('id', 'patient', 'modality', 'body_part', 'urgency', 'status', 'requested_by', 'scheduled_at')
    list_filter = ('modality', 'urgency', 'status', 'scheduled_at')
    search_fields = ('patient__patient_id', 'patient__first_name', 'patient__last_name', 'modality', 'body_part')
    inlines = [RadiologyReportInline]


@admin.register(RadiologyReport)
class RadiologyReportAdmin(ModelAdmin):
    list_display = ('radiology_request', 'critical_finding', 'reported_by', 'reported_at', 'digitally_signed')
    list_filter = ('critical_finding', 'digitally_signed', 'reported_at')
    search_fields = ('radiology_request__patient__patient_id', 'findings', 'impression')
