from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView, DeleteView
from apps.api.info.models import Contact, About, FAQ
from apps.asset_manager.forms import ContactForm, AboutForm, FAQForm
from web_project import TemplateLayout
from django.http import Http404


class ContactView(PermissionRequiredMixin, TemplateView):
    permission_required = ['info.view_contact']

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context.update({'contacts': Contact.objects.all()})
        return context

    def post(self, request):
        form = ContactForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'contact Added')
        else:
            error_message = ' '.join([f'{key}: {value}' for key, value in form.errors.items()])
            messages.error(request, f'contact Failed: {error_message}')
        return redirect('app-asset-manager-contacts-list')


class ContactUpdateView(PermissionRequiredMixin, TemplateView):
    permission_required = ['info.change_contact']

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        contact = get_object_or_404(Contact, pk=self.kwargs['pk'])
        context.update({
            'contact': contact,
        })
        return context

    def post(self, request, pk):
        contact = get_object_or_404(Contact, pk=self.kwargs['pk'])
        form = ContactForm(request.POST, request.FILES, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, 'contact updated successfully')
        else:
            messages.error(request, f'contact failed to updated'.join(form.errors))
        return redirect('app-asset-manager-contacts-list')


class ContactDeleteView(PermissionRequiredMixin, TemplateView):
    permission_required = ['info.delete_contact']

    def get(self, request, pk):
        contact = get_object_or_404(Contact, id=pk)
        contact.delete()
        messages.success(request, f'contact Deleted')
        return redirect('app-asset-manager-contacts-list')


class AboutView(PermissionRequiredMixin, TemplateView):
    permission_required = ['info.view_about']

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context.update({'abouts': About.objects.all()})
        return context

    def post(self, request):
        form = AboutForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'about Added')
        else:
            error_message = ' '.join([f'{key}: {value}' for key, value in form.errors.items()])
            messages.error(request, f'feedback Failed: {error_message}')
        return redirect('app-asset-manager-abouts-list')


class AboutUpdateView(PermissionRequiredMixin, TemplateView):
    permission_required = ['info.change_about']

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        about = get_object_or_404(About, pk=self.kwargs['pk'])
        context.update({
            'about': about,
        })
        return context

    def post(self, request, pk):
        about = get_object_or_404(About, pk=self.kwargs['pk'])
        form = AboutForm(request.POST, request.FILES, instance=about)
        if form.is_valid():
            form.save()
            messages.success(request, 'about updated successfully')
        else:
            messages.error(request, f'about failed to updated'.join(form.errors))
        return redirect('app-asset-manager-abouts-list')


class AboutDeleteView(PermissionRequiredMixin, TemplateView):
    permission_required = ['info.delete_about']

    def get(self, request, pk):
        about = get_object_or_404(About, id=pk)
        about.delete()
        messages.success(request, f'about Deleted')
        return redirect('app-asset-manager-abouts-list')


class FAQView(PermissionRequiredMixin, TemplateView):
    permission_required = ['info.view_faq']

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context.update({'faqs': FAQ.objects.all()})
        return context

    def post(self, request):
        form = FAQForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item Added')
        else:
            error_message = ' '.join([f'{key}: {value}' for key, value in form.errors.items()])
            messages.error(request, f'feedback Failed: {error_message}')
        return redirect('app-asset-manager-faqs-list')


class FAQUpdateView(PermissionRequiredMixin, TemplateView):
    permission_required = ['info.change_faq']

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        faq=get_object_or_404(FAQ, pk=self.kwargs['pk'])
        context.update({
            'faq': faq,
        })
        return context

    def post(self, request, pk):
        faq = get_object_or_404(FAQ, pk=self.kwargs['pk'])
        form = FAQForm(request.POST, instance=faq)
        if form.is_valid():
            form.save()
            messages.success(request, 'item updated successfully')
        else:
            messages.error(request, f'item failed to updated'.join(form.errors))
        return redirect('app-asset-manager-faqs-list')


class FAQtDeleteView(PermissionRequiredMixin, TemplateView):
    permission_required = ['info.delete_faq']

    def get(self, request, pk):
        faq = get_object_or_404(FAQ, id=pk)
        faq.delete()
        messages.success(request, f'item Deleted')
        return redirect('app-asset-manager-faqs-list')

