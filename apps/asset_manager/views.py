from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView, DeleteView
from apps.api.patients.models import Patient
from apps.api.specialists.models import SpecialistCategory
from apps.asset_manager.forms import PatientForm, CategoryForm
from web_project import TemplateLayout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

"""
This file is a view controller for multiple pages as a module.
Here you can override the page view layout.
Refer to sample/urls.py file for more pages.
"""


class PatientsView(PermissionRequiredMixin, TemplateView):
    permission_required = []

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context.update({'patients': Patient.objects.all()})
        return context

    def post(self, request):
        form = PatientForm(request.POST, request.FILES)
        if form.is_valid():
            if not self.patient_exists(form.cleaned_data):
                patient = form.save(commit=False)  # Save form data without committing to the database
                patient_user = self.create_user(patient)
                # Ensure the user creation was successful
                if not patient_user:
                    messages.error(request, 'User creation failed for the patient')
                    return redirect('app-asset-manager-patients-list')

                # Assign the created user to the patient and save the patient instance
                patient.user = patient_user
                patient.save()

                messages.success(request, 'Patient Added')
            else:
                messages.error(request, 'Patient already exists')
        else:
            error_message = ' '.join([f'{key}: {value}' for key, value in form.errors.items()])
            messages.error(request, f'Patient Failed: {error_message}')
        return redirect('app-asset-manager-patients-list')

    def create_user(self, patient):
        password = 'password123'
        hashed_password = make_password(password)
        user_email = patient.contact_email if patient.contact_email else f"{patient.full_name.lower().replace(' ', '_')}@gmail.com"
        try:
            user = User.objects.create(username=user_email, email=user_email, password=hashed_password)
            return user
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    def patient_exists(self, cleaned_data):
        return Patient.objects.filter(
            full_name__iexact=cleaned_data['full_name'],
        ).exists()

class PatientsUpdateView(PermissionRequiredMixin, TemplateView):
    permission_required = ()
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
            form.save()
            messages.success(request, 'Patient updated successfully')
        else:
            messages.error(request, f'Patient failed to updated'.join(form.errors))
        return redirect('app-asset-manager-patients-list')

class PatientsDeleteView(PermissionRequiredMixin, TemplateView):
    permission_required = ()
    def get(self, request, pk):
        patient = get_object_or_404(Patient, id=pk)
        patient.delete()
        if patient:
            user = get_object_or_404(User, username=patient.contact_email)
            user.delete()
        messages.success(request, f'{patient.full_name} Deleted')
        return redirect('app-asset-manager-patients-list')

# CATEGORIES
class CategoriesView(PermissionRequiredMixin, TemplateView):
    permission_required = []

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context.update({'categories': SpecialistCategory.objects.all()})
        return context

    def post(self, request):
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            if not self.category_exists(form.cleaned_data):
                category = form
                category.save()
                messages.success(request, 'Category  Added')
            else:
                messages.error(request, 'Category already exists')
        else:
            error_message = ' '.join([f'{key}: {value}' for key, value in form.errors.items()])
            messages.error(request, f'Category Failed: {error_message}')
        return redirect('app-asset-manager-categories-list')

    def category_exists(self, cleaned_data):
        return SpecialistCategory.objects.filter(
            name__iexact=cleaned_data['name'],
        ).exists()

# CATEGORY UPDATE
class CategoryUpdateView(PermissionRequiredMixin, TemplateView):
    permission_required = ()
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        category = get_object_or_404(SpecialistCategory, pk=self.kwargs['pk'])
        context.update({
            'category': category,
        })
        return context

    def post(self, request, pk):
        category = get_object_or_404(SpecialistCategory, pk=self.kwargs['pk'])
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully')
        else:
            messages.error(request, f'Category failed to updated'.join(form.errors))
        return redirect('app-asset-manager-categories-list')


# CATEGORY DELETE
class CategoryDeleteView(PermissionRequiredMixin, TemplateView):
    permission_required = ()
    def get(self, request, pk):
        category = get_object_or_404(SpecialistCategory, id=pk)
        category.delete()
        messages.success(request, f'{category.name} Deleted')
        return redirect('app-asset-manager-categories-list')

