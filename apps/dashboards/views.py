from django.shortcuts import redirect
from django.views.generic import TemplateView

from apps.api.patients.models import Patient
from apps.api.specialists.models import Transaction, Specialist, Appointment, Hospital
from web_project import TemplateLayout


"""
This file is a view controller for multiple pages as a module.
Here you can override the page view layout.
Refer to dashboards/urls.py file for more pages.
"""


class DashboardsView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        transactions = Transaction.objects.all(),
        patients = Patient.objects.all().count()
        specialists = Specialist.objects.all().count()
        appointments = Appointment.objects.all().count()
        hospitals = Hospital.objects.all().count()
        new_specialists = Specialist.objects.all()
        new_patients = Patient.objects.all()
        context.update({
            'transactions': transactions,
            'patients': patients,
            'specialists': specialists,
            'appointments': appointments,
            'hospitals': hospitals,
            'new_specialists': new_specialists,
            'new_patients': new_patients
        })

        return context
