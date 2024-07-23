"""
URL configuration for web_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from mpesa.urls import mpesa_urls
from django.conf import settings
from django.conf.urls.static import static

from web_project.views import SystemView

from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include("apps.dashboards.urls")),
    path("", include("apps.api.urls")),

    # Calendar urls
    path("", include("apps.my_calendar.urls")),

    # kanban urls
    # path("", include("apps.kanban.urls")),

    # User urls
    path("", include("apps.users.urls")),

    # Access urls
    path("", include("apps.access.urls")),

    # Pages urls
    path("", include("apps.pages.urls")),

    # Auth urls
    path("", include("apps.authentication.urls")),


    # auth urls
    path("", include("auth.urls")),

    # transaction urls
    path("", include("apps.transactions.urls")),
    path("dashboard/", include("apps.asset_manager.urls")),
    # path('accounts/', include('django_ledger.urls', namespace='django_ledger')),
    # path('appointment/', include('appointment.urls')),
    path('oauth/v1/',include('apps._api_app.urls')),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = SystemView.as_view(template_name="pages_misc_error.html", status=404)
handler403 = SystemView.as_view(template_name="pages_misc_not_authorized.html", status=403)
handler400 = SystemView.as_view(template_name="pages_misc_error.html", status=400)
handler500 = SystemView.as_view(template_name="pages_misc_error.html", status=500)
