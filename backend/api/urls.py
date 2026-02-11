from django.urls import include, path
from rest_framework.authtoken import views

from control_plane.views import manage_endpoint

app_name = "api"

urlpatterns = [
    path("v1/", include("api.v1.urls", namespace="v1")),
    path("manage", manage_endpoint, name="manage"),
    path("token-auth/", views.obtain_auth_token),
]
