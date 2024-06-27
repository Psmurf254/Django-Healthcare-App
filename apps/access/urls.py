from django.urls import path
from .views import AccessView, AccessUpdateView, AccessDeleteView, UserUpdateStatus
from django.contrib.auth.decorators import login_required




urlpatterns = [

    path(
        "app/access/roles/",
        login_required(AccessView.as_view(template_name="app_access_roles.html")),
        name="app-access-roles",
    ),

    path(
    "app/access/roles/update/<str:role_id>/",
    login_required(AccessUpdateView.as_view(template_name="app_access_roles_update.html")),
    name="app-access-roles_update",
    ),
    path(
        "app/access/user/update/<str:user_id>/",
        login_required(UserUpdateStatus.as_view(template_name="app_access_roles_update.html")),
        name="app-access-user_update",
    ),

 path(
    "app/access/roles/delete/<str:role_id>/",
    login_required(AccessDeleteView.as_view(template_name="app_access_roles_update.html")),
    name="app-access-roles_delete",
),

    path(
        "app/access/permission/",
        login_required(AccessView.as_view(template_name="app_access_permission.html")),
        name="app-access-permission",
    ),
]
