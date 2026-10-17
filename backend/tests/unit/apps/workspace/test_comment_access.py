"""P0 regression: project comments are scoped to the owning user."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.workspace.models import Comment, Project

User = get_user_model()


@pytest.fixture
def owner(db):
    return User.objects.create_user(email="c-owner@example.com", password="password")


@pytest.fixture
def stranger(db):
    return User.objects.create_user(email="c-stranger@example.com", password="password")


@pytest.fixture
def project(owner):
    return Project.objects.create(user=owner, name="P")


@pytest.fixture
def comment(owner, project):
    return Comment.objects.create(project=project, user=owner, text="hi")


def _client(user=None):
    client = APIClient()
    if user:
        client.force_authenticate(user)
    return client


def _url(project_id, suffix=""):
    return f"/api/v1/workspace/projects/{project_id}/comments/{suffix}"


@pytest.mark.django_db
class TestCommentAccessControl:
    def test_owner_lists_own_comments(self, owner, project, comment):
        res = _client(owner).get(_url(project.id))
        assert res.status_code == 200

    def test_stranger_list_is_404(self, stranger, project):
        res = _client(stranger).get(_url(project.id))
        assert res.status_code == 404

    def test_stranger_post_is_404(self, stranger, project):
        res = _client(stranger).post(_url(project.id), {"text": "x"}, format="json")
        assert res.status_code == 404
        assert Comment.objects.filter(text="x").count() == 0

    def test_stranger_resolve_is_404(self, stranger, project, comment):
        res = _client(stranger).post(_url(project.id, f"{comment.id}/resolve/"))
        assert res.status_code == 404
        comment.refresh_from_db()
        assert comment.is_resolved is False

    def test_owner_resolve_works(self, owner, project, comment):
        res = _client(owner).post(_url(project.id, f"{comment.id}/resolve/"))
        assert res.status_code == 200
        comment.refresh_from_db()
        assert comment.is_resolved is True
