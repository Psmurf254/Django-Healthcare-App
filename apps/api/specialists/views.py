from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from apps.api.specialists.models import Specialist, SpecialistCategory, SpecialistFeedback, CommonConsultation, \
    Hospital
from web_project import TemplateLayout


class SpecialistsView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(SpecialistCategory, pk=self.kwargs['pk'])
        specialists = Specialist.objects.filter(category=category)
        context.update({
            'category': category,
            'specialists': specialists,
        })
        return context


class DocDetailsView(TemplateView):
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        specialist = get_object_or_404(Specialist, pk=self.kwargs['pk'])
        reviews = SpecialistFeedback.objects.filter(specialist=specialist)
        hospitals = specialist.hospital.all()


        context.update({
            'hospitals': hospitals,
            'specialist': specialist,
            'doctor_review': reviews,
            'categories': SpecialistCategory.objects.all()
        })
        return context
