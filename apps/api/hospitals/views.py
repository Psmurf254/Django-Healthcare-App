from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from apps.api.specialists.models import Hospital, Specialist
from web_project import TemplateLayout


class HospitalDetailsView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hospital = get_object_or_404(Hospital, pk=self.kwargs['pk'])
        specialists = Specialist.objects.filter(hospital=hospital)
        context.update({
            'hospital': hospital,
            'specialists': specialists,
        })
        return context


