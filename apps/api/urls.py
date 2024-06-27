
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('apps.api.specialists.urls')),
    path('', include('apps.api.patients.urls')),
    path('', include('apps.api.accountApp.urls')),
    path('', include('apps.api.info.urls')),
    path('', include('rest_framework.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
