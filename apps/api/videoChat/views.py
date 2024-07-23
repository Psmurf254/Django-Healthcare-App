from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView
from apps.api.info.models import Notification
from apps.api.patients.models import Patient
from apps.api.specialists.models import Appointment, Consultation
from config import settings
from web_project import TemplateLayout
import random
import logging

logger = logging.getLogger(__name__)


def get_absolute_url(path):
    return settings.BASE_URL + path


class VideoChatView(TemplateView):
    template_name = 'video_conference.html'

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        appointment = get_object_or_404(Appointment, pk=self.kwargs['pk'])

        if appointment:
            appointment.status = 'In Progress'
            appointment.save()

        patient = appointment.patient
        room_id = str(random.randint(10000, 99999))
        link_url = get_absolute_url(reverse('app-api-video-chat', kwargs={'pk': patient.pk}) + f'?roomID={room_id}')

        if patient:
            # Create and save the notification
            notification = Notification(
                user=patient.user,
                subject='Meeting Invitation Request',
                message=f'You have a new meeting invitation. Follow the link to continue: {link_url}'
            )
            notification.save()

            # Send an email to the patient's contact email
            try:
                send_mail(
                    subject='Meeting Invitation Request',
                    message=f'You have a new meeting invitation. Follow the link to continue: {link_url}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[patient.contact_email],
                    fail_silently=False,
                )
            except Exception as e:
                logger.error(f"Failed to send email: {e}")

        context['room_id'] = room_id
        return context
