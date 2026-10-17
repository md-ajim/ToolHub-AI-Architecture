"""P0 regression: storage file inventory is private per user."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.storage.models import File

User = get_user_model()


@pytest.fixture
def owner(db):
    return User.objects.create_user(email="owner@example.com", password="password")


@pytest.fixture
def stranger(db):
    return User.objects.create_user(email="stranger@example.com", password="password")


def _make_file(user):
    return File.objects.create(
        user=user,
        filename="a.bin",
        mime_type="application/octet-stream",
        size=10,
        storage_path="/tmp/a.bin",
        status="processed",
    )


def _client(user=None):
    client = APIClient()
    if user:
        client.force_authenticate(user)
    return client


@pytest.mark.django_db
class TestFileAccessControl:
    def test_anonymous_list_denied(self):
        res = _client().get("/api/v1/storage/files/")
        assert res.status_code in (401, 403)

    def test_anonymous_delete_denied(self, owner):
        f = _make_file(owner)
        res = _client().delete(f"/api/v1/storage/files/{f.id}/")
        assert res.status_code in (401, 403)
        assert File.objects.filter(pk=f.pk).exists()

    def test_user_sees_only_own_files(self, owner, stranger):
        _make_file(owner)
        _make_file(stranger)
        res = _client(owner).get("/api/v1/storage/files/")
        assert res.status_code == 200
        assert len(res.data["data"]) == 1

    def test_cross_user_delete_is_404(self, owner, stranger):
        f = _make_file(owner)
        res = _client(stranger).delete(f"/api/v1/storage/files/{f.id}/")
        assert res.status_code == 404
        assert File.objects.filter(pk=f.pk).exists()

    def test_owner_delete_works(self, owner):
        f = _make_file(owner)
        res = _client(owner).delete(f"/api/v1/storage/files/{f.id}/")
        assert res.status_code == 200
        assert not File.objects.filter(pk=f.pk).exists()
