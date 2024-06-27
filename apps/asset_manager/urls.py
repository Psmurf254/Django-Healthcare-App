from django.contrib.auth.decorators import login_required
from django.urls import path
from .appointments.views import AppointmentView, AppointmentUpdateView, AppointmentsDeleteView
from .commonConcerns.views import CommonConcernDeleteView, CommonConcernUpdateView, CommonConcernView
from .feedbacks.views import FeedbacksView, FeedbacksUpdateView, FeedbacksDeleteView
from .info.views import ContactView, ContactUpdateView, ContactDeleteView, AboutView, AboutUpdateView, AboutDeleteView, \
    FAQView, FAQUpdateView, FAQtDeleteView
from .notifications.views import NotificationView, NotificationDeleteView
from .specialists.views import SpecialistView, SpecialistUpdateView, SpecialistDeleteView, SpecialistUpdateVerification
from .views import PatientsView, PatientsUpdateView, \
    PatientsDeleteView, CategoriesView, CategoryUpdateView, CategoryDeleteView

urlpatterns = [

    path(
        "patients/",
        login_required(PatientsView.as_view(template_name="app_patients_list.html")),
        name="app-asset-manager-patients-list",
    ),
    path(
        "patient/update/<str:pk>",
        login_required(PatientsUpdateView.as_view(template_name="app_patients_update.html")),
        name="app-asset-manager-patient-update",
    ),
    path(
        "patient/delete/<str:pk>/",
        login_required(PatientsDeleteView.as_view()),
        name="app-asset-manager-patients-delete",
    ),

    path(
        "categories/",
        login_required(CategoriesView.as_view(template_name="app_category_list.html")),
        name="app-asset-manager-categories-list",
    ),
    path(
        "category/update/<str:pk>",
        login_required(CategoryUpdateView.as_view(template_name="app_categories_update.html")),
        name="app-asset-manager-categories-update",
    ),
    path(
        "category/delete/<str:pk>/",
        login_required(CategoryDeleteView.as_view()),
        name="app-asset-manager-categories-delete",
    ),

    path(
        "appointments/",
        login_required(AppointmentView.as_view(template_name="app_appointment_list.html")),
        name="app-asset-manager-appointments-list",
    ),
    path(
        "appointment/update/<str:pk>",
        login_required(AppointmentUpdateView.as_view(template_name="app_appointment_update.html")),
        name="app-asset-manager-appointment-update",
    ),
    path(
        "appointment/delete/<str:pk>/",
        login_required(AppointmentsDeleteView.as_view()),
        name="app-asset-manager-appointment-delete",
    ),

    path(
        "specialists/",
        login_required(SpecialistView.as_view(template_name="app_specialists_list.html")),
        name="app-asset-manager-specialists-list",
    ),
    path(
        "specialist/update/<str:pk>",
        login_required(SpecialistUpdateView.as_view(template_name="app_specialist_update.html")),
        name="app-asset-manager-specialist-update",
    ),
    path(
        "specialist/delete/<str:pk>/",
        login_required(SpecialistDeleteView.as_view()),
        name="app-asset-manager-specialist-delete",
    ),
    path(
        "specialist/verification/update/<str:specialist_id>/",
        login_required(SpecialistUpdateVerification.as_view(template_name="app_specialist_update.html")),
        name="app-asset-manager-specialist-verification-update",
    ),
    path(
        "concerns/",
        login_required(CommonConcernView.as_view(template_name="app_concerns_list.html")),
        name="app-asset-manager-concerns-list",
    ),
    path(
        "concern/update/<str:pk>",
        login_required(CommonConcernUpdateView.as_view(template_name="app_concern_update.html")),
        name="app-asset-manager-concern-update",
    ),
    path(
        "concern/delete/<str:pk>/",
        login_required(CommonConcernDeleteView.as_view()),
        name="app-asset-manager-concern-delete",
    ),

    path(
        "feedbacks/",
        login_required(FeedbacksView.as_view(template_name="app_feedbacks_list.html")),
        name="app-asset-manager-feedbacks-list",
    ),
    path(
        "feedback/update/<str:pk>",
        login_required(FeedbacksUpdateView.as_view(template_name="app_feedback_update.html")),
        name="app-asset-manager-feedback-update",
    ),
    path(
        "feedback/delete/<str:pk>/",
        login_required(FeedbacksDeleteView.as_view()),
        name="app-asset-manager-feedback-delete",
    ),

    path(
        "contacts/",
        login_required(ContactView.as_view(template_name="app_contacts_list.html")),
        name="app-asset-manager-contacts-list",
    ),
    path(
        "contact/update/<str:pk>",
        login_required(ContactUpdateView.as_view(template_name="app_contact_update.html")),
        name="app-asset-manager-contact-update",
    ),
    path(
        "contact/delete/<str:pk>/",
        login_required(ContactDeleteView.as_view()),
        name="app-asset-manager-contacts-list",
    ),

    path(
        "faqs/",
        login_required(FAQView.as_view(template_name="app_faqs_list.html")),
        name="app-asset-manager-faqs-list",
    ),
    path(
        "faq/update/<str:pk>",
        login_required(FAQUpdateView.as_view(template_name="app_faq_update.html")),
        name="app-asset-manager-faq-update",
    ),
    path(
        "faqs/delete/<str:pk>/",
        login_required(FAQtDeleteView.as_view()),
        name="app-asset-manager-faq-delete",
    ),

    path(
        "abouts/",
        login_required(AboutView.as_view(template_name="app_abouts_list.html")),
        name="app-asset-manager-abouts-list",
    ),
    path(
        "about/update/<str:pk>",
        login_required(AboutUpdateView.as_view(template_name="app_about_update.html")),
        name="app-asset-manager-about-update",
    ),
    path(
        "about/delete/<str:pk>/",
        login_required(AboutDeleteView.as_view()),
        name="app-asset-manager-about-delete",
    ),
    path(
        "notifications/",
        login_required(NotificationView.as_view(template_name="app_notifications.html")),
        name="app-asset-manager-notifications",
    ),
    path(
        "notifications/delete/<str:pk>/",
        login_required(NotificationDeleteView.as_view()),
        name="app-asset-manager-notifications-delete",
    ),

]
