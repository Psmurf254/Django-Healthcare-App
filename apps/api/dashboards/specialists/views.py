from django.contrib import messages
from django.db.models import Sum
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView
from django.utils import timezone
from datetime import timedelta, date, datetime
from apps.api.info.models import Notification
from apps.api.patients.models import Patient
from apps.api.specialists.models import Appointment, Specialist, Prescription, Transaction, \
    SpecialistCategory, Test, Consultation, Hospital
from apps.asset_manager.forms import SpecialistUpdateForm, APISpecialistUpdateForm
from web_project import TemplateLayout


class DoctorDashboardView(TemplateView):
    template_name = 'doctor_dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        current_user = request.user

        if Patient.objects.filter(user=current_user).exists():
            return redirect('app-api-patient-dashboard')

        if not Specialist.objects.filter(user=current_user).exists():
            messages.error(request, 'You are not authorized to access this page.')
            return redirect('pages-misc-not-authorized')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        specialist = get_object_or_404(Specialist, user=current_user)
        hospital = specialist.hospital.first()
        test_reports = Test.objects.filter(consultation__appointment__specialist=specialist)

        # Get today's date and next day's date
        today_date = timezone.now().date()
        next_day_date = today_date + timedelta(days=1)

        today_appointments = Appointment.objects.filter(specialist=specialist, date_time__date=today_date).order_by(
            'date_time')
        next_day_appointments = Appointment.objects.filter(specialist=specialist,
                                                           date_time__date=next_day_date).order_by('date_time')
        total_appointments_count = Appointment.objects.filter(specialist=specialist)
        accepted_appointments = total_appointments_count.filter(status='Accepted')
        for appt in accepted_appointments:
            if appt.date_time < timezone.now():
                appt.status = 'InProgress'
                appt.save()
        context.update({
            'specialist': specialist,
            'all_appointments': total_appointments_count,
            'today_appointments': today_appointments,
            'next_day_appointments': next_day_appointments,
            'total_appointments_count': total_appointments_count.count(),
            'current_date': today_date,
            'next_day_date': next_day_date,
            'test_reports': test_reports,
            'hospital': hospital
        })
        return context

    def post(self, request):
        current_user = self.request.user
        notifications = Notification.objects.filter(user=current_user)
        for notification in notifications:
            notification.is_read = True
            notification.save()
        return redirect('app-api-patient-dashboard')


class DocProfileView(TemplateView):
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        specialist = get_object_or_404(Specialist, pk=self.kwargs['pk'])
        hospital = specialist.hospital.first()
        context.update({
            'specialist': specialist,
            'hospital': hospital
        })
        return context


class DocProfileUpdateView(TemplateView):
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        specialist = get_object_or_404(Specialist, pk=self.kwargs['pk'])
        context.update({
            'specialist': specialist,
            'categories': SpecialistCategory.objects.all(),
            'hospitals': Hospital.objects.all()
        })
        return context

    def post(self, request, pk):
        specialist = get_object_or_404(Specialist, pk=self.kwargs['pk'])
        form = APISpecialistUpdateForm(request.POST, request.FILES, instance=specialist)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, f'Failed to update profile'.join(form.errors))
        return redirect('app-api-doc-dashboard')


class DocTransactionsView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        specialist = get_object_or_404(Specialist, pk=self.kwargs['pk'])
        hospital = specialist.hospital.first()
        transactions = Transaction.objects.filter(appointment__specialist=specialist)
        total_paid = transactions.filter(status='Paid').aggregate(total_paid=Sum('amount'))['total_paid']
        total_paid = total_paid if total_paid else 0
        total_due = transactions.filter(status='Due').aggregate(total_due=Sum('amount'))['total_due']
        total_due = total_due if total_due else 0

        context.update({
            'specialist': specialist,
            'transactions': transactions,
            'total_transactions_count': transactions.count(),
            'total_due': total_due,
            'total_paid': total_paid,
            'hospital': hospital,
        })
        return context


class AppointmentStatusUpdateView(TemplateView):
    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=self.kwargs['pk'])
        # Retrieve status from POST data
        status = request.POST.get('status')
        reject_reason = request.POST.get('reject_reason')
        if reject_reason:
            appointment.reject_reason = reject_reason
            appointment.status = status
            appointment.save()
        else:
            appointment.status = status
            appointment.save()
        messages.success(request, 'Appointment updated successfully')
        return redirect('app-api-doc-dashboard')


