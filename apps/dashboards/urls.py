from django.urls import path
from .views import DashboardsView
from django.contrib.auth.decorators import login_required
from ..asset_manager.appointments.views import AppointmentView


urlpatterns = [
    path(
        'dashboard/',
        login_required(AppointmentView.as_view(template_name="app_appointment_list.html")),
        name="index",
    ),
    path(
        'crm/',
        login_required(DashboardsView.as_view(template_name="dashboard.html")),
        name="crm",
    ),
]
