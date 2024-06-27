from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView, DeleteView

from apps.api.patients.models import Patient
from apps.api.specialists.models import SpecialistFeedback, Specialist
from apps.asset_manager.forms import FeedbackForm
from web_project import TemplateLayout


class FeedbacksView(PermissionRequiredMixin, TemplateView):
    permission_required = ["specialists.view_specialistfeedback"]

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context.update({'feedbacks': SpecialistFeedback.objects.all(),
                        'specialists': Specialist.objects.all(),
                        'patients': Patient.objects.all(),
                        })
        print(Specialist.objects.all().count())
        return context

    def post(self, request):
        form = FeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'feedback Added')
        else:
            error_message = ' '.join([f'{key}: {value}' for key, value in form.errors.items()])
            messages.error(request, f'feedback Failed: {error_message}')
        return redirect('app-asset-manager-feedbacks-list')


class FeedbacksUpdateView(PermissionRequiredMixin, TemplateView):
    permission_required = ["specialists.change_specialistfeedback"]

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        feedback = get_object_or_404(SpecialistFeedback, pk=self.kwargs['pk'])
        context.update({
            'feedback': feedback,
            'specialists': Specialist.objects.all(),
            'patients': Patient.objects.all(),
        })
        return context

    def post(self, request, pk):
        feedback = get_object_or_404(SpecialistFeedback, pk=self.kwargs['pk'])
        form = FeedbackForm(request.POST, request.FILES, instance=feedback)
        if form.is_valid():
            form.save()
            messages.success(request, 'feedback updated successfully')
        else:
            messages.error(request, f'feedback failed to updated'.join(form.errors))
        return redirect('app-asset-manager-feedbacks-list')


class FeedbacksDeleteView(PermissionRequiredMixin, TemplateView):

    permission_required =["specialists.delete_specialistfeedback"]

    def get(self, request, pk):
        feedback = get_object_or_404(SpecialistFeedback, id=pk)
        feedback.delete()
        messages.success(request, f'feedback Deleted')
        return redirect('app-asset-manager-feedbacks-list')
