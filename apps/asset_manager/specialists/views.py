from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView
from apps.api.specialists.models import Specialist, SpecialistCategory
from apps.asset_manager.forms import SpecialistForm, SpecialistUpdateForm
from web_project import TemplateLayout
from django.core.mail import send_mail
from django.conf import settings


class SpecialistView(PermissionRequiredMixin, TemplateView):
    permission_required = ["specialists.view_specialist"]

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context.update({
            'specialists': Specialist.objects.all(),
            'categories': SpecialistCategory.objects.all()
        })
        return context

    def post(self, request):
        form = SpecialistForm(request.POST, request.FILES)
        if form.is_valid():
            if not self.specialist_exists(form.cleaned_data):
                specialist = form.save(commit=False)
                specialist_user = self.create_user(specialist)

                if not specialist_user:
                    messages.error(request, 'User creation failed for the specialist')
                    return redirect('app-asset-manager-specialists-list')

                specialist.user = specialist_user

                # Set default values for availability and time fields
                specialist.sunday_availability = specialist._meta.get_field('sunday_availability').default
                specialist.monday_availability = specialist._meta.get_field('monday_availability').default
                specialist.tuesday_availability = specialist._meta.get_field('tuesday_availability').default
                specialist.wednesday_availability = specialist._meta.get_field('wednesday_availability').default
                specialist.thursday_availability = specialist._meta.get_field('thursday_availability').default
                specialist.friday_availability = specialist._meta.get_field('friday_availability').default
                specialist.saturday_availability = specialist._meta.get_field('saturday_availability').default

                specialist.sunday_start_time = specialist._meta.get_field('sunday_start_time').default
                specialist.sunday_end_time = specialist._meta.get_field('sunday_end_time').default
                specialist.monday_start_time = specialist._meta.get_field('monday_start_time').default
                specialist.monday_end_time = specialist._meta.get_field('monday_end_time').default
                specialist.tuesday_start_time = specialist._meta.get_field('tuesday_start_time').default
                specialist.tuesday_end_time = specialist._meta.get_field('tuesday_end_time').default
                specialist.wednesday_start_time = specialist._meta.get_field('wednesday_start_time').default
                specialist.wednesday_end_time = specialist._meta.get_field('wednesday_end_time').default
                specialist.thursday_start_time = specialist._meta.get_field('thursday_start_time').default
                specialist.thursday_end_time = specialist._meta.get_field('thursday_end_time').default
                specialist.friday_start_time = specialist._meta.get_field('friday_start_time').default
                specialist.friday_end_time = specialist._meta.get_field('friday_end_time').default
                specialist.saturday_start_time = specialist._meta.get_field('saturday_start_time').default
                specialist.saturday_end_time = specialist._meta.get_field('saturday_end_time').default

                specialist.save()

                messages.success(request, 'Specialist Added')
            else:
                messages.error(request, 'Specialist already exists')
        else:
            print(form.errors)
            error_message = ' '.join([f'{key}: {value}' for key, value in form.errors.items()])
            messages.error(request, f'Specialist Failed: {error_message}')
        return redirect('app-asset-manager-specialists-list')

    def create_user(self, specialist):
        password = 'password123'
        hashed_password = make_password(password)
        user_email = specialist.contact_email if specialist.contact_email else f"{specialist.full_name.lower().replace(' ', '_')}@gmail.com"
        try:
            user = User.objects.create(username=user_email, email=user_email, password=hashed_password)
            return user
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    def specialist_exists(self, cleaned_data):
        return Specialist.objects.filter(
            full_name__iexact=cleaned_data['full_name'],
        ).exists()



class SpecialistUpdateView(PermissionRequiredMixin, TemplateView):
    permission_required = ["specialists.change_specialist"]

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        specialist = get_object_or_404(Specialist, pk=self.kwargs['pk'])
        context.update({
            'specialist': specialist,
            'categories': SpecialistCategory.objects.all()
        })
        return context

    def post(self, request, pk):
        specialist = get_object_or_404(Specialist, pk=self.kwargs['pk'])
        form = SpecialistUpdateForm(request.POST, request.FILES, instance=specialist)
        if form.is_valid():
            specialist_update = form.save(commit=False)

            # Preserve the initial values for the availability fields and time ranges
            specialist_update.sunday_availability = specialist.sunday_availability
            specialist_update.monday_availability = specialist.monday_availability
            specialist_update.tuesday_availability = specialist.tuesday_availability
            specialist_update.wednesday_availability = specialist.wednesday_availability
            specialist_update.thursday_availability = specialist.thursday_availability
            specialist_update.friday_availability = specialist.friday_availability
            specialist_update.saturday_availability = specialist.saturday_availability

            specialist_update.sunday_start_time = specialist.sunday_start_time
            specialist_update.sunday_end_time = specialist.sunday_end_time
            specialist_update.monday_start_time = specialist.monday_start_time
            specialist_update.monday_end_time = specialist.monday_end_time
            specialist_update.tuesday_start_time = specialist.tuesday_start_time
            specialist_update.tuesday_end_time = specialist.tuesday_end_time
            specialist_update.wednesday_start_time = specialist.wednesday_start_time
            specialist_update.wednesday_end_time = specialist.wednesday_end_time
            specialist_update.thursday_start_time = specialist.thursday_start_time
            specialist_update.thursday_end_time = specialist.thursday_end_time
            specialist_update.friday_start_time = specialist.friday_start_time
            specialist_update.friday_end_time = specialist.friday_end_time
            specialist_update.saturday_start_time = specialist.saturday_start_time
            specialist_update.saturday_end_time = specialist.saturday_end_time

            specialist_update.save()
            messages.success(request, 'Specialist updated successfully')
        else:
            print(form.errors)
            messages.error(request, 'Specialist failed to update. ' + ' '.join(form.errors))
        return redirect('app-asset-manager-specialists-list')





class SpecialistDeleteView(PermissionRequiredMixin, TemplateView):
    permission_required = ["specialists.delete_specialist"]

    def get(self, request, pk):
        specialist = get_object_or_404(Specialist, id=pk)
        user = specialist.user
        specialist.delete()
        user.delete()
        messages.success(request, f'specialist Deleted')
        return redirect('app-asset-manager-specialists-list')

class SpecialistUpdateVerification(PermissionRequiredMixin, TemplateView):
    permission_required = ["specialists.change_specialist"]
    def get(self, request, specialist_id):
        specialist = get_object_or_404(Specialist, id=specialist_id)
        if specialist.verified:
            specialist.verified = False
            messages.success(request, f'{specialist.full_name} Verification updated.')
        else:
            specialist.verified = True
            # Send the email to specialist
            specialist_email_subject = 'Account Verification Notification'
            specialist_email_message = f"""
                            Dear Dr. {specialist.full_name},

                            This is to inform you that your account has been verified and your profile has been published on our website to receive patients.

                            If you need further information, please contact us at {settings.CONTACT_EMAIL}.

                            Best regards,
                            Health360
                            """

            send_mail(
                specialist_email_subject,
                specialist_email_message,
                settings.DEFAULT_FROM_EMAIL,
                [specialist.contact_email],
                fail_silently=False,
            )
            messages.success(request, f'{specialist.full_name} Verification updated.')

        specialist.save()
        return redirect('app-asset-manager-specialists-list')
