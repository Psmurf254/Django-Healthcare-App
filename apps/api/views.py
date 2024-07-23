from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from apps.api.specialists.models import Specialist, SpecialistCategory, SpecialistFeedback
from web_project import TemplateLayout


class HomeView(TemplateView):
       def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        context.update({
            'specialists': Specialist.objects.all(),
            'categories': SpecialistCategory.objects.all()
        })
        return context



