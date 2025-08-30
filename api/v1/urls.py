from django.conf import settings

from rest_framework.routers import DefaultRouter, SimpleRouter

from api.v1.scoringengine.views import (
    LeadViewSet, QuestionViewSet, ChoiceViewSet, ScoringModelViewSet,
    ValueRangeViewSet, DatesRangeViewSet, RecommendationViewSet,
    UserViewSet, AnalyticsViewSet
)

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

# Lead management
router.register(r"leads", LeadViewSet)

# Admin endpoints
router.register(r"questions", QuestionViewSet)
router.register(r"choices", ChoiceViewSet)
router.register(r"scoring-models", ScoringModelViewSet)
router.register(r"value-ranges", ValueRangeViewSet)
router.register(r"dates-ranges", DatesRangeViewSet)
router.register(r"recommendations", RecommendationViewSet)
router.register(r"users", UserViewSet)
router.register(r"analytics", AnalyticsViewSet, basename='analytics')

app_name = "v1"
urlpatterns = router.urls
