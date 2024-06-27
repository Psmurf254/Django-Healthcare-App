from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView, DeleteView

from apps.api.patients.models import Patient
from apps.api.specialists.models import Appointment, Specialist, Transaction
from apps.asset_manager.forms import AppointmentForm
from web_project import TemplateLayout



class AppointmentView(PermissionRequiredMixin, TemplateView):
    permission_required = ['specialists.view_appointment']

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        pending = Appointment.objects.filter(status='Pending').count()
        cancelled = Appointment.objects.filter(status='Cancelled').count()
        rejected = Appointment.objects.filter(status='Rejected').count()
        completed = Appointment.objects.filter(status='Completed').count()

        print(pending)
        # Get the current datetime
        current_datetime = timezone.now()

        # Filter active bookings
        active_bookings = Appointment.objects.filter(
            status='accepted',
            date_time__gte=current_datetime
        ).count()

        # Filter past bookings and update their status to 'completed'
        past_bookings = Appointment.objects.filter(
            status='accepted',
            date_time__lt=current_datetime
        )
        past_bookings.update(status='completed')
        for appointment in past_bookings:
            appointment.status = 'completed'
            appointment.save()

        context.update({'appointments': Appointment.objects.all(),
                        'specialists': Specialist.objects.all(),
                        'patients': Patient.objects.all(),
                        'pending': pending,
                        'cancelled': cancelled,
                        'rejected': rejected,
                        'completed': completed,
                        'active': active_bookings,
                        })
        return context

    def post(self, request):
        form = AppointmentForm(request.POST, request.FILES)
        if form.is_valid():
            appointment = form.save(commit=False)
            specialist_id = form.cleaned_data['specialist']
            specialist = get_object_or_404(Specialist, full_name=specialist_id)

            appointment.specialist = specialist
            appointment.save()

            # Create a transaction
            transaction = Transaction(
                appointment=appointment,
                patient=form.cleaned_data['patient'],
                reference=None,
                timestamp=timezone.now(),
                amount=specialist.pricing,
                status='Due'
            )
            transaction.save()

            if transaction:
                messages.success(request, 'Appointment Added')
                return redirect(reverse_lazy('transactions-pay', kwargs={'pk': transaction.pk}))
            else:
                appointment.delete()
                messages.error(request, 'Failed to create transaction')
        else:
            print(form.errors)
            error_message = ' '.join([f'{key}: {value}' for key, value in form.errors.items()])
            messages.error(request, f'Appointment Failed: {error_message}')
        return redirect('app-asset-manager-appointments-list')


class AppointmentUpdateView(PermissionRequiredMixin, TemplateView):
    permission_required = ['specialist.change_appointment']

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        appointment = get_object_or_404(Appointment, pk=self.kwargs['pk'])
        context.update({
            'appointment': appointment,
            'specialists': Specialist.objects.all(),
            'patients': Patient.objects.all()
        })
        return context

    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=self.kwargs['pk'])
        form = AppointmentForm(request.POST, request.FILES, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Appointment updated successfully')
        else:
            messages.error(request, f'Appointment failed to updated'.join(form.errors))
        return redirect('app-asset-manager-appointments-list')


class AppointmentsDeleteView(PermissionRequiredMixin, TemplateView):
    permission_required = ['specialist.delete_appointment']

    def get(self, request, pk):
        appointment = get_object_or_404(Appointment, id=pk)
        appointment.delete()
        messages.success(request, f'Appointment Deleted')
        return redirect('app-asset-manager-appointments-list')
