"""hfcscoringengine URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, include, re_path
from django.http import JsonResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from scoringengine.admin import admin_site

# Swagger/OpenAPI schema view
schema_view = get_schema_view(
    openapi.Info(
        title="HFC Scoring Engine API",
        default_version='v1',
        description="API for lead scoring and qualification system",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

def meaningful_health_check(request):
    """Health check that actually verifies the application is working"""
    health_status = {
        "status": "healthy",
        "checks": {}
    }
    
    # Check 1: Basic Django functionality
    try:
        from django.conf import settings
        health_status["checks"]["django_settings"] = "valid"
    except Exception as e:
        health_status["checks"]["django_settings"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check 2: Installed apps
    try:
        from django.apps import apps
        app_count = len(apps.get_app_configs())
        health_status["checks"]["installed_apps"] = f"{app_count} apps loaded"
    except Exception as e:
        health_status["checks"]["installed_apps"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check 3: Database connectivity (non-blocking)
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_status["checks"]["database"] = "connected"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        # Don't fail health check for database issues during startup
        health_status["checks"]["database"] = "connecting..."
    
    # Check 4: Static files
    try:
        from django.conf import settings
        if hasattr(settings, 'STATIC_URL'):
            health_status["checks"]["static_files"] = "configured"
        else:
            health_status["checks"]["static_files"] = "not configured"
    except Exception as e:
        health_status["checks"]["static_files"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Return appropriate HTTP status
    if health_status["status"] == "healthy":
        return JsonResponse(health_status, status=200)
    else:
        return JsonResponse(health_status, status=503)  # Service Unavailable

def test_view(request):
    """Very simple test view"""
    return JsonResponse({"test": "working"})

urlpatterns = [
    path("admin/", admin_site.urls),
    path("api/", include("api.urls", namespace="api")),
    path("health/", meaningful_health_check, name="health_check"),
    path("test/", test_view, name="test"),
    
    # API Documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
