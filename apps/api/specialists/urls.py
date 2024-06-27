from django.urls import path
from . import views
from .views import SpecialistDatalistView, AppointmentListView, SpecialistRetrieveUpdateDestroyView

urlpatterns = [
    path('specialist_categories/', views.getAllCategories),
    path('categories_with_Items/', views.getCategoriesWithItems),
    path('CategoryById/<str:category_id>/', views.getCategoryById, name='specialistByCategory'),

    path('specialistByCategories/<str:category_id>/', views.getSpecialistByCategories),
    path('specialistById/<str:specialist_id>/', views.getSpecialistById),
    path('specialist/account/create/', views.createSpecialistAccount),

    path('specialistFeedbacks/<str:specialist_id>/', views.specialist_feedback),
    path('specialist_review/create/<str:id>/', views.create_specialist_feedback),


    path('appointmentData/<str:specialist_id>/', views.getSpecialistAppointments),
    path('appointment/create/<str:id>/', AppointmentListView.as_view()),
    path('appointment/update/<str:id>/', views.updateAppointment),

    path('create_appointment/', views.createAppointment),

    path('commonConsultations/', views.common_Concerns),

    path('specialist_Data/', SpecialistDatalistView.as_view()),
    path('specialist/update/<str:pk>/', SpecialistRetrieveUpdateDestroyView.as_view()),
    path('create-diagnosis/<str:appointment_id>/', views.create_diagnosis),

    path('appointment/<str:id>/', views.getAppointment),
    path('create_payment/', views.iniate_stk_push),
    path('payment_waiting/<str:appointment_id>/', views.payment_waiting, name='payment_waiting'),
    path('payment_webhook/<str:appointment_id>/', views.payment_webhook, name='payment_webhook'),
]
