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
from django.urls import path, include
from django.http import JsonResponse

from scoringengine.admin import admin_site

def meaningful_health_check(request):
    """Simple health check that always returns 200 OK"""
    return JsonResponse({"status": "ok", "message": "Django is running"}, status=200)

def test_view(request):
    """Very simple test view"""
    return JsonResponse({"test": "working"})

urlpatterns = [
    path("admin/", admin_site.urls),
    path("api/", include("api.urls", namespace="api")),
    path("health/", meaningful_health_check, name="health_check"),
    path("test/", test_view, name="test"),
]
