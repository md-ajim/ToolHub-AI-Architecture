"""Chat model output outage guard: a model that produces no valid output is
disabled for all users until it recovers. Config/registry untouched.
"""
import pytest
from django.contrib.auth import get_user_model

from apps.ai_workspace import provider_registry
from apps.ai_workspace.models import AiWorkspaceModel
from apps.ai_workspace.providers.base import ProviderError

User = get_user_model()


pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _locmem_cache(settings):
    settings.CACHES = {
        "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
    }
    yield
    from django.core.cache import cache

    cache.clear()


@pytest.fixture
def user(db):
    return User.objects.create_user(email="chat-guard@example.com", password="password")


def _make_model(**overrides):
    data = {
        "id": "chat-guard-model",
        "provider": "openai_compatible",
        "provider_model_id": "prov-1",
        "display_name": "Guard Model",
        "tier": "free",
        "capabilities": ["chat"],
        "context_window": 8192,
        "status": "active",
        "sort_order": 1,
    }
    data.update(overrides)
    return AiWorkspaceModel.objects.create(**data)


class TestOutageClassification:
    def test_output_failures_tracked(self):
        for code in (
            "provider_error",
            "provider_unavailable",
            "provider_billing_required",
            "provider_license_required",
            "rate_limited",
            "timeout",
            "empty_response",
        ):
            assert provider_registry.should_track_model_outage(ProviderError(code, "x")) is True, code

    def test_input_and_app_errors_never_tracked(self):
        for code in ("invalid_request", "model_not_found", "model_access_denied", "cancelled"):
            assert provider_registry.should_track_model_outage(ProviderError(code, "x")) is False, code

    def test_secret_details_never_cached(self):
        provider_registry.record_model_outage(
            "m-secret", "openai_compatible", ProviderError("provider_error", "sk-secret quota xyz")
        )
        state = provider_registry.get_model_outage("m-secret", "openai_compatible")
        assert state is not None
        assert "sk-secret" not in str(state)
        assert "sk-secret" not in state["reason"]


class TestGlobalDisableAndRecovery:
    def test_serializer_disables_outage_model(self, user, monkeypatch):
        from apps.ai_workspace.serializers import ModelSerializer

        model = _make_model(id="m-out-1", provider="openai_compat_out1")

        class _Configured:
            def is_configured(self):
                return True

        monkeypatch.setattr(
            "apps.ai_workspace.providers.get_adapter", lambda provider: _Configured()
        )
        monkeypatch.setattr(
            "apps.ai_workspace.serializers.get_adapter", lambda provider: _Configured(),
            raising=False,
        )
        assert ModelSerializer(model).data["available"] is True

        provider_registry.record_model_outage(
            model.id, model.provider, ProviderError("provider_error", "gone upstream")
        )
        data = ModelSerializer(model).data
        assert data["available"] is False
        assert "not available from provider" in data["unavailability_reason"].lower()
        # Row stays listed (never removed).
        assert data["id"] == model.id

    def test_success_clears_outage(self, monkeypatch):
        from apps.ai_workspace.serializers import ModelSerializer

        model = _make_model(id="m-out-2", provider="openai_compat_out2")

        class _Configured:
            def is_configured(self):
                return True

        monkeypatch.setattr(
            "apps.ai_workspace.providers.get_adapter", lambda provider: _Configured()
        )
        provider_registry.record_model_outage(
            model.id, model.provider, ProviderError("empty_response", "no text")
        )
        assert provider_registry.is_model_in_outage(model.id, model.provider) is True
        provider_registry.note_model_call_result(model.id, model.provider, None)
        assert provider_registry.is_model_in_outage(model.id, model.provider) is False

    def test_gateway_note_helper_tracks_generic_provider_error(self):
        from apps.ai_workspace.gateway import note_provider_call_result

        note_provider_call_result("openai_compatible", ProviderError("provider_error", "gone"), "m-note-1")
        assert provider_registry.is_model_in_outage("m-note-1", "openai_compatible") is True
        note_provider_call_result("openai_compatible", None, "m-note-1")
        assert provider_registry.is_model_in_outage("m-note-1", "openai_compatible") is False

    def test_gateway_rejects_outage_model_fast(self, user, monkeypatch):
        from apps.ai_workspace import gateway
        from apps.ai_workspace.models import AiConversation

        class _Configured:
            def is_configured(self):
                return True

        monkeypatch.setattr(gateway, "get_adapter", lambda provider: _Configured())
        model = _make_model(id="m-out-3", provider="openai_compat_out3")
        provider_registry.record_model_outage(
            model.id, model.provider, ProviderError("provider_error", "gone")
        )
        conv = AiConversation.objects.create(user=user, model=model)
        with pytest.raises(gateway.GatewayError) as exc_info:
            list(gateway.stream_reply(user, conv, model, "Hello"))
        assert exc_info.value.code == "model_not_found"

    def test_registry_rows_untouched(self):
        model = _make_model(id="m-out-4", provider="openai_compat_out4")
        provider_registry.record_model_outage(
            model.id, model.provider, ProviderError("provider_error", "gone")
        )
        assert AiWorkspaceModel.objects.filter(id="m-out-4").exists()
