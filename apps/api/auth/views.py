from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from apps.api.patients.models import Patient
from apps.api.specialists.models import Specialist, SpecialistCategory
from auth.views import AuthView


class PatientRegisterView(TemplateView):
    template_name = 'patient_register.html'

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        full_name = request.POST.get('full_name')
        hashed_password = make_password(password)

        # Check if a patient with the same email already exists
        if Patient.objects.filter(contact_email=email).exists():
            messages.error(request, 'A patient with this email already exists.')
            return redirect('app-api-patient-register')

        try:
            user = User.objects.create(username=username, email=email, password=hashed_password)
            patient = Patient(
                user=user,
                full_name=full_name,
                contact_email=email,
            )
            patient.save()
            messages.success(request, 'Account successfully created. Update your details to proceed.')
            return redirect(reverse_lazy('app-api-patient-update', kwargs={'pk': patient.pk}))
        except Exception as e:
            print(f"Error creating user: {e}")
            messages.error(request, 'Failed to create account. Please try again later.')
            return redirect('app-api-patient-register')



class DoctorRegisterView(TemplateView):
    template_name = 'doctor_register.html'

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        full_name = request.POST.get('full_name')
        hashed_password = make_password(password)

        # Check if a specialist with the same email already exists
        if Specialist.objects.filter(contact_email=email).exists():
            messages.error(request, 'A specialist with this email already exists.')
            return redirect('app-api-doc-register')

        try:
            user = User.objects.create(username=username, email=email, password=hashed_password)
            category, created = SpecialistCategory.objects.get_or_create(name='Other')
            specialist = Specialist(
                user=user,
                full_name=full_name,
                contact_email=email,
                category=category,
            )
            specialist.save()
            if not specialist:
                user.delete()
                messages.error(request, 'Failed to create account')
                return redirect('app-api-doc-register')
            messages.success(request, 'Account successfully created. Update your details to proceed.')
            return redirect(reverse_lazy('app-api-doc-profile-update', kwargs={'pk': specialist.pk}))
        except Exception as e:
            messages.error(request, 'Failed To Create Account. Please Try again Later.')
            return redirect('app-api-doc-register')





class PatientLoginView(AuthView):
    def get(self, request):
        if request.user.is_authenticated:
            # If the user is already logged in, redirect them to the home page or another appropriate page.
            return redirect("app-api-patient-dashboard")  # Replace 'app-api-patient-dashboard' with the actual URL name for the home page

        # Render the login page for users who are not logged in.
        return super().get(request)

    def post(self, request):
        if request.method == "POST":
            username = request.POST.get("email-username")
            password = request.POST.get("password")

            if not (username and password):
                messages.error(request, "Please enter your username and password.")
                return redirect("app-api-patient-login")

            if "@" in username:
                user_email = User.objects.filter(email=username).first()
                if user_email is None:
                    messages.error(request, "Please enter a valid email.")
                    return redirect("app-api-patient-login")
                username = user_email.username

            user_email = User.objects.filter(username=username).first()
            if user_email is None:
                messages.error(request, "Please enter a valid username.")
                return redirect("app-api-patient-login")

            authenticated_user = authenticate(request, username=username, password=password)
            if authenticated_user is not None:
                # Login the user if authentication is successful
                login(request, authenticated_user)

                # Redirect to the page the user was trying to access before logging in
                if "next" in request.POST:
                    return redirect(request.POST["next"])
                else: # Redirect to the home page or another appropriate page
                    return redirect("app-api-patient-dashboard")
            else:
                messages.error(request, "Please enter a valid username.")
                return redirect("app-api-patient-login")

class DoctorLoginView(AuthView):
    def get(self, request):
        if request.user.is_authenticated:
            # If the user is already logged in, redirect them to the home page or another appropriate page.
            return redirect("app-api-doc-dashboard")  # Replace 'app-api-home' with the actual URL name for the home page

        # Render the login page for users who are not logged in.
        return super().get(request)

    def post(self, request):
        if request.method == "POST":
            username = request.POST.get("email-username")
            password = request.POST.get("password")

            if not (username and password):
                messages.error(request, "Please enter your username and password.")
                return redirect("app-api-doc-login")

            if "@" in username:
                user_email = User.objects.filter(email=username).first()
                if user_email is None:
                    messages.error(request, "Please enter a valid email.")
                    return redirect("app-api-doc-login")
                username = user_email.username

            user_email = User.objects.filter(username=username).first()
            if user_email is None:
                messages.error(request, "Please enter a valid username.")
                return redirect("app-api-doc-login")

            authenticated_user = authenticate(request, username=username, password=password)
            if authenticated_user is not None:
                # Login the user if authentication is successful
                login(request, authenticated_user)

                # Redirect to the page the user was trying to access before logging in
                if "next" in request.POST:
                    return redirect(request.POST["next"])
                else: # Redirect to the home page or another appropriate page
                    return redirect("app-api-doc-dashboard")
            else:
                messages.error(request, "Please enter a valid username.")
                return redirect("app-api-doc-login")
