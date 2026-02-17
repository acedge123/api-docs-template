from django.urls import include, path
from rest_framework.authtoken import views

# Lazy import to avoid startup errors if control_plane has issues
def manage_endpoint_lazy(request):
    """Lazy import of manage_endpoint to avoid startup failures"""
    from control_plane.views import manage_endpoint
    return manage_endpoint(request)

app_name = "api"

urlpatterns = [
    path("v1/", include("api.v1.urls", namespace="v1")),
    path("manage", manage_endpoint_lazy, name="manage"),
    path("token-auth/", views.obtain_auth_token),
]
