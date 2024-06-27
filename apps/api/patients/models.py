import uuid

from django.db import models
from django.contrib.auth.models import User


class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10)
    date_of_birth = models.DateField()
    contact_phone = models.CharField(max_length=15)
    contact_email = models.EmailField()
    profile_picture = models.ImageField(upload_to='patient_profile_pics/', null=True, blank=True)
    total_consultations = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return self.full_name
