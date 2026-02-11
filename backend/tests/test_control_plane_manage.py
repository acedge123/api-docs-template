import json

import pytest
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token


@pytest.mark.api
@pytest.mark.views
class TestControlPlaneManage:
    def test_meta_actions_ok(self, client, db):
        user = get_user_model().objects.create_user(username="acp_test", password="pw")
        token = Token.objects.get(user=user)

        resp = client.post(
            "/api/manage",
            data=json.dumps({"action": "meta.actions"}),
            content_type="application/json",
            **{"HTTP_X_API_KEY": token.key},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        assert body["request_id"]
        assert "data" in body
        assert "actions" in body["data"]

    def test_invalid_json(self, client, db):
        user = get_user_model().objects.create_user(username="acp_test2", password="pw")
        token = Token.objects.get(user=user)

        resp = client.post(
            "/api/manage",
            data="{not json}",
            content_type="application/json",
            **{"HTTP_X_API_KEY": token.key},
        )
        assert resp.status_code == 400
        body = resp.json()
        assert body["ok"] is False
        assert body["code"] == "VALIDATION_ERROR"

    def test_missing_api_key(self, client):
        resp = client.post(
            "/api/manage",
            data=json.dumps({"action": "meta.actions"}),
            content_type="application/json",
        )
        assert resp.status_code == 401
        body = resp.json()
        assert body["ok"] is False
        assert body["code"] == "INVALID_API_KEY"
