from django.urls import include, path
from rest_framework.authtoken import views

app_name = "api"

urlpatterns = [
    path("v1/", include("api.v1.urls", namespace="v1")),
    path("token-auth/", views.obtain_auth_token),
]
