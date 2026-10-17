"""Storage usage endpoint: per-user bytes, deleted files excluded."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.storage.models import File

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(email="storage@example.com", password="password")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(email="other@example.com", password="password")


def _make_file(user, size, status="processed"):
    return File.objects.create(
        user=user,
        filename="f.bin",
        mime_type="application/octet-stream",
        size=size,
        storage_path="/tmp/f.bin",
        status=status,
    )


def _get(user):
    client = APIClient()
    client.force_authenticate(user)
    return client.get("/api/v1/storage/usage/")


@pytest.mark.django_db
class TestStorageUsageView:
    def test_sums_own_non_deleted_files(self, user):
        _make_file(user, 100)
        _make_file(user, 200)
        res = _get(user)
        assert res.status_code == 200
        assert res.data["success"] is True
        assert res.data["data"]["used_bytes"] == 300
        assert res.data["data"]["file_count"] == 2

    def test_deleted_files_excluded(self, user):
        _make_file(user, 100)
        _make_file(user, 500, status="deleted")
        res = _get(user)
        assert res.data["data"]["used_bytes"] == 100
        assert res.data["data"]["file_count"] == 1

    def test_other_users_files_excluded(self, user, other_user):
        _make_file(user, 100)
        _make_file(other_user, 900)
        res = _get(user)
        assert res.data["data"]["used_bytes"] == 100

    def test_empty_usage_is_zero(self, user):
        res = _get(user)
        assert res.status_code == 200
        assert res.data["data"] == {"used_bytes": 0, "file_count": 0}

    def test_requires_auth(self, db):
        client = APIClient()
        res = client.get("/api/v1/storage/usage/")
        assert res.status_code in (401, 403)
