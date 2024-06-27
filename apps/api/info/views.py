from .models import  About, Contact, FAQ, Notification
from .serializers import AboutSerializer, ContactSerializer, FAQSerializer, NotificationSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.utils import timezone
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..specialists.models import Appointment
from django.core.mail import send_mail
from django.conf import settings


@api_view(['GET'])
def getAbout(request):
    try:
        about = About.objects.all()
        serializer = AboutSerializer(about, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        error_message = f"Error retrieving about: {str(e)}"

        return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def create_contact(request):
    try:
        recieved_data = request.data
        recieved_data['created_at'] = timezone.now()
        recieved_data['created_at'] = timezone.now()

        serializer = ContactSerializer(data=recieved_data)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print('Validation Error:', serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print('Error:', str(e))
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def getFAQ(request):
    try:
        about = FAQ.objects.all()
        serializer = FAQSerializer(about, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        error_message = f"Error retrieving FAQ: {str(e)}"

        return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def createPatientNotification(request, appointment_id):
    received_data = request.data
    appointment = get_object_or_404(Appointment, id=appointment_id)
    patient = appointment.patient.user.id
    message = request.data['message']
    received_data['user'] = patient
    received_data['updated_at'] = timezone.now()
    serializer = NotificationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        # Send the email to specialist
        specialist_email_subject = 'Appointment Invitation'
        specialist_email_message = f"""
                                    Dear Dr. {appointment.patient.full_name},
                                    {message}
                                    If you need further information, please contact us at {settings.CONTACT_EMAIL}.

                                    Best regards,
                                    Health360
                                    """

        send_mail(
            specialist_email_subject,
            specialist_email_message,
            settings.DEFAULT_FROM_EMAIL,
            [appointment.patient.contact_email],
            fail_silently=False,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        print('Validation Error:', serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clearNotifications(request):
    current_user = request.user
    notification = Notification.objects.filter(user=current_user)
    notification.delete()
    return Response('Items deleted', status=status.HTTP_200_OK)
