from django.db import transaction
from rest_framework import generics
from django.core.mail import send_mail
from django.conf import settings
import base64
import logging
import requests
from rest_framework.exceptions import ValidationError
from django.db.models import Sum
from .models import *
from .serializers import *
from ..info.models import Notification
from ..info.serializers import NotificationSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.generics import ListCreateAPIView
from django.http import HttpResponse, JsonResponse
from django.utils.timezone import make_aware
from time import sleep

logger = logging.getLogger(__name__)


# Categories
def get_categories(queryset):
    try:
        serializer = SpecialistCategorySerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        error_message = f"Error retrieving categories: {str(e)}"
        return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def getAllCategories(request):
    categories = SpecialistCategory.objects.all()
    return get_categories(categories)


@api_view(['GET'])
def getCategoriesWithItems(request):
    categories = SpecialistCategory.objects.filter(total_specialists__gt=0)
    return get_categories(categories)


@api_view(['GET'])
def getCategoryById(request, category_id):
    try:
        category = get_object_or_404(SpecialistCategory, id=category_id)
        serializer = SpecialistCategorySerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        error_message = f"Error retrieving Item: {str(e)}"
        return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#=============== /CATEGORIES END===============

# =============SPECIALISTS STAR===============

# 001 Specialists filterd by category
@api_view(['GET'])
def getSpecialistByCategories(request, category_id):
    try:
        specialist = Specialist.objects.filter(category=category_id, verified=True)
        serializer = SpecialistSerializer(specialist, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        error_message = f"Error retrieving about: {str(e)}"
        return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def getSpecialistById(request, specialist_id):
    try:
        specialist = get_object_or_404(Specialist, id=specialist_id)
        serializer = SpecialistSerializer(specialist)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        error_message = f"Error retrieving Item: {str(e)}"
        return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Create Specialist
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createSpecialistAccount(request):
    try:
        received = request.data
        received['user'] = request.user.id
        serializer = SpecialistSerializer(data=received)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print('Validation Error:', serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        error_message = f"Error retrieving Item: {str(e)}"
        return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#=========Specialist Profile data ==========

class SpecialistDatalistView(generics.ListCreateAPIView):
    serializer_class = SpecialistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Specialist.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"detail": "Specialist data not found"}, status=status.HTTP_404_NOT_FOUND)

        specialist = queryset.first()
        feedbacks = SpecialistFeedback.objects.filter(specialist=specialist)
        appointments = Appointment.objects.filter(specialist=specialist)
        diagnosis = Diagnosis.objects.filter(appointment__specialist=specialist).order_by('-created_at')
        transactions = Transaction.objects.filter(appointment__specialist=specialist)
        notifications = Notification.objects.filter(user=specialist.user)
        appointments_with_diagnoses_ids = set(diagnosis.values_list('appointment_id', flat=True))

        now = make_aware(datetime.now())
        active_appointments = appointments.filter(date_time__lt=now, status='accepted').count()
        total_consultations = appointments.count()
        accepted_appointments = appointments.filter(status='accepted').count()
        pending_appointments = appointments.filter(status='pending').count()
        cancelled_appointments = appointments.filter(status='cancelled').count()
        rejected_appointments = appointments.filter(status='rejected').count()

        # Count transactions related to specialist's appointments
        total_amount = transactions.aggregate(total_amount=Sum('amount'))['total_amount']
        total_due = transactions.filter(status='Due').aggregate(total_due=Sum('amount'))['total_due']
        total_paid = transactions.filter(status='Paid').aggregate(total_paid=Sum('amount'))['total_paid']
        total_cancelled = transactions.filter(status='Cancelled').aggregate(total_cancelled=Sum('amount'))[
            'total_cancelled']
        total_transactions = transactions.count()

        feedback_serializer = SpecialistFeedbackSerializer(feedbacks, many=True)
        transaction_serializer = TransactionSerializer(transactions, many=True)
        appointment_serializer = AppointmentSerializer(appointments, many=True)
        notification_serializer = NotificationSerializer(notifications, many=True)
        diagnosis_serializer = DiagnosisSerializer(diagnosis, many=True)

        data = {
            'specialist': self.get_serializer(specialist).data,
            'appointment_count': [],
            'feedbacks': [],
            'appointments': [],
            'diagnosis': [],
            'transactions': [],
            'transaction_count': [],
            'messages': [],
        }

        appointment_count_data = {
            'total_consultations': total_consultations,
            'active_appointments': active_appointments,
            'accepted_appointments': accepted_appointments,
            'pending_appointments': pending_appointments,
            'cancelled_appointments': cancelled_appointments,
            'rejected_appointments': rejected_appointments,

        }
        data['appointment_count'].append(appointment_count_data)

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
                'concern': appointment.concern,
                'date_time': appointment.date_time
            }
            data['diagnosis'].append(diagnosis)

        transaction_count_data = {
            'total_amount': total_amount if total_amount is not None else 0,
            'total_paid': total_paid if total_paid is not None else 0.00,
            'total_due': total_due if total_due is not None else 0.00,
            'total_cancelled': total_cancelled if total_cancelled is not None else 0.00,
            'total_transactions': total_transactions if total_transactions is not None else 0.00,
        }
        data['transaction_count'].append(transaction_count_data)

        # Process Notifications:
        for notification in notification_serializer.data:
            notification_data = {
                'message': notification['message'],
                'subject': notification['subject'],
                'update_at': notification['updated_at']
            }

            data['messages'].append(notification_data)

        # Process feedbacks
        for feedback in feedback_serializer.data:
            patient = Patient.objects.get(id=feedback['patient'])
            feedback['patient'] = {
                'id': patient.id,
                'full_name': patient.full_name,
                'profile_picture': specialist.profile_picture.url if specialist.profile_picture else None
            }
            data['feedbacks'].append(feedback)

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
                    'transaction_patient': {
                        'id': appointment.patient.id,
                        'full_name': appointment.patient.full_name,
                        'profile_picture': appointment.patient.profile_picture.url if appointment.patient.profile_picture else None
                    },

                }
            }
            data['transactions'].append(transaction_data)

        # Process appointments
        for appointment in appointment_serializer.data:
            appointment_id = uuid.UUID(appointment['id'])
            has_diagnosis = appointment_id in appointments_with_diagnoses_ids

            patient_id = appointment['patient']
            patient = Patient.objects.get(id=patient_id)
            appointment_data = {
                'id': appointment['id'],
                'patient': {
                    'patient_id': patient.id,
                    'full_name': patient.full_name,
                    'contact_phone': patient.contact_phone,
                    'profile_picture': patient.profile_picture.url if patient.profile_picture else None
                },
                'date_time': appointment['date_time'],
                'concern': appointment['concern'],
                'status': appointment['status'],
                'payment_status': appointment['payment_status'],
                'cancel_reason': appointment['cancel_reason'],
                'reject_reason': appointment['reject_reason'],
                'updated_at': appointment['updated_at'],
                'has_diagnosis': has_diagnosis
            }
            data['appointments'].append(appointment_data)

        return Response(data, status=status.HTTP_200_OK)

