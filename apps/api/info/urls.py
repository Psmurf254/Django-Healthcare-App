from django.urls import path
from . import views


urlpatterns = [
    path('contact/', views.create_contact),
    path('about/', views.getAbout, name='about'),
    path('faq/', views.getFAQ, name='FAQ'),
    path('notification/create/<str:appointment_id>/', views.createPatientNotification),
    path('clear_notifications/', views.clearNotifications),
]
