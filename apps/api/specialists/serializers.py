from rest_framework import serializers
from .models import *


class SpecialistCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialistCategory
        fields = '__all__'


class SpecialistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialist
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class Common_ConsultationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommonConsultation
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    date_time = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S')

    class Meta:
        model = Appointment
        fields = '__all__'
class DiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagnosis
        fields = '__all__'

class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = '__all__'

class SpecialistFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialistFeedback
        fields = '__all__'
