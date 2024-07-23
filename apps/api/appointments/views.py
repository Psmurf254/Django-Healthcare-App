import datetime
from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView
from apps.api.patients.models import Patient
from apps.api.specialists.models import Specialist, Transaction, Appointment, Consultation


class AppointmentAddView(TemplateView):
    template_name = 'app-api-appointment-add'

    def dispatch(self, request, *args, **kwargs):
        current_user = request.user
        if not Patient.objects.filter(user=current_user).exists():
            messages.error(request, 'You are not authorized to access this page.')
            return redirect('pages-misc-not-authorized')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        specialist = get_object_or_404(Specialist, pk=self.kwargs['pk'])
        today = timezone.now().date()

        availability = {
            'sunday': (specialist.sunday_availability, specialist.sunday_start_time, specialist.sunday_end_time),
            'monday': (specialist.monday_availability, specialist.monday_start_time, specialist.monday_end_time),
            'tuesday': (specialist.tuesday_availability, specialist.tuesday_start_time, specialist.tuesday_end_time),
            'wednesday': (
                specialist.wednesday_availability, specialist.wednesday_start_time, specialist.wednesday_end_time),
            'thursday': (
                specialist.thursday_availability, specialist.thursday_start_time, specialist.thursday_end_time),
            'friday': (specialist.friday_availability, specialist.friday_start_time, specialist.friday_end_time),
            'saturday': (
                specialist.saturday_availability, specialist.saturday_start_time, specialist.saturday_end_time),
        }

        slots = self.get_available_slots(today, availability, specialist)
        context.update({
            'specialist': specialist,
            'slots': slots,
        })
        return context

    def get_available_slots(self, start_date, availability, specialist):
        slots = {}
        current_date = start_date
        for i in range(7):  # Show slots for the next 7 days
            day_name = current_date.strftime('%A').lower()
            available, start_time, end_time = availability[day_name]
            if available:
                day_slots = self.generate_time_slots(start_time, end_time, current_date, specialist)
                slots[current_date] = day_slots
            current_date += datetime.timedelta(days=1)
        return slots

    def generate_time_slots(self, start_time, end_time, date, specialist):
        slots = []
        current_time = datetime.datetime.combine(date, start_time)
        end_time = datetime.datetime.combine(date, end_time)

        accepted_appointments = Appointment.objects.filter(
            specialist=specialist,
            status='accepted',
            date_time__date=date
        ).values_list('date_time', flat=True)

        now = timezone.now()

        while current_time + datetime.timedelta(hours=1) <= end_time:
            slot_start = timezone.make_aware(current_time, timezone.get_current_timezone())
            slot_end = timezone.make_aware(current_time + datetime.timedelta(hours=1), timezone.get_current_timezone())

            if slot_start <= now:  # Exclude past slots
                current_time += datetime.timedelta(hours=1)
                continue

            conflict = False
            for appointment_time in accepted_appointments:
                appointment_start = appointment_time
                appointment_end = appointment_time + datetime.timedelta(hours=1)
                if slot_start < appointment_end and slot_end > appointment_start:
                    conflict = True
                    break

            if not conflict:
                slots.append(current_time.time())

            current_time += datetime.timedelta(hours=1)
        return slots

    def post(self, request, pk):
        specialist = get_object_or_404(Specialist, pk=pk)
        patient = get_object_or_404(Patient, user=request.user)
        concern = request.POST.get('concern')
        date_time = request.POST.get('date_time')
        print('Concern', concern)

        appointment = Appointment(
            specialist=specialist,
            patient=patient,
            concern=concern,
            date_time=date_time,
            status='Accepted',
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
            consultation, created = Consultation.objects.get_or_create(
                appointment=appointment,
                defaults={
                    'symptoms': 'None',
                    'diagnosis': 'None',
                    'status': 'Consultation'
                }
            )
            messages.success(request, 'Appointment successfully created. Complete Payment Process.')
            return redirect(reverse_lazy('app-api-transactions-pay', kwargs={'pk': transaction.pk}))
        else:
            messages.error(request, 'Failed to create appointment.')

        return redirect(reverse_lazy('app-api-appointment-add', kwargs={'pk': specialist.id}))
