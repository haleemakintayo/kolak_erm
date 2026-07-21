from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Patient, PatientAllergy, PatientNextOfKin


class PatientAllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientAllergy
        fields = ['id', 'allergen', 'allergen_type', 'severity', 'reaction']


class PatientNextOfKinSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientNextOfKin
        fields = ['id', 'name', 'relationship', 'phone', 'is_primary']


class PatientSerializer(serializers.ModelSerializer):
    allergies = PatientAllergySerializer(many=True, read_only=True)
    next_of_kin = PatientNextOfKinSerializer(many=True, read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    @extend_schema_field(serializers.CharField())
    def get_full_name(self, obj):
        parts = [obj.first_name, obj.other_names, obj.last_name]
        return ' '.join(p for p in parts if p).strip()


class PatientRegistrationSerializer(serializers.ModelSerializer):
    """
    Writable serializer that accepts nested allergies and next_of_kin
    during patient registration. Auto-generates patient_id.
    """
    allergies = PatientAllergySerializer(many=True, required=False)
    next_of_kin = PatientNextOfKinSerializer(many=True, required=False)

    class Meta:
        model = Patient
        fields = [
            'id', 'patient_id', 'first_name', 'last_name', 'other_names',
            'date_of_birth', 'gender', 'blood_group', 'genotype',
            'phone', 'alt_phone', 'email', 'address', 'city', 'state', 'lga',
            'national_id', 'photo_url', 'status', 'is_vip', 'is_deceased',
            'registered_by', 'allergies', 'next_of_kin'
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'patient_id': {'required': False, 'allow_blank': True},
        }

    def _generate_patient_id(self):
        """Generate a sequential patient ID like PAT-00001."""
        last_patient = Patient.objects.order_by('-created_at').first()
        if last_patient and last_patient.patient_id.startswith('PAT-'):
            try:
                last_num = int(last_patient.patient_id.split('-')[1])
                return f"PAT-{last_num + 1:05d}"
            except (ValueError, IndexError):
                pass
        return f"PAT-{Patient.objects.count() + 1:05d}"

    def create(self, validated_data):
        allergies_data = validated_data.pop('allergies', [])
        next_of_kin_data = validated_data.pop('next_of_kin', [])

        # Auto-generate patient_id if not provided
        if not validated_data.get('patient_id'):
            validated_data['patient_id'] = self._generate_patient_id()

        patient = Patient.objects.create(**validated_data)

        for allergy_data in allergies_data:
            PatientAllergy.objects.create(patient=patient, **allergy_data)

        for kin_data in next_of_kin_data:
            PatientNextOfKin.objects.create(patient=patient, **kin_data)

        return patient

    def to_representation(self, instance):
        """Use the read serializer for response output."""
        return PatientSerializer(instance, context=self.context).data


class PatientSearchSerializer(serializers.ModelSerializer):
    """Lightweight serializer for search results."""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            'id', 'patient_id', 'first_name', 'last_name', 'full_name',
            'gender', 'phone', 'email', 'date_of_birth', 'status', 'is_vip'
        ]

    @extend_schema_field(serializers.CharField())
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
