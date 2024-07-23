from django.shortcuts import get_object_or_404

from apps.api.info.models import Notification
from apps.api.patients.models import Patient
from apps.api.specialists.models import Specialist

def navbar(request):
    current_user = request.user
    user_type = None
    specialist = None
    patient = None
    profile = None
    notifications = None
    not_count = 0

    if current_user.is_authenticated:
        try:
            # Attempt to fetch as Patient
            profile = Patient.objects.get(user=current_user)
            user_type = 'patient'
        except Patient.DoesNotExist:
            try:
                profile = Specialist.objects.get(user=current_user)
                user_type = 'specialist'
            except Specialist.DoesNotExist:
                pass

        if user_type == 'patient':
            patient = get_object_or_404(Patient, user=current_user)
            notifications = Notification.objects.filter(user=current_user).order_by('-timestamp')
            not_count = notifications.filter(is_read=False).count()
        elif user_type == 'specialist':
            specialist = get_object_or_404(Specialist, user=current_user)
            notifications = Notification.objects.filter(user=current_user).order_by('-timestamp')
            not_count = notifications.filter(is_read=False).count()

    return {
        'profile': profile,
        'user_type': user_type,
        'doctor': specialist,
        'patient': patient,
        'notifications': notifications,
        'not_count': not_count,
    }


