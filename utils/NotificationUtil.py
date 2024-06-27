from django.contrib.auth.models import User

from apps.asset_manager.models import Notification

def notify(recipient,subject, message):
    user = recipient
    if user is None:
        user = User.objects.filter(is_superuser=True).first()
    notification = Notification.objects.create(
        user=user,
        subject=subject,
        message=message,
        is_read=False
    )
    notification.save()

