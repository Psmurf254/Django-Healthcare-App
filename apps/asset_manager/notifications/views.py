from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView
from apps.asset_manager.forms import NotificationForm
from web_project import TemplateLayout
from apps.api.info.models import Notification as Messages


class NotificationView(PermissionRequiredMixin,TemplateView):
    permission_required = ["asset_manager.view_notification"]
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context.update({
            'notifications': Messages.objects.all(),
            'users': User.objects.all(),
            })
        print(Messages.objects.all().count())
        return context
    def post(self, request):
        form = NotificationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notification Added')
        else:
            print(form.errors)
            error_message = ' '.join([f'{key}: {value}' for key, value in form.errors.items()])
            messages.error(request, f'Notification Failed: {error_message}')
        return redirect('app-asset-manager-notifications')

class NotificationDeleteView(PermissionRequiredMixin, TemplateView):
    permission_required = ["asset_manager.delete_notification"]
    def get(self, request, pk):
        notification = get_object_or_404(Messages, id=pk)
        notification.delete()
        messages.success(request, f'{notification.subject} Deleted')
        return redirect('app-asset-manager-notifications')



