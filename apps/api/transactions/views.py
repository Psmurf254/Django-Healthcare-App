from datetime import date
from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic import TemplateView
from apps.api.patients.models import Patient
from web_project import TemplateLayout
from apps.api.specialists.models import Transaction, Appointment
from apps.transactions.forms import TransactionForm
from django.contrib.auth.mixins import PermissionRequiredMixin


class TransactionAddView(TemplateView):
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['current_date'] = date.today().strftime("%Y-%m-%d")

        context.update({
            'appointments': Appointment.objects.all(),
            'patients': Patient.objects.all(),
        })
        return context

    def post(self, request):
        form = TransactionForm(request.POST)
        if form.is_valid():
            if not self.transaction_exists(form.cleaned_data):
                form.save()
                messages.success(request, 'Transaction Added')
            else:
                messages.error(request, 'Transaction already exists')
        else:
            messages.error(request, 'Transaction Failed')
        return redirect('transactions')

    def transaction_exists(self, cleaned_data):
        if cleaned_data['reference'] is not None:
            return Transaction.objects.filter(reference=cleaned_data['reference']).exists()

        return Transaction.objects.filter(
            status__iexact=cleaned_data['status'],
            amount__iexact=cleaned_data['amount'],
        ).exists()
