from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import HMOProvider, PatientHMOEnrollment
from patients.models import Patient


class HMOProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = HMOProvider
        fields = [
            'id', 'name', 'code', 'portal_url', 'api_key',
            'contact_email', 'contact_phone', 'is_active'
        ]


class BillingPatientBriefSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ['id', 'patient_id', 'first_name', 'last_name', 'full_name', 'gender', 'phone']

    @extend_schema_field(serializers.CharField())
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class PatientHMOEnrollmentSerializer(serializers.ModelSerializer):
    hmo_provider_detail = HMOProviderSerializer(source='hmo_provider', read_only=True)
    patient_detail = BillingPatientBriefSerializer(source='patient', read_only=True)

    class Meta:
        model = PatientHMOEnrollment
        fields = [
            'id', 'patient', 'patient_detail', 'hmo_provider',
            'hmo_provider_detail', 'hmo_number', 'plan_name',
            'valid_from', 'valid_until', 'is_active'
        ]

    def validate(self, attrs):
        valid_from = attrs.get('valid_from', getattr(self.instance, 'valid_from', None))
        valid_until = attrs.get('valid_until', getattr(self.instance, 'valid_until', None))

        if valid_from and valid_until and valid_from > valid_until:
            raise serializers.ValidationError({
                "valid_until": "valid_until date must be after valid_from date."
            })
        return attrs
