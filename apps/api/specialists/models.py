import uuid

from django.db import models
from django.contrib.auth.models import User
from datetime import time, datetime, timedelta
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.validators import FileExtensionValidator
from ..patients.models import Patient
from django.db.models import Avg


class SpecialistCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    total_specialists = models.PositiveIntegerField(default=0)
    icon = models.FileField(upload_to="specialistCategory_images", blank=True, null=True,
                            validators=[FileExtensionValidator(['pdf', 'doc', 'svg'])])

    def __str__(self):
        return self.name


class Specialist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    verified = models.BooleanField(default=False)
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('in_active', 'In_Active'),
    ]

    status = models.BooleanField(default=True)
    category = models.ForeignKey(SpecialistCategory, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10)
    contact_phone = models.CharField(max_length=15)
    contact_email = models.EmailField()
    date_of_birth = models.DateField(blank=True, null=True)
    national_id = models.CharField(max_length=20, null=True, blank=True)
    medical_license_number = models.CharField(max_length=50, null=True, blank=True)
    pricing = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    years_of_experience = models.PositiveIntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    biography = models.TextField(blank=True, null='True')
    profile_picture = models.ImageField(upload_to='doctor_profile_pics/', null=True, blank=True)
    languages_spoken = models.CharField(max_length=255)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    total_consultations = models.PositiveIntegerField(blank=True, null=True)

    # Availability for Appointments
    sunday_availability = models.BooleanField(default=False)
    monday_availability = models.BooleanField(default=True)
    tuesday_availability = models.BooleanField(default=True)
    wednesday_availability = models.BooleanField(default=True)
    thursday_availability = models.BooleanField(default=True)
    friday_availability = models.BooleanField(default=True)
    saturday_availability = models.BooleanField(default=True)

    # Time ranges for appointments
    sunday_start_time = models.TimeField(default=time(9, 0))
    sunday_end_time = models.TimeField(default=time(13, 0))
    monday_start_time = models.TimeField(default=time(9, 0))
    monday_end_time = models.TimeField(default=time(17, 0))
    tuesday_start_time = models.TimeField(default=time(9, 0))
    tuesday_end_time = models.TimeField(default=time(17, 0))
    wednesday_start_time = models.TimeField(default=time(9, 0))
    wednesday_end_time = models.TimeField(default=time(17, 0))
    thursday_start_time = models.TimeField(default=time(9, 0))
    thursday_end_time = models.TimeField(default=time(17, 0))
    friday_start_time = models.TimeField(default=time(9, 0))
    friday_end_time = models.TimeField(default=time(17, 0))
    saturday_start_time = models.TimeField(default=time(9, 0))
    saturday_end_time = models.TimeField(default=time(13, 0))

    x = models.TextField(blank=True, null='True')
    whatsApp = models.TextField(blank=True, null='True')
    facebook = models.TextField(blank=True, null='True')
    instagram = models.TextField(blank=True, null='True')

    physical_clinic = models.BooleanField(default=False)
    address = models.CharField(max_length=255, blank=True, null='True')
    city = models.CharField(max_length=100, blank=True, null='True')
    state = models.CharField(max_length=100, blank=True, null='True')
    country = models.CharField(max_length=100, blank=True, null='True')
    zipcode = models.CharField(max_length=20, blank=True, null='True')

    def __str__(self):
        return self.full_name


class CommonConsultation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(SpecialistCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='Common_Consultations_images', null=True, blank=True)

    def __str__(self):
        return self.name


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    concern = models.TextField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    payment_status = models.BooleanField(default=False)
    cancel_reason = models.CharField(max_length=250, null=True, blank=True)
    reject_reason = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Appointment for {self.patient.full_name} with {self.specialist.full_name} at {self.date_time}"


class Diagnosis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment = models.ForeignKey(Appointment, null=True, blank=True, on_delete=models.CASCADE)
    diagnosis_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.diagnosis_text


class Prescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    diagnosis = models.ForeignKey(Diagnosis, on_delete=models.CASCADE)
    prescription_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.prescription_text




class SpecialistFeedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    rating = models.FloatField()
    concern = models.CharField(max_length=250, blank=True, null=True)
    feedback_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.patient} for {self.specialist}"


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    reference = models.CharField(max_length=150, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True
                                    )
    status = models.CharField(max_length=20, choices=[("Paid", "Paid"), ("Due", "Due"), ("Canceled", "Canceled")])

    def __str__(self):
        return self.reference


@receiver([post_save, post_delete], sender=Specialist)
def update_specialist_count(sender, instance, **kwargs):
    category = instance.category
    category.total_specialists = Specialist.objects.filter(category=category, verified=True).count()
    category.save()


@receiver([post_save, post_delete], sender=Appointment)
def update_specialist_total_consultations(sender, instance, **kwargs):
    specialist = instance.specialist
    total_consultations = Appointment.objects.filter(specialist=specialist).count()
    specialist.total_consultations = total_consultations
    specialist.save(update_fields=['total_consultations'])


@receiver([post_save, post_delete], sender=Appointment)
def update_patient_total_consultations(sender, instance, **kwargs):
    patient = instance.patient
    total_consultations = Appointment.objects.filter(patient=patient).count()
    patient.total_consultations = total_consultations
    patient.save(update_fields=['total_consultations'])


@receiver([post_save, post_delete], sender=SpecialistFeedback)
def update_specialist_average_rating(sender, instance, **kwargs):
    specialist = instance.specialist
    feedbacks = SpecialistFeedback.objects.filter(specialist=specialist)
    average_rating = feedbacks.aggregate(Avg('rating'))['rating__avg']
    specialist.average_rating = average_rating
    specialist.save(update_fields=['average_rating'])
