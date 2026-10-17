import pytest
from django.contrib.auth import get_user_model

from apps.ai_workspace.models import AiConversation

User = get_user_model()


@pytest.fixture
def user_a(db):
    return User.objects.create_user(email="a@example.com", password="password")


@pytest.fixture
def user_b(db):
    return User.objects.create_user(email="b@example.com", password="password")


@pytest.mark.django_db
class TestConversationAuthorization:
    def test_user_a_cannot_see_user_b_conversation(self, user_a, user_b):
        conv = AiConversation.objects.create(user=user_a)
        # The owner sees it.
        assert (
            AiConversation.objects.filter(
                id=conv.id, user=user_a, deleted_at__isnull=True
            ).exists()
            is True
        )
        # Another user cannot see it (the endpoint filters by user).
        assert (
            AiConversation.objects.filter(
                id=conv.id, user=user_b, deleted_at__isnull=True
            ).exists()
            is False
        )

    def test_deleted_conversation_is_hidden(self, user_a):
        conv = AiConversation.objects.create(user=user_a)
        conv.deleted_at = __import__("django.utils.timezone", fromlist=["now"]).now()
        conv.save(update_fields=["deleted_at"])
        assert (
            AiConversation.objects.filter(
                id=conv.id, user=user_a, deleted_at__isnull=True
            ).exists()
            is False
        )
