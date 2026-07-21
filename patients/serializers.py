from rest_framework import serializers
from .models import Patient, PatientAllergy, PatientNextOfKin


class PatientAllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientAllergy
        fields = '__all__'


class PatientNextOfKinSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientNextOfKin
        fields = '__all__'


class PatientSerializer(serializers.ModelSerializer):
    allergies = PatientAllergySerializer(many=True, read_only=True)
    next_of_kin = PatientNextOfKinSerializer(many=True, read_only=True)

    class Meta:
        model = Patient
        fields = '__all__'
