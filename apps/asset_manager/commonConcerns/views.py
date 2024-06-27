from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView
from apps.api.specialists.models import CommonConsultation, SpecialistCategory
from apps.asset_manager.forms import CommonConcernForm
from web_project import TemplateLayout


class CommonConcernView(PermissionRequiredMixin, TemplateView):
    permission_required = ["specialists.view_commonconsultation"]

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context.update({'concerns': CommonConsultation.objects.all(),
                        'categories': SpecialistCategory.objects.all()
                        })
        return context

    def post(self, request):
        form = CommonConcernForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'item Added')
        else:
            error_message = ' '.join([f'{key}: {value}' for key, value in form.errors.items()])
            messages.error(request, f'feedback Failed: {error_message}')
        return redirect('app-asset-manager-concerns-list')


class CommonConcernUpdateView(PermissionRequiredMixin, TemplateView):
    permission_required = ["specialists.change_commonconsultation"]

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        concern = get_object_or_404(CommonConsultation, pk=self.kwargs['pk'])
        context.update({
            'concern': concern,
            'categories': SpecialistCategory.objects.all()
        })
        return context

    def post(self, request, pk):
        concern = get_object_or_404(CommonConsultation, pk=self.kwargs['pk'])
        form = CommonConcernForm(request.POST, request.FILES, instance=concern)
        if form.is_valid():
            form.save()
            messages.success(request, 'item updated successfully')
        else:
            messages.error(request, f'item failed to updated'.join(form.errors))
        return redirect('app-asset-manager-concerns-list')


class CommonConcernDeleteView(PermissionRequiredMixin, TemplateView):
    permission_required = ["specialists.delete_commonconsultation"]

    def get(self, request, pk):
        feedback = get_object_or_404(CommonConsultation, id=pk)
        feedback.delete()
        messages.success(request, f'item Deleted')
        return redirect('app-asset-manager-concerns-list')
