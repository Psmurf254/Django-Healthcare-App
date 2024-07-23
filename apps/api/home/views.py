from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from apps.api.specialists.models import Specialist, SpecialistCategory, SpecialistFeedback, CommonConsultation, \
    Hospital
from web_project import TemplateLayout


class HomeView(TemplateView):
       def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context.update({
            'specialists': Specialist.objects.filter(verified=True),
            # 'top_specialists': Specialist.objects.filter(average_rating__gt=3),
            'top_specialists': Specialist.objects.all(),
            'common_consultations': CommonConsultation.objects.all(),
            'categories': SpecialistCategory.objects.all(),
            'hospitals': Hospital.objects.all()
        })
        return context


class DocDetailsView(TemplateView):
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        specialist = get_object_or_404(Specialist, pk=self.kwargs['pk'])
        reviews = SpecialistFeedback.objects.filter(specialist=specialist)

        context.update({
            'specialist': specialist,
            'doctor_review': reviews,
            'categories': SpecialistCategory.objects.all()
        })
        return context


class HowItWorksView(TemplateView):
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context
