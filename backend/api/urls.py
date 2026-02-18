from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken import views

# Lazy import to avoid startup errors if control_plane has issues
@csrf_exempt
def manage_endpoint_lazy(request):
    """Lazy import of manage_endpoint to avoid startup failures"""
    from control_plane.views import manage_endpoint
    return manage_endpoint(request)

@csrf_exempt
def onboard_leadscoring_lazy(request):
    """Lazy import of onboard_leadscoring to avoid startup failures"""
    from control_plane.onboarding_views import onboard_leadscoring
    return onboard_leadscoring(request)

@csrf_exempt
def get_usage_lazy(request):
    """Lazy import of get_usage to avoid startup failures"""
    from control_plane.usage_views import get_usage
    return get_usage(request)

app_name = "api"

urlpatterns = [
    path("v1/", include("api.v1.urls", namespace="v1")),
    path("manage", manage_endpoint_lazy, name="manage"),
    path("onboard/leadscoring", onboard_leadscoring_lazy, name="onboard-leadscoring"),
    path("usage", get_usage_lazy, name="usage"),
    path("token-auth/", views.obtain_auth_token),
]
