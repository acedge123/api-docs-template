import pytest
from django.test import RequestFactory

from api.v1.core.permissions import IsOwner
from api.v1.scoringengine.views import QuestionViewSet

pytestmark = pytest.mark.django_db


class TestIsOwner:
    def test_has_object_permission(self, user, user1, question, rf: RequestFactory):
        permission = IsOwner()
        request = rf.get('/fake-url/')
        view = QuestionViewSet()

        # Same user in request and in object owner
        request.user = user

        assert permission.has_object_permission(request, view, question)

        # Different user in request
        request.user = user1

        assert not permission.has_object_permission(request, view, question)
