from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.views.generic import TemplateView
from apps.api.patients.models import Patient
from web_project import TemplateLayout
from apps.transactions.forms import TransactionForm
from apps.api.specialists.models import Transaction, Appointment
from django.contrib.auth.mixins import PermissionRequiredMixin

class TransactionUpdateView(PermissionRequiredMixin, TemplateView):
    permission_required = ("transactions.update_transaction")

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['transaction_id'] = self.get_transaction(self.kwargs['pk'])
        context.update({
            'patients': Patient.objects.all(),
            'appointments': Appointment.objects.all()
        })
        return context

    def post(self, request, pk):
        transaction = self.get_transaction(pk)
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            status = form.cleaned_data['status']
            appointment_id = form.cleaned_data['appointment'].id
            appointment = get_object_or_404(Appointment, id=appointment_id)
            if not self.transaction_exists(form.cleaned_data, transaction):
                form.save()
                if status == 'Paid':
                    appointment.payment_status = True
                    appointment.save()
                else:
                    appointment.payment_status = False
                    appointment.save()


                messages.success(request, 'Transaction Updated')
            else:
                messages.error(request, 'Transaction Already Exists')

        else:
            print(form.errors)
            messages.error(request, 'Transaction Failed'.join(form.errors))
        return redirect('transactions')

    def get_transaction(self, pk):
        return Transaction.objects.get(pk=pk)

    def transaction_exists(self, cleaned_data, current_transaction):
        matching_transactions = Transaction.objects.filter(
            Q(reference=cleaned_data['reference']) &
            Q(status=cleaned_data['status'])
        ).exclude(pk=current_transaction.pk)
        return matching_transactions.exists()