class OrderTestView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appointment = get_object_or_404(Appointment, pk=self.kwargs['pk'])
        appointment.status = 'InProgress'
        appointment.save()
        consultation = appointment.consultation
        context.update({
            'specialist': appointment.specialist,
            'hospital': appointment.specialist.hospital.first(),
            'appointment': appointment,
            'consultation': consultation,

        })
        return context

    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        test_name = request.POST.get('test_name')
        consultation_symptoms = request.POST.get('symptoms')
        consultation_diagnosis = request.POST.get('diagnosis')
        consultation_notes = request.POST.get('notes')

        consultation = appointment.consultation

        consultation.symptoms = consultation_symptoms
        consultation.diagnosis = consultation_diagnosis
        consultation.notes = consultation_notes
        consultation.status = 'Test Ordered'
        consultation.save()

        test, created = Test.objects.get_or_create(
            consultation=consultation,
            test_name=test_name,
            status='Ordered'
        )
        test.save()
        if test:
            messages.success(request, 'Test Ordered successfully')
        else:
            messages.error(request, 'Failed to order the Test Results')
        return redirect('app-api-doc-dashboard')


class UpdateTestResultView(TemplateView):
    template_name = "app-api-test-update.html"

    def dispatch(self, request, *args, **kwargs):
        appointment = get_object_or_404(Appointment, pk=kwargs['pk'])
        consultation = get_object_or_404(Consultation, appointment=appointment)
        try:
            test = Test.objects.get(consultation=consultation)
        except Test.DoesNotExist:
            messages.error(request, 'No test found for this appointment. Kindly Add Test first')
            return redirect('app-api-doc-dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appointment = get_object_or_404(Appointment, pk=self.kwargs['pk'])
        consultation = get_object_or_404(Consultation, appointment=appointment)
        test = Test.objects.get(consultation=consultation)
        context.update({
            'test': test,
            'specialist': consultation.appointment.specialist,
            'appointment': appointment,
            'hospital': appointment.specialist.hospital.first(),
        })
        return context

    def post(self, request, *args, **kwargs):
        appointment = get_object_or_404(Appointment, pk=self.kwargs['pk'])
        appointment.status = 'InProgress'
        appointment.save()
        consultation = get_object_or_404(Consultation, appointment=appointment)
        consultation.status = 'Prescription'
        consultation.save()
        test = get_object_or_404(Test, consultation=consultation)
        results = request.POST.get('results')
        # Update the test instance
        test.results = results
        test.status = 'Completed'
        test.completed_date = date.today()
        test.save()
        if test:
            messages.success(request, 'Test Updated successfully')
        else:
            messages.error(request, 'Failed To Update The Results')
        return redirect('app-api-doc-dashboard')


class PrescriptionAddView(TemplateView):
    template_name = "app-api-prescription-add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appointment = get_object_or_404(Appointment, pk=self.kwargs['pk'])
        patient = appointment.patient
        date_of_birth = patient.date_of_birth
        today = datetime.today().date()
        age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        context.update({
            'specialist': appointment.specialist,
            'appointment': appointment,
            'age': age,
            'hospital': appointment.specialist.hospital.first(),
        })
        try:
            prescription = Prescription.objects.get(consultation__appointment=appointment)
            context.update({'prescription': prescription})
        except Prescription.DoesNotExist:
            context.update({'prescription': None})
        return context

    def post(self, request, *args, **kwargs):
        appointment = get_object_or_404(Appointment, pk=kwargs['pk'])
        appointment.status = 'Completed'
        appointment.save()
        consultation = appointment.consultation
        consultation.status = 'Completed'
        consultation.save()

        medication = request.POST.get('medication')
        dosage = request.POST.get('dosage')
        duration = request.POST.get('duration')
        instructions = request.POST.get('instructions')

        prescription, created = Prescription.objects.get_or_create(
            consultation=consultation,
            defaults={
                'medication': medication,
                'dosage': dosage,
                'duration': duration,
                'instructions': instructions
            }
        )
        if not created:
            # Update existing prescription if it was not created
            prescription.medication = medication
            prescription.dosage = dosage
            prescription.duration = duration
            prescription.instructions = instructions
            prescription.save()

        if prescription:
            messages.success(request, 'Prescription added successfully')
        else:
            messages.error(request, 'Failed to add the Prescription')
        return redirect('app-api-doc-dashboard')


class TestReportAndPrescriptionView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        specialist = get_object_or_404(Specialist, user=current_user)
        test_reports = Test.objects.filter(consultation__appointment__specialist=specialist)
        prescriptions = Prescription.objects.filter(consultation__appointment__specialist=specialist)

        context.update({
            'specialist': specialist,
            'test_reports': test_reports,
            'prescriptions': prescriptions,
            'hospital': specialist.hospital.first(),
        })
        return context
