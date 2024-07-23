from django.contrib.auth.decorators import login_required
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .appointments.views import AppointmentAddView
from .auth.views import PatientRegisterView, DoctorRegisterView, PatientLoginView, DoctorLoginView
from .dashboards.patients.views import PatientDashboardView, PatientProfileUpdateView, AddFeedbacksView, \
    PrescriptionView, DownloadPrescriptionView, TestReportView, DownloadTestView
from .dashboards.specialists.views import DoctorDashboardView, DocProfileView, DocProfileUpdateView, \
    DocTransactionsView, AppointmentStatusUpdateView, PrescriptionAddView, OrderTestView, UpdateTestResultView, \
    TestReportAndPrescriptionView
from .hospitals.views import HospitalDetailsView
from .info.views import ContactView, AboutView, ContactSuccess
from .specialists.views import SpecialistsView, DocDetailsView
from .videoChat.views import VideoChatView
from ..api.home.views import HomeView, HowItWorksView

urlpatterns = [
    path(
        "",
        (HomeView.as_view(template_name="home.html")),
        name="app-api-home",
    ),
    path(
        "how-it-works",
        (HowItWorksView.as_view(template_name="how-it-works.html")),
        name="app-api-how-it-works",
    ),
    # specialists by category
    path(
        "doctors/<str:pk>/",
        (SpecialistsView.as_view(template_name="doctors.html")),
        name="app-api-doc-list",
    ),
    path(
        "doc-details/<str:pk>/",
        (DocDetailsView.as_view(template_name="doc-profile.html")),
        name="app-api-doc-details",
    ),
    # Add Appointment
    path(
        "add-appointment/<str:pk>/",
        login_required(AppointmentAddView.as_view(template_name="add-appointment.html")),
        name="app-api-appointment-add",
    ),
    # Patient Dashboard
    path(
        "patient-dashboard/",
        login_required(PatientDashboardView.as_view(template_name="patient-dashboard.html")),
        name="app-api-patient-dashboard",
    ),

    path(
        "patient-update-profile/<str:pk>/",
        login_required(PatientProfileUpdateView.as_view(template_name="patient-update.html")),
        name="app-api-patient-update",
    ),
    path(
        "add-feedback/<str:pk>/",
        login_required(AddFeedbacksView.as_view(template_name="feedback-add.html")),
        name="app-api-patient-add-feedback",
    ),
    # Test Reports list
    path(
        "doc-test-reports/",
        login_required(TestReportAndPrescriptionView.as_view(template_name="app-api-doc-test-reports.html")),
        name="app-api-doc-test-reports-list",
    ),
    # order test
    path(
        "order-test/<str:pk>/",
        login_required(OrderTestView.as_view(template_name="app-api-order-test.html")),
        name="app-api-doc-order-test",
    ),
    # test update results
    path(
        "test-update-results/<str:pk>/",
        login_required(UpdateTestResultView.as_view(template_name="app-api-test-update.html")),
        name="app-api-doc-update-test",
    ),
    # Add Prescription
    path(
        "create-prescription/<str:pk>/",
        login_required(PrescriptionAddView.as_view(template_name="app-api-prescription-add.html")),
        name="app-api-appointment-add-prescription",
    ),
    path(
        "patient-prescription/<str:pk>/",
        login_required(PrescriptionView.as_view(template_name="prescription-view.html")),
        name="app-api-patient-prescription",
    ),
    # Test view
    path(
        "patient-test-view/<str:pk>/",
        login_required(TestReportView.as_view(template_name="app-api-test-view.html")),
        name="app-api-patient-test-report",
    ),
    path(
        "download-test-report/<str:pk>/",
        login_required(DownloadTestView.as_view(template_name="patient-test-pfd.html")),
        name="app-api-test-generate_pdf",
    ),
    path(
        "download-prescription/<str:pk>/",
        login_required(DownloadPrescriptionView.as_view(template_name="patient-prescription-pfd.html")),
        name="app-api-prescription-generate_pdf",
    ),

    # Doc Dashboard
    path(
        "doc-dashboard/",
        login_required(DoctorDashboardView.as_view(template_name="app-api-doc-dash.html")),
        name="app-api-doc-dashboard",
    ),
    path(
        "doc-profile/<str:pk>/",
        login_required(DocProfileView.as_view(template_name="doc-myprofile.html")),
        name="app-api-doc-profile",
    ),
    path(
        "doc-profile-update/<str:pk>/",
        login_required(DocProfileUpdateView.as_view(template_name="doc-profile-setting.html")),
        name="app-api-doc-profile-update",
    ),
    path(
        "doc-transactions/<str:pk>/",
        login_required(DocTransactionsView.as_view(template_name="doc-transactions.html")),
        name="app-api-doc-transactions",
    ),
    path(
        "appointment-update-status/<str:pk>/",
        login_required(AppointmentStatusUpdateView.as_view()),
        name="app-api-appointment-update-status",
    ),

    # auth
    path(
        "patient-register/",
        (PatientRegisterView.as_view(template_name="patient-register.html")),
        name="app-api-patient-register",
    ),
    path(
        "patient-login/",
        (PatientLoginView.as_view(template_name="patient-login.html")),
        name="app-api-patient-login",
    ),
    path(
        "doc-register/",
        (DoctorRegisterView.as_view(template_name="doctor-register.html")),
        name="app-api-doc-register",
    ),
    path(
        "doc-login/",
        (DoctorLoginView.as_view(template_name="doctor-login.html")),
        name="app-api-doc-login",
    ),
    # about
    path(
        "about-us/",
        (AboutView.as_view(template_name="about.html")),
        name="app-api-about",
    ),
    # contact
    path(
        "contact-us/",
        (ContactView.as_view(template_name="contact.html")),
        name="app-api-contact",
    ),
    # Contact success
    path(
        "contact-success/",
        (ContactSuccess.as_view(template_name="contact-success.html")),
        name="app-api-contact-success",
    ),

    # Video Chat
    path(
        "video-conference/<str:pk>/",
        (VideoChatView.as_view(template_name="video-conference.html")),
        name="app-api-video-chat",
    ),

    # Hospital
    path(
        "hospital/<str:pk>/",
        (HospitalDetailsView.as_view(template_name="hospital-profile.html")),
        name="app-api-hospital-profile",
    ),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
