import uuid

from django.db import models
from django.contrib.auth.models import User


class About(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    impact = models.TextField()
    commitment = models.TextField()
    vision = models.TextField()
    philosophy = models.TextField()


class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.TextField()
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contact {self.pk}"


class FAQ(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=255)
    answer = models.TextField()

    def __str__(self):
        return self.question


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='info_notifications')
    subject = models.CharField(max_length=250, blank=True, null=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message
