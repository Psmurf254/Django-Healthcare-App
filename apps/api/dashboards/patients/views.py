import logging
from datetime import datetime
from django.template.loader import render_to_string
from xhtml2pdf import pisa

from django.contrib import messages
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView
from io import BytesIO

from apps.api.info.models import Notification
from apps.api.patients.models import Patient
from apps.api.specialists.models import Appointment, Prescription, Transaction, Specialist, Test
from apps.asset_manager.forms import PatientForm, FeedbackForm
from web_project import TemplateLayout

logger = logging.getLogger(__name__)


#Register


# main Content
class PatientDashboardView(TemplateView):
    template_name = 'patient_dashboard.html'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        current_user = request.user

        if Specialist.objects.filter(user=current_user).exists():
            return redirect('app-api-doc-dashboard')

        if not Patient.objects.filter(user=current_user).exists():
            messages.error(request, 'You are not authorized to access this page.')
            return redirect('pages-misc-not-authorized')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        patient = get_object_or_404(Patient, user=current_user)
        appointments = Appointment.objects.filter(patient=patient)
        appointment_page = self.request.GET.get('appointment_page', 1)
        appointments_paginator = Paginator(appointments, self.paginate_by)
        test_reports = Test.objects.filter(consultation__appointment__patient=patient)
        try:
            appointments = appointments_paginator.page(appointment_page)
        except PageNotAnInteger:
            appointments = appointments_paginator.page(1)
        except EmptyPage:
            appointments = appointments_paginator.page(appointments_paginator.num_pages)

        # Fetching prescriptions and applying pagination
        prescriptions = Prescription.objects.filter(consultation__appointment__in=appointments)

        prescription_page = self.request.GET.get('prescription_page', 1)
        prescriptions_paginator = Paginator(prescriptions, self.paginate_by)
        try:
            prescriptions = prescriptions_paginator.page(prescription_page)
        except PageNotAnInteger:
            prescriptions = prescriptions_paginator.page(1)
        except EmptyPage:
            prescriptions = prescriptions_paginator.page(prescriptions_paginator.num_pages)

        transactions = Transaction.objects.filter(patient=patient)
        transaction_page = self.request.GET.get('transaction_page', 1)
        transactions_paginator = Paginator(transactions, self.paginate_by)
        try:
            transactions = transactions_paginator.page(transaction_page)
        except PageNotAnInteger:
            transactions = transactions_paginator.page(1)
        except EmptyPage:
            transactions = transactions_paginator.page(transactions_paginator.num_pages)

        context.update({
            'patient': patient,
            'appointments': appointments,
            'prescriptions': prescriptions,
            'test_reports': test_reports,
            'transactions': transactions,
        })
        return context

    def post(self, request):
        current_user = self.request.user
        notifications = Notification.objects.filter(user=current_user)
        for notification in notifications:
            notification.is_read = True
            notification.save()
        return redirect('app-api-patient-dashboard')


# Profile Settings
class PatientProfileUpdateView(TemplateView):
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        patient = get_object_or_404(Patient, pk=self.kwargs['pk'])
        context.update({
            'patient': patient,
        })
        return context

    def post(self, request, pk):
        patient = get_object_or_404(Patient, pk=self.kwargs['pk'])
        form = PatientForm(request.POST, request.FILES, instance=patient)
        if form.is_valid():
            patient.user = request.user
            form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, f'Failed to updated'.join(form.errors))
        return redirect('app-api-patient-dashboard')


# Prescription
class PrescriptionView(TemplateView):
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        prescription = get_object_or_404(Prescription, pk=self.kwargs['pk'])
        patient = prescription.consultation.appointment.patient
        hospital = prescription.consultation.appointment.specialist.hospital.first()
        date_of_birth = patient.date_of_birth
        today = datetime.today().date()
        age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        context.update({
            'prescription': prescription,
            'age': age,
            'hospital': hospital,
            'patient': patient,
        })
        return context


class TestReportView(TemplateView):
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        test = get_object_or_404(Test, pk=self.kwargs['pk'])
        appointment = test.consultation.appointment
        hospital = test.consultation.appointment.specialist.hospital.first()
        today = datetime.today().date()
        patient = appointment.patient
        date_of_birth = patient.date_of_birth
        age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        context.update({
            'test': test,
            'appointment': appointment,
            'patient': patient,
            'hospital': hospital,
            'age': age
        })
        return context


# Download Test Report
class DownloadTestView(TemplateView):
    template_name = 'api/patient-test-pfd.html'

    def get(self, request, *args, **kwargs):
        # Retrieve data
        test = get_object_or_404(Test, pk=self.kwargs['pk'])
        appointment = test.consultation.appointment
        hospital = test.consultation.appointment.specialist.hospital.first()
        today = datetime.today().date()
        patient = appointment.patient
        date_of_birth = patient.date_of_birth
        age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))

        # Prepare context
        context = {
            'test': test,
            'appointment': appointment,
            'patient': patient,
            'hospital': hospital,
            'age': age
        }

        # Render template to string
        html_string = render_to_string(self.template_name, context)

        # Convert HTML to PDF
        buffer = BytesIO()
        pisa_status = pisa.CreatePDF(
            html_string,
            dest=buffer,
            encoding='utf-8'
        )
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html_string + '</pre>')

        pdf = buffer.getvalue()
        buffer.close()

        # Return PDF response
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="test_report.pdf"'
        return response


# Download Prescription
class DownloadPrescriptionView(TemplateView):
    template_name = 'api/patient-prescription-pdf.html'

    def get(self, request, *args, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        prescription = get_object_or_404(Prescription, pk=self.kwargs['pk'])
        patient = prescription.consultation.appointment.patient
        hospital = prescription.consultation.appointment.specialist.hospital.first()
        date_of_birth = patient.date_of_birth
        today = datetime.today().date()
        age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        context.update({
            'prescription': prescription,
            'age': age,
            'hospital': hospital,
            'patient': patient,
        })

        # Render template to string
        html_string = render_to_string(self.template_name, context)

        # Convert HTML to PDF
        buffer = BytesIO()
        pisa_status = pisa.CreatePDF(
            html_string,
            dest=buffer,
            encoding='utf-8'
        )
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html_string + '</pre>')

        pdf = buffer.getvalue()
        buffer.close()

        # Return PDF response
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="prescription_report.pdf"'
        return response


# feedbacks
class AddFeedbacksView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        specialist = get_object_or_404(Specialist, pk=self.kwargs['pk'])
        current_user = self.request.user
        patient = get_object_or_404(Patient, user=current_user)
        context['specialist'] = specialist
        context['patient'] = patient
        return context

    def post(self, request, *args, **kwargs):
        form = FeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            feedback = form.save(commit=False)
            patient = get_object_or_404(Patient, user=request.user)
            feedback.patient = patient
            feedback.save()
            messages.success(request, 'Feedback added successfully.')
            return redirect(
                'app-api-patient-dashboard')
        else:
            error_message = ' '.join([f'{key}: {value}' for key, value in form.errors.items()])
            messages.error(request, f'Failed to add feedback: {error_message}')

        return self.render_to_response(self.get_context_data(form=form))
