from .models import *
from rest_framework import generics
from django.db.models import Sum
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from ..specialists.models import SpecialistFeedback, Specialist, Appointment, Transaction, Diagnosis, Prescription
from ..specialists.serializers import SpecialistFeedbackSerializer, AppointmentSerializer, TransactionSerializer, \
    DiagnosisSerializer
from ..info.models import Notification
from ..info.serializers import NotificationSerializer
from datetime import datetime
from django.utils.timezone import make_aware


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createPatientAccount(request):
    try:
        received = request.data
        received['user'] = request.user.id
        serializer = PatientSerializer(data=received)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print('Validation Error:', serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        error_message = f"Error retrieving Item: {str(e)}"
        return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ======================PATIENT DATA START========================

class PatientListView(generics.ListCreateAPIView):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Patient.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"detail": "Patient data not found"}, status=status.HTTP_404_NOT_FOUND)

        patient = queryset.first()
        current_user = request.user
        feedbacks = SpecialistFeedback.objects.filter(patient=patient)
        appointments = Appointment.objects.filter(patient=patient)
        transactions = Transaction.objects.filter(patient=patient)
        notifications = Notification.objects.filter(user=current_user)
        diagnosis = Diagnosis.objects.filter(appointment__patient=patient).order_by('-created_at')



        now = make_aware(datetime.now())
        active_appointments = appointments.filter(date_time__lt=now, status='accepted').count()
        total_consultations = appointments.count()
        accepted_appointments = appointments.filter(status='Accepted').count()
        pending_appointments = appointments.filter(status='Pending').count()
        cancelled_appointments = appointments.filter(status='Cancelled').count()
        rejected_appointments = appointments.filter(status='Rejected').count()

        total_amount = transactions.aggregate(total_amount=Sum('amount'))['total_amount']
        total_due = transactions.filter(status='Due').aggregate(total_due=Sum('amount'))['total_due']
        total_paid = transactions.filter(status='Paid').aggregate(total_paid=Sum('amount'))['total_paid']
        total_cancelled = transactions.filter(status='Cancelled').aggregate(total_cancelled=Sum('amount'))[
            'total_cancelled']

        feedback_serializer = SpecialistFeedbackSerializer(feedbacks, many=True)
        transaction_serializer = TransactionSerializer(transactions, many=True)
        appointment_serializer = AppointmentSerializer(appointments, many=True)
        notification_serializer = NotificationSerializer(notifications, many=True)
        diagnosis_serializer = DiagnosisSerializer(diagnosis, many=True)

        data = {
            'patient': self.get_serializer(patient).data,
            'total_consultations': total_consultations,
            'active_appointments': active_appointments,
            'accepted_appointments': accepted_appointments,
            'pending_appointments': pending_appointments,
            'cancelled_appointments': cancelled_appointments,
            'rejected_appointments': rejected_appointments,

            'feedbacks': [],
            'appointments': [],
            'transactions': [],
            'transaction_count': [],
            'diagnosis': [],
            'messages': [],
        }

        transaction_count_data = {
            'total_transactions': total_amount if total_amount is not None else 0,
            'total_paid': total_paid if total_paid is not None else 0,
            'total_due': total_due if total_due is not None else 0,
            'total_cancelled': total_cancelled if total_cancelled is not None else 0,
        }
        data['transaction_count'].append(transaction_count_data)

        # Process diagnosis
        for diagnosis in diagnosis_serializer.data:
            diagnosis_id = diagnosis['id']
            appointment_id = diagnosis['appointment']
            prescription = Prescription.objects.get(diagnosis__id=diagnosis_id)
            appointment = Appointment.objects.get(id=appointment_id)
            diagnosis['prescription'] = {
                'id': prescription.id,
                'prescription_text': prescription.prescription_text,
                'created_at': prescription.created_at
            }
            diagnosis['appointment'] = {
                'id': appointment.id,
                'patient_name': appointment.patient.full_name,
                'patient_birth_date': appointment.patient.date_of_birth,
                'patient_gender': appointment.patient.gender,
                'specialist_name': appointment.specialist.full_name,
                'specialist_category': appointment.specialist.category.name,
                'specialist_contact': appointment.specialist.contact_phone,
                'concern': appointment.concern,
                'date_time':  appointment.date_time
            }
            data['diagnosis'].append(diagnosis)

        # Process feedbacks
        for feedback in feedback_serializer.data:
            specialist = Specialist.objects.get(id=feedback['specialist'])
            feedback['specialist'] = {
                'id': specialist.id,
                'full_name': specialist.full_name,
                'profile_picture': specialist.profile_picture.url if specialist.profile_picture else None
            }
            data['feedbacks'].append(feedback)

        #Process Notifications:
        for notification in notification_serializer.data:
            notification_data = {
                'message': notification['message'],
                'subject': notification['subject'],
                'update_at': notification['updated_at']
            }

            data['messages'].append(notification_data)

        # Process transactions
        for transaction in transaction_serializer.data:
            appointment_id = transaction['appointment']
            appointment = Appointment.objects.get(id=appointment_id)
            transaction_data = {
                'id': transaction['id'],
                'amount': transaction['amount'],
                'payment_method': transaction['payment_method'],
                'reference': transaction['reference'],
                'timestamp': transaction['timestamp'],
                'status': transaction['status'],

                'transaction_appointment': {
                    'id': appointment.id,
                    'transaction_specialist': {
                        'id': appointment.specialist.id,
                        'full_name': appointment.specialist.full_name,
                        'profile_picture': appointment.specialist.profile_picture.url if appointment.specialist.profile_picture else None
                    },

                }
            }
            data['transactions'].append(transaction_data)

        # Process appointments
        for appointment in appointment_serializer.data:
            specialist_id = appointment['specialist']
            specialist = Specialist.objects.get(id=specialist_id)
            appointment_data = {
                'id': appointment['id'],
                'specialist': {
                    'specialist_id': specialist.id,
                    'full_name': specialist.full_name,
                    'profile_picture': specialist.profile_picture.url if specialist.profile_picture else None
                },
                'date_time': appointment['date_time'],
                'concern': appointment['concern'],
                'status': appointment['status'],
                'payment_status': appointment['payment_status'],
                'cancel_reason': appointment['cancel_reason'],
                'reject_reason': appointment['reject_reason'],
                'updated_at': appointment['updated_at']
            }
            data['appointments'].append(appointment_data)

        return Response(data, status=status.HTTP_200_OK)


#===========Update profile============
class PatientRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Patient.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()
# ======================PATIENT DATA END========================

