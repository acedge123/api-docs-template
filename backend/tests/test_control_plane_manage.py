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

    def test_questions_upsert_and_list_and_lead_dry_run(self, client, db):
        user = get_user_model().objects.create_user(username="acp_test3", password="pw")
        token = Token.objects.get(user=user)

        upsert = client.post(
            "/api/manage",
            data=json.dumps(
                {
                    "action": "domain.leadscoring.questions.upsert_bulk",
                    "params": {
                        "questions": [
                            {
                                "number": 1,
                                "text": "What is your goal?",
                                "field_name": "goal",
                                "type": "CH",
                                "choices": [
                                    {"text": "Buy", "slug": "buy", "value": 1},
                                    {"text": "Refinance", "slug": "refi", "value": 0},
                                ],
                            }
                        ]
                    },
                }
            ),
            content_type="application/json",
            **{"HTTP_X_API_KEY": token.key},
        )
        assert upsert.status_code == 200
        upsert_body = upsert.json()
        assert upsert_body["ok"] is True
        assert upsert_body["data"]["questions"]["created"] == 1

        listed = client.post(
            "/api/manage",
            data=json.dumps({"action": "domain.leadscoring.questions.list"}),
            content_type="application/json",
            **{"HTTP_X_API_KEY": token.key},
        )
        assert listed.status_code == 200
        listed_body = listed.json()
        assert listed_body["ok"] is True
        assert len(listed_body["data"]) == 1
        assert listed_body["data"][0]["field_name"] == "goal"
        assert len(listed_body["data"][0]["choices"]) == 2

        # Lead create dry_run should score without writing
        lead_preview = client.post(
            "/api/manage",
            data=json.dumps(
                {
                    "action": "domain.leadscoring.leads.create",
                    "dry_run": True,
                    "params": {"answers": [{"field_name": "goal", "response": "Buy"}]},
                }
            ),
            content_type="application/json",
            **{"HTTP_X_API_KEY": token.key},
        )
        assert lead_preview.status_code == 200
        lead_body = lead_preview.json()
        assert lead_body["ok"] is True
        assert lead_body["data"]["preview"] is True