# update profile
#===========Update profile============
class SpecialistRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Specialist.objects.all()
    serializer_class = SpecialistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Specialist.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

#===Diagnosis
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_diagnosis(request, appointment_id):
    try:
        received_data = request.data
        diagnosis_text = received_data['diagnosis_text']
        prescription_text = received_data['prescription_text']
        appointment = get_object_or_404(Appointment, id=appointment_id)

        with transaction.atomic():
            diagnosis = Diagnosis(
                appointment=appointment,
                diagnosis_text=diagnosis_text,
                created_at=timezone.now()
            )
            diagnosis.save()

            prescription = Prescription(
                diagnosis=diagnosis,
                prescription_text=prescription_text,
                created_at=timezone.now()
            )
            prescription.save()

        prescription_serializer = PrescriptionSerializer(prescription)
        return Response(prescription_serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        print('Error:', str(e))
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#===/Diagnosis
# ======================SPECIALISTS END========================

# ======================SPECIALIST RATINGS START========================
@api_view(['GET'])
def specialist_feedback(request, specialist_id):
    try:
        specialist = get_object_or_404(Specialist, id=specialist_id)
        feedbacks = SpecialistFeedback.objects.filter(specialist=specialist)

        serializer = SpecialistFeedbackSerializer(feedbacks, many=True)
        data = []
        for feedback in serializer.data:
            patient = Patient.objects.get(id=feedback['patient'])
            feedback['patient'] = {
                'id': patient.id,
                'full_name': patient.full_name,
                'profile_picture': patient.profile_picture.url if patient.profile_picture else None
            }
            data.append(feedback)
        return JsonResponse(data, safe=False, status=status.HTTP_200_OK)

    except Exception as e:
        error_message = f"Error retrieving Item: {str(e)}"
        print(f"Error occurred: {error_message}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ======================SPECIALIST FEEDBACK POST========================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_specialist_feedback(request, id):
    received_data = request.data
    appointment = get_object_or_404(Appointment, id=id)
    specialist = appointment.specialist

    try:
        if not hasattr(request.user, 'patient'):
            return Response({'error': 'User is not a patient.'}, status=status.HTTP_403_FORBIDDEN)

        patient = request.user.patient

        specialist_feedback_data = {
            'specialist': specialist.id,
            'patient': patient.id,
            'rating': received_data.get('rating'),
            'concern': received_data.get('concern'),
            'feedback_text': received_data.get('feedback_text'),
            'timezone': timezone.now()
        }

        serializer = SpecialistFeedbackSerializer(data=specialist_feedback_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print('Validation Error:', serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print('Error:', str(e))
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ======================/SPECIALISTS========================
# ======================APPOINTMENT========================
#data
@api_view(['GET'])
def getSpecialistAppointments(request, specialist_id):
    try:
        specialist = get_object_or_404(Specialist, id=specialist_id)
        appointments = Appointment.objects.filter(specialist=specialist, status='accepted')
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        error_message = f"Error retrieving item: {str(e)}"
        return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#create
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createAppointment(request):
    try:
        received = request.data
        patient_user = request.user
        patient = get_object_or_404(Patient, user=patient_user.id)

        received['patient'] = patient.id
        received['updated_at'] = timezone.now()

        serializer = AppointmentSerializer(data=received)
        if serializer.is_valid():
            appointment = serializer.save()

            amount = received.get('amount')
            if amount is None:
                return Response({"error": "Amount is required for the transaction."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Create transaction
            transaction = Transaction(
                appointment=appointment,
                patient=patient,
                amount=amount,
                payment_method=received.get('payment_method', 'Unknown'),
                reference=received.get('reference', ''),
                phone_number=received.get('phone_number', ''),
                status=received.get('status', 'Due')
            )
            transaction.save()

            # Create notification for patient
            patient_notification = Notification(
                user=patient_user,
                subject='Appointment Created',
                message=f'Your appointment with {appointment.specialist} on {appointment.date_time} has been created.',
            )
            patient_notification.save()

            # Send the email to patient
            patient_email_subject = 'Appointment Confirmation'
            patient_email_message = f"""
            Dear {patient.full_name},

            We are pleased to inform you that your appointment with {appointment.specialist} has been successfully scheduled. Please find the details of your appointment below:

            Specialist: {appointment.specialist}
            Date and Time: {appointment.date_time}

            If you have any questions or need to reschedule, please contact us at {settings.CONTACT_EMAIL}.

            Thank you for choosing our services.

            Best regards,
            Health60
            """

            send_mail(
                patient_email_subject,
                patient_email_message,
                settings.DEFAULT_FROM_EMAIL,
                [patient.contact_email],
                fail_silently=False,
            )

            # Fetch the specialist user
            specialist_user = appointment.specialist.user

            # Create notification for specialist
            specialist_notification = Notification(
                user=specialist_user,
                subject='New Appointment',
                message=f'You have a new appointment with {patient_user.username} on {appointment.date_time}.',
            )
            specialist_notification.save()

            # Send the email to specialist
            specialist_email_subject = 'New Appointment Notification'
            specialist_email_message = f"""
            Dear Dr. {appointment.specialist.full_name},

            This is to inform you that you have a new appointment scheduled with {patient.full_name}. Please find the details below:

            Patient: {patient.full_name}
            Date and Time: {appointment.date_time}

            Please ensure to review the patient's details and prepare accordingly. If you need further information, please contact us at {settings.CONTACT_EMAIL}.

            Best regards,
            Health360
            """

            send_mail(
                specialist_email_subject,
                specialist_email_message,
                settings.DEFAULT_FROM_EMAIL,
                [appointment.specialist.contact_email],
                fail_silently=False,
            )

            response_data = {
                "appointment_id": appointment.id,
                "appointment_data": serializer.data
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            print('Validation Error:', serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        error_message = f"Error creating appointment: {str(e)}"
        print(error_message)
        return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class AppointmentListView(generics.ListCreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Appointment.objects.all()

    def perform_create(self, serializer):
        try:
            serializer.is_valid(raise_exception=True)
            appointment = serializer.save()
            appointment.clean()

            # Return success response with created appointment data
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            # Return error response with validation errors
            return Response({'errors': e.messages}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def updateAppointment(request, id):
    try:
        received_data = request.data
        appointment = get_object_or_404(Appointment, id=id)

        serializer = AppointmentSerializer(appointment, data=received_data, partial=True)
        if serializer.is_valid():
            appointment_status_before_update = appointment.status  # Save current status
            appointment = serializer.save()

            if appointment_status_before_update != 'rejected' and appointment.status == 'rejected':
                # Create a notification to the patient
                patient = appointment.patient  # Assuming appointment has a 'patient' field
                notification = Notification.objects.create(
                    user=patient.user,
                    subject='Appointment Rejected',
                    message=f'Your appointment on {appointment.date_time} has been rejected. Reason: {appointment.reject_reason}',
                    timestamp=timezone.now()
                )
                notification.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            print('Validation Error:', serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print('Error:', str(e))
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#======================/APPOINTMENTS========================


# ======================COMMON CONCERNS START========================

@api_view(['GET'])
def common_Concerns(request):
    try:
        consultations = CommonConsultation.objects.all()
        serializer = Common_ConsultationsSerializer(consultations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        error_message = f"Error retrieving Item: {str(e)}"
        print('Error', error_message)
        return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ======================COMMON CONCERNS END========================

#======================TRANSACTIONS========================
# get appointment
@api_view(['GET'])
def getAppointment(request, id):
    try:
        appointment = get_object_or_404(Appointment, id=id)
        response_data = {
            "id": appointment.id,
            "date_time": appointment.date_time,
            "specialist_full_name": appointment.specialist.full_name,
            'specialist_category': appointment.specialist.category.name,
            "specialist_pricing": appointment.specialist.pricing,
            "concern": appointment.concern
        }
        return JsonResponse(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        error_message = f"Error retrieving appointment: {str(e)}"
        return JsonResponse({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# create payment
def get_access_token():
    consumer_key = 'jJBJkM31XGcvBP6rbdjdq0swCSm9eJFS'
    consumer_secret = 'KJmmfii1sbHiduyh'
    api_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    credentials = f"{consumer_key}:{consumer_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode('utf-8')

    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'application/json',
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        access_token = response.json().get('access_token')
        logger.info(f"Access token retrieved: {access_token}")
        return access_token
    else:
        error_message = f"Failed to get access token: {response.status_code} - {response.text}"
        logger.error(error_message)
        raise Exception(error_message)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def iniate_stk_push(request):
    try:
        received_data = request.data
        total_amount = float(received_data['amount'])
        appointment_id = received_data['appointment']

        payload = {
            "BusinessShortCode": 174379,
            "Password": "MTc0Mzc5YmZiMjc5ZjlhYTliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMjMwODI5MTEzNTEy",
            "Timestamp": "20230829113512",
            "TransactionType": "CustomerPayBillOnline",
            "Amount": total_amount,
            "PartyA": received_data['phone_number'],
            "PartyB": 174379,
            "PhoneNumber": received_data['phone_number'],
            "CallBackURL": f"https://d069-105-29-165-229.ngrok-free.app/api/payment_webhook/?appointment_id={appointment_id}",
            "AccountReference": "Health 360",
            "TransactionDesc": "Payment for Booking Services",
            "appointment_id": appointment_id,
        }

        try:
            access_token = get_access_token()
        except Exception as e:
            logger.error(f"Error obtaining access token: {str(e)}")
            return JsonResponse({'success': False, 'error': 'Failed to get access token'}, status=500)

        stk_push_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        stk_push_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
        }
        stk_push_response = requests.post(stk_push_url, json=payload, headers=stk_push_headers)

        if stk_push_response.status_code == 200:
            return JsonResponse({'message': 'Payment processing...', 'appointment_id': appointment_id}, status=200)
        else:
            error_message = f'STK push request failed with status code {stk_push_response.status_code}: {stk_push_response.text}'
            logger.error(error_message)
            return JsonResponse({'success': False, 'error': 'STK push request failed. Please try again later.'},
                                status=400)
    except Exception as e:
        logger.error(f"Error initiating STK push: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
def payment_webhook(request, appointment_id):
    try:
        response_data = request.data
        logger.info(f"Webhook received data: {response_data}")

        # Retrieve the appointment from the database
        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Appointment not found'}, status=404)

        # Process the response data
        stk_callback = response_data.get('Body', {}).get('stkCallback', {})
        result_code = stk_callback.get('ResultCode')
        result_desc = stk_callback.get('ResultDesc', 'Unknown error')

        if result_code == 0:
            # Payment was successful
            callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
            amount = None
            receipt_number = None
            transaction_date = None
            phone_number = None

            for item in callback_metadata:
                if item['Name'] == 'Amount':
                    amount = item['Value']
                elif item['Name'] == 'MpesaReceiptNumber':
                    receipt_number = item['Value']
                elif item['Name'] == 'TransactionDate':
                    transaction_date = item['Value']
                    # Convert transaction_date to datetime object
                    transaction_date = datetime.strptime(str(transaction_date), '%Y%m%d%H%M%S')
                elif item['Name'] == 'PhoneNumber':
                    phone_number = item['Value']

            appointment.payment_status = True
            appointment.save()

            transaction = get_object_or_404(Transaction, appointment=appointment_id)
            transaction.status = 'Paid'
            transaction.payment_method = 'MPESA',
            transaction.amount = amount
            transaction.reference = receipt_number
            transaction.timestamp = transaction_date
            transaction.phone_number = phone_number
            transaction.save()

            logger.info(f"Payment for appointment {appointment_id} completed successfully.")
            return JsonResponse({'success': True, 'message': 'Payment completed successfully'}, status=200)
        else:
            # Payment failed or was cancelled
            appointment.payment_status = False
            appointment.save()

            transaction = get_object_or_404(Transaction, appointment=appointment_id)
            transaction.status = 'Canceled'
            transaction.save()

            logger.error(f"Payment for appointment {appointment_id} failed: {result_desc}")
            return JsonResponse({'success': False, 'error': f'Payment failed: {result_desc}'}, status=400)

    except Exception as e:
        logger.error(f"Error processing payment webhook: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@api_view(['GET'])
def payment_waiting(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    payment = get_object_or_404(Transaction, appointment=appointment_id)

    MAX_ATTEMPTS = 10
    attempts = 0

    while attempts < MAX_ATTEMPTS:
        appointment.refresh_from_db()
        if appointment.payment_status == True:
            # Payment completed, return success response
            data = {
                "message": "Payment successful",
                'reference': payment.reference

            }
            return Response(data, status=status.HTTP_200_OK)

        sleep(2)
        attempts += 1

    return Response({"message": "Payment timed out. Please try again later."}, status=status.HTTP_408_REQUEST_TIMEOUT)

#======================/TRANSACTIONS========================
