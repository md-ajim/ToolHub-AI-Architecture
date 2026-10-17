"""Contact message endpoint: real persistence, validation, throttling."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.notifications.models import ContactMessage

User = get_user_model()

VALID = {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "subject": "Billing question",
    "message": "Please explain how credit rollover works for my plan.",
}


def _anon_post(payload, ip="10.8.8.8"):
    # Unique source IP per test: throttle buckets are per-IP and shared
    # across tests (and runs) in one process/cache.
    return APIClient().post(
        "/api/v1/contact/messages/", payload, format="json", REMOTE_ADDR=ip
    )


@pytest.mark.django_db
class TestContactMessageView:
    def test_valid_message_stored_anonymous(self):
        res = _anon_post(dict(VALID), ip="10.8.8.1")
        assert res.status_code == 201, res.content[:300]
        assert res.data["success"] is True
        row = ContactMessage.objects.get(email="jane@example.com")
        assert row.subject == "Billing question"
        assert row.user is None
        assert row.is_read is False

    def test_authenticated_user_attached(self, db):
        user = User.objects.create_user(email="c@example.com", password="x")
        client = APIClient()
        client.force_authenticate(user)
        res = client.post("/api/v1/contact/messages/", VALID, format="json")
        assert res.status_code == 201
        row = ContactMessage.objects.get(email="jane@example.com")
        assert row.user_id == user.id

    def test_validation_rejects_short_message(self):
        bad = dict(VALID, message="hi")
        res = _anon_post(bad, ip="10.8.8.2")
        assert res.status_code == 400
        assert ContactMessage.objects.count() == 0

    def test_validation_rejects_bad_email(self):
        bad = dict(VALID, email="not-an-email")
        res = _anon_post(bad, ip="10.8.8.3")
        assert res.status_code == 400
        assert ContactMessage.objects.count() == 0

    def test_throttle_trips_after_burst(self):
        import random

        # Random source IP per run: throttle buckets persist in cache
        # across runs, so a fixed IP would inherit other runs' hits.
        ip = f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
        statuses = []
        for i in range(11):
            payload = dict(VALID, email=f"spam{i}@example.com")
            res = _anon_post(payload, ip=ip)
            statuses.append(res.status_code)
        assert statuses[-1] == 429
        assert all(s == 201 for s in statuses[:-1])
