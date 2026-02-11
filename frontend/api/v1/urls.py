from django.conf import settings

from rest_framework.routers import DefaultRouter, SimpleRouter

from api.v1.scoringengine.views import (
    LeadViewSet,
    QuestionViewSet,
    ChoiceViewSet,
    ScoringModelViewSet,
    ValueRangeViewSet,
    DatesRangeViewSet,
    RecommendationViewSet,
    UserViewSet,
    AnalyticsViewSet,
)

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

# Lead management
router.register(r"leads", LeadViewSet, basename="leads")

# Admin endpoints
router.register(r"questions", QuestionViewSet, basename="questions")
router.register(r"choices", ChoiceViewSet, basename="choices")
router.register(r"scoring-models", ScoringModelViewSet, basename="scoring-models")
router.register(r"value-ranges", ValueRangeViewSet, basename="value-ranges")
router.register(r"dates-ranges", DatesRangeViewSet, basename="dates-ranges")
router.register(r"recommendations", RecommendationViewSet, basename="recommendations")
router.register(r"users", UserViewSet, basename="users")
router.register(r"analytics", AnalyticsViewSet, basename="analytics")

app_name = "v1"
urlpatterns = router.urls
