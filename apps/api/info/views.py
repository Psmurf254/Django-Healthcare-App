from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import TemplateView

from apps.api.info.models import About
from apps.asset_manager.forms import ContactForm
from web_project import TemplateLayout


class AboutView(TemplateView):
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        about = About.objects.first()
        context.update({
            'about': about,
        })
        return context


class ContactView(TemplateView):

    def post(self, request):
        form = ContactForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Message sent successfully')
        else:
            print(form.errors)
            messages.error(request, f'Failed to submit message'.join(form.errors))
        return redirect('app-api-contact-success')


class ContactSuccess(TemplateView):
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context
