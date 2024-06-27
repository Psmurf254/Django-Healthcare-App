from django.urls import path
from . import views
from .views import  PatientListView, PatientRetrieveUpdateDestroyView
from .views import *

urlpatterns = [
    path('patient/account/create/', views.createPatientAccount),
    path('patient_Data/',  PatientListView.as_view()),
    path('patients/update/<str:pk>/', PatientRetrieveUpdateDestroyView.as_view())
]
