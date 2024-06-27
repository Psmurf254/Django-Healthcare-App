from django import forms
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.api.patients.models import Patient
from apps.api.info.models import Notification, About, Contact, FAQ
from apps.api.specialists.models import SpecialistCategory, Specialist, SpecialistFeedback, Appointment, \
    CommonConsultation


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = '__all__'


class CategoryForm(forms.ModelForm):
    class Meta:
        model = SpecialistCategory
        exclude = ['total_specialists']


class SpecialistForm(forms.ModelForm):
    class Meta:
        model = Specialist
        exclude = [
            'sunday_start_time', 'sunday_end_time',
            'monday_start_time', 'monday_end_time',
            'tuesday_start_time', 'tuesday_end_time',
            'wednesday_start_time', 'wednesday_end_time',
            'thursday_start_time', 'thursday_end_time',
            'friday_start_time', 'friday_end_time',
            'saturday_start_time', 'saturday_end_time',
            'status',
            'user',

        ]


class SpecialistUpdateForm(forms.ModelForm):
    class Meta:
        model = Specialist
        exclude = [
            'sunday_start_time', 'sunday_end_time',
            'monday_start_time', 'monday_end_time',
            'tuesday_start_time', 'tuesday_end_time',
            'wednesday_start_time', 'wednesday_end_time',
            'thursday_start_time', 'thursday_end_time',
            'friday_start_time', 'friday_end_time',
            'saturday_start_time', 'saturday_end_time',
            'sunday_availability', 'monday_availability',
            'tuesday_availability', 'wednesday_availability',
            'thursday_availability', 'friday_availability',
            'saturday_availability', 'user'
        ]



class FeedbackForm(forms.ModelForm):
    class Meta:
        model = SpecialistFeedback
        exclude = '__all__'


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        exclude = ['created_at']

    def clean_date_time(self):
        date_time = self.cleaned_data.get('date_time')
        if date_time and date_time < timezone.now():
            raise ValidationError("You cannot book an appointment for a past time.")
        return date_time


class CommonConcernForm(forms.ModelForm):
    class Meta:
        model = CommonConsultation
        fields = '__all__'


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        exclude = '__all__'


class AboutForm(forms.ModelForm):
    class Meta:
        model = About
        exclude = '__all__'


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        exclude = '__all__'


class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        exclude = '__all__'


class RoleForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']


class AssignPermissionsForm(forms.Form):
    role = forms.ModelChoiceField(queryset=Group.objects.all())
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
