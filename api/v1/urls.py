from django.conf import settings

from rest_framework.routers import DefaultRouter, SimpleRouter

from api.v1.scoringengine.views import LeadViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register(r"leads", LeadViewSet)

app_name = "v1"
urlpatterns = router.urls
