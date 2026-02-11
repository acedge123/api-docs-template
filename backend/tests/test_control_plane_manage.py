import json

import pytest


@pytest.mark.api
@pytest.mark.views
class TestControlPlaneManage:
    def test_meta_actions_ok(self, client):
        resp = client.post(
            "/api/manage",
            data=json.dumps({"action": "meta.actions"}),
            content_type="application/json",
            **{"HTTP_X_API_KEY": "test-key-123"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        assert body["request_id"]
        assert "data" in body
        assert "actions" in body["data"]

    def test_invalid_json(self, client):
        resp = client.post(
            "/api/manage",
            data="{not json}",
            content_type="application/json",
            **{"HTTP_X_API_KEY": "test-key-123"},
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
