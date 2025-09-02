import pytest
from django.urls import resolve, reverse

pytestmark = pytest.mark.django_db


def test_lead_detail(lead):
    assert (
        reverse("api:v1:lead-detail", kwargs={"pk": str(lead.lead_id)})
        == f"/api/v1/leads/{lead.lead_id}/"
    )
    assert resolve(f"/api/v1/leads/{lead.lead_id}/").view_name == "api:v1:lead-detail"


def test_lead_create():
    assert reverse("api:v1:lead-list") == "/api/v1/leads/"
    assert resolve("/api/v1/leads/").view_name == "api:v1:lead-list"
