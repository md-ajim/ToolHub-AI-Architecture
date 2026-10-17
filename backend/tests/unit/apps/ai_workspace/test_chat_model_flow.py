"""End-to-end chat model flow tests.

These mirror the QA scenario that user-facing acceptance checks exercise:
model selection travels to the backend, is honored (no silent fallback to
mock-frontier), and chat capability restrictions hold on every surface
(conversation create, conversation patch, chat stream).

Requires DRF + pytest-django, same as the rest of the ai_workspace suite.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from apps.ai_workspace.models import AiConversation, AiWorkspaceModel

User = get_user_model()

CHAT_LIGHT = "t-light"
CHAT_FRONTIER = "t-frontier"
NON_CHAT_IMAGE = "t-image-gen"
AUTO = "auto"


@pytest.fixture(autouse=True)
def _allow_mock_models(settings):
    """Flow fixtures use mock-provider rows; opt into mock mode."""
    settings.AI_ALLOW_MOCK_MODELS = True


@pytest.fixture
def qa_user(db):
    return User.objects.create_user(
        email="qa-test@toolhub.local", password="password", is_qa_user=True
    )


@pytest.fixture
def free_user(db):
    return User.objects.create_user(
        email="free@example.com", password="password", is_qa_user=False
    )


@pytest.fixture
def registry(db):
    light = AiWorkspaceModel.objects.create(
        id=CHAT_LIGHT,
        provider="mock",
        provider_model_id="mock-light-1",
        display_name="Light",
        description="Mock light chat model",
        tier="max",
        capabilities=["chat", "files"],
        context_window=8192,
        status="active",
        sort_order=10,
    )
    frontier = AiWorkspaceModel.objects.create(
        id=CHAT_FRONTIER,
        provider="mock",
        provider_model_id="mock-frontier-1",
        display_name="Frontier",
        description="Mock frontier chat model",
        tier="max",
        capabilities=["chat", "reasoning"],
        context_window=128000,
        status="active",
        sort_order=30,
    )
    image = AiWorkspaceModel.objects.create(
        id=NON_CHAT_IMAGE,
        provider="mock",
        provider_model_id="mock-img-1",
        display_name="Image Gen",
        description="Text-to-image model",
        tier="max",
        capabilities=["image_generation"],
        context_window=0,
        status="active",
        sort_order=40,
    )
    return {"light": light, "frontier": frontier, "image": image}


def _client(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


def _models_url():
    from django.urls import reverse

    return reverse("ai-workspace-models")


def _conversations_url():
    from django.urls import reverse

    return reverse("ai-workspace-conversations")


def _conversation_url(conversation_id):
    from django.urls import reverse

    return reverse("ai-workspace-conversation-detail", args=[conversation_id])


def _compare_url():
    from django.urls import reverse

    return reverse("ai-workspace-compare")


def _chat_url(conversation_id):
    from django.urls import reverse

    return reverse("ai-workspace-chat-stream", args=[conversation_id])


def _sse_text(response) -> str:
    if response.streaming:
        return b"".join(response.streaming_content).decode()
    text = getattr(response, "content", None)
    return text.decode() if isinstance(text, bytes) else (text or "")


class TestModelListSupportsChat:
    def test_models_expose_only_configured_chat_models(self, qa_user, registry):
        resp = _client(qa_user).get(_models_url())
        assert resp.status_code == status.HTTP_200_OK
        payload = resp.json()
        models = {m["id"]: m for m in payload["data"]}
        assert CHAT_LIGHT in models and CHAT_FRONTIER in models
        assert NON_CHAT_IMAGE not in models
        assert models[CHAT_LIGHT]["supports_chat"] is True
        assert models[CHAT_FRONTIER]["supports_chat"] is True


class TestCompareModelValidation:
    def test_compare_rejects_non_chat_model(self, qa_user, registry):
        response = _client(qa_user).post(
            _compare_url(),
            {"prompt": "hello", "model_ids": [NON_CHAT_IMAGE]},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "does not support chat" in response.json()["error"]["message"]

    def test_compare_rejects_unknown_model(self, qa_user, registry):
        response = _client(qa_user).post(
            _compare_url(),
            {"prompt": "hello", "model_ids": ["missing"]},
            format="json",
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestConversationModelValidation:
    def test_create_rejects_non_chat_model(self, qa_user, registry):
        resp = _client(qa_user).post(
            _conversations_url(), {"model": NON_CHAT_IMAGE}, format="json"
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "does not support chat" in _sse_text(resp)

    def test_create_accepts_chat_model(self, qa_user, registry):
        resp = _client(qa_user).post(
            _conversations_url(), {"model": CHAT_LIGHT}, format="json"
        )
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.json()["data"]["model"] == CHAT_LIGHT

    def test_create_rejects_unknown_model(self, qa_user):
        resp = _client(qa_user).post(
            _conversations_url(), {"model": "does-not-exist"}, format="json"
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_patch_rejects_non_chat_model(self, qa_user, registry):
        client = _client(qa_user)
        conv = AiConversation.objects.create(user=qa_user)
        resp = client.patch(
            _conversation_url(conv.id), {"model": NON_CHAT_IMAGE}, format="json"
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "does not support chat" in _sse_text(resp)

    def test_patch_switches_to_chat_model(self, qa_user, registry):
        client = _client(qa_user)
        conv = AiConversation.objects.create(user=qa_user, model=registry["frontier"])
        resp = client.patch(
            _conversation_url(conv.id), {"model": CHAT_LIGHT}, format="json"
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["data"]["model"] == CHAT_LIGHT

    def test_patch_resets_to_auto(self, qa_user, registry):
        client = _client(qa_user)
        conv = AiConversation.objects.create(user=qa_user, model=registry["frontier"])
        resp = client.patch(_conversation_url(conv.id), {"model": AUTO}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["data"]["model"] is None


class TestChatStreamModelSelection:
    def _create_and_stream(self, client, model, content):
        conv = AiConversation.objects.create(user=client.handler._force_user, model=model)
        return (
            conv,
            client.post(
                _chat_url(conv.id),
                {
                    "content": content,
                    "client_message_id": f"test-{conv.id}",
                },
                format="json",
            ),
        )

    def test_explicit_light_model_is_honored(self, qa_user, registry):
        client = _client(qa_user)
        conv, resp = self._create_and_stream(client, registry["light"], "MODEL_TEST_LIGHT")
        assert resp.status_code == status.HTTP_200_OK, _sse_text(resp)
        body = _sse_text(resp)
        # The selected mock model is used, not a silent fallback to frontier.
        assert "[mock:mock-light-1]" in body
        assert "[mock:mock-frontier-1]" not in body
        conv.refresh_from_db()
        assert conv.model.id == CHAT_LIGHT

    def test_explicit_frontier_model_is_honored(self, qa_user, registry):
        client = _client(qa_user)
        conv, resp = self._create_and_stream(client, registry["frontier"], "MODEL_TEST_FRONTIER")
        assert resp.status_code == status.HTTP_200_OK, _sse_text(resp)
        body = _sse_text(resp)
        assert "[mock:mock-frontier-1]" in body
        assert "[mock:mock-light-1]" not in body
        conv.refresh_from_db()
        assert conv.model.id == CHAT_FRONTIER

    def test_non_chat_model_rejected_by_stream(self, qa_user, registry):
        client = _client(qa_user)
        conv, resp = self._create_and_stream(client, registry["image"], "draw a cat")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "does not support chat" in _sse_text(resp)

    def test_free_user_blocked_from_max_tier_model(self, free_user, registry):
        """Normal (non-QA) users must keep their entitlement restrictions."""
        client = _client(free_user)
        conv = AiConversation.objects.create(
            user=free_user, model=registry["frontier"]
        )
        resp = client.post(
            _chat_url(conv.id),
            {"content": "hello", "client_message_id": "free-1"},
            format="json",
        )
        assert resp.status_code in (
            status.HTTP_403_FORBIDDEN,
            status.HTTP_402_PAYMENT_REQUIRED,
        )
        body = _sse_text(resp)
        assert "model_access_denied" in body or "access" in body.lower()