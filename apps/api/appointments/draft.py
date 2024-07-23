import datetime

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.timezone import make_aware
from django.views.generic import TemplateView

from apps.api.patients.models import Patient
from apps.api.specialists.models import Specialist, Transaction, Appointment
from apps.asset_manager.forms import AppointmentForm


class AppointmentAddView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        specialist = get_object_or_404(Specialist, pk=self.kwargs['pk'])
        context.update({
            'specialist': specialist,
        })
        return context

    def post(self, request, pk):
        specialist = get_object_or_404(Specialist, pk=pk)
        patient = get_object_or_404(Patient, user=request.user)
        concern = request.POST.get('concern')
        date_time = request.POST.get('date_time')

        print('date time', date_time)

        appointment = Appointment(
            specialist=specialist,
            patient=patient,
            concern=concern,
            date_time=date_time
        )
        appointment.save()

        if appointment:
            transaction = Transaction(
                appointment=appointment,
                patient=patient,
                reference=None,
                timestamp=timezone.now(),
                amount=specialist.pricing,
                status='Due'
            )
            transaction.save()
            messages.success(request, 'Appointment successfully created. Complete Payment Process.')
            return redirect(reverse_lazy('app-api-transactions-pay', kwargs={'pk': transaction.pk}))
        else:
            messages.error(request, 'Failed to create appointment.')

        return redirect(reverse_lazy('app-api-appointment-add', kwargs={'pk': specialist.id}))
