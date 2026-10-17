"""Production gate: mock models are never listed, routed, or executable
unless AI_ALLOW_MOCK_MODELS is explicitly enabled (default off).

Unlike the routing/flow suites (which opt into mock mode via an autouse
fixture to exercise logic with mock-provider rows), these tests assert the
production posture: deterministic fake models stay invisible and
unrunnable out of the box.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.ai_workspace import gateway, routing
from apps.ai_workspace.models import AiConversation, AiWorkspaceModel

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(email="gate@example.com", password="password")


@pytest.fixture
def mock_chat(db):
    return AiWorkspaceModel.objects.create(
        id="g-mock",
        provider="mock",
        provider_model_id="mock-g1",
        display_name="Gate Mock",
        tier="free",
        capabilities=["chat"],
        context_window=8192,
        status="active",
        sort_order=1,
    )


def _client(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


def _models_url():
    from django.urls import reverse

    return reverse("ai-workspace-models")


@pytest.mark.django_db
class TestMockGateOff:
    def test_eligible_models_excludes_mock_by_default(self, user, mock_chat):
        assert mock_chat.id not in {m.id for m in routing._eligible_models(user)}

    def test_eligible_mock_helper_returns_none_by_default(self, user, mock_chat):
        assert routing.eligible_mock_chat_model(user) is None

    def test_model_list_view_excludes_mock_by_default(self, user, mock_chat):
        res = _client(user).get(_models_url())
        assert res.status_code == 200
        ids = [m["id"] for m in res.data["data"]]
        assert "g-mock" not in ids

    def test_explicit_mock_execution_rejected_by_default(self, user, mock_chat):
        conv = AiConversation.objects.create(user=user, model=None)
        with pytest.raises(gateway.GatewayError) as exc:
            list(gateway.stream_reply(user, conv, mock_chat, "hi", "gate-1"))
        assert exc.value.code == "model_not_found"


@pytest.mark.django_db
class TestMockGateOn:
    def test_eligible_models_includes_mock_when_enabled(self, user, mock_chat, settings):
        settings.AI_ALLOW_MOCK_MODELS = True
        assert mock_chat.id in {m.id for m in routing._eligible_models(user)}

    def test_model_list_view_includes_mock_when_enabled(self, user, mock_chat, settings):
        settings.AI_ALLOW_MOCK_MODELS = True
        res = _client(user).get(_models_url())
        assert res.status_code == 200
        ids = [m["id"] for m in res.data["data"]]
        assert "g-mock" in ids

    def test_real_models_unaffected_by_gate(self, user):
        from unittest import mock as umock

        real = AiWorkspaceModel.objects.create(
            id="g-real",
            provider="openai_compatible",
            provider_model_id="gpt-g1",
            display_name="Gate Real",
            tier="free",
            capabilities=["chat"],
            context_window=8192,
            status="active",
            sort_order=1,
        )

        class _Configured:
            def is_configured(self):
                return True

        with umock.patch(
            "apps.ai_workspace.providers.get_adapter", return_value=_Configured()
        ), umock.patch(
            "apps.ai_workspace.views.get_adapter", return_value=_Configured()
        ):
            assert real.id in {m.id for m in routing._eligible_models(user)}
            res = _client(user).get(_models_url())
            assert res.status_code == 200
            assert "g-real" in [m["id"] for m in res.data["data"]]
