"""Provider payment-state honesty: billing-demanding models are flagged,
never offered as runnable, and flip back automatically once funded.

Covers: billing-failure normalization, payment-state memory, serializer
flags, listing integration, gateway record/clear, and end-to-end billing
error surfacing. Cache is overridden to locmem so no Redis is required.
"""
import pytest
from django.contrib.auth import get_user_model

from apps.ai_workspace import provider_registry, routing
from apps.ai_workspace.models import AiConversation, AiWorkspaceModel
from apps.ai_workspace.providers.base import (
    BILLING_REQUIRED_CODE,
    LICENSE_REQUIRED_CODE,
    ProviderError,
    is_billing_failure,
    is_license_failure,
)

User = get_user_model()


@pytest.fixture(autouse=True)
def _locmem_cache(settings):
    settings.CACHES = {
        "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
    }


@pytest.fixture
def user(db):
    return User.objects.create_user(email="pay@example.com", password="password")


@pytest.fixture
def qa_user(db):
    return User.objects.create_user(
        email="pay-qa@example.com", password="password", is_qa_user=True
    )


def _make_model(**overrides):
    data = {
        "id": "p-model",
        "provider": "openai_compatible",
        "provider_model_id": "prov-1",
        "display_name": "Pay Model",
        "tier": "free",
        "capabilities": ["chat"],
        "context_window": 8192,
        "status": "active",
        "sort_order": 1,
    }
    data.update(overrides)
    return AiWorkspaceModel.objects.create(**data)


class TestBillingFailureDetection:
    def test_http_402_is_billing(self):
        assert is_billing_failure(402, "Payment Required") is True

    def test_insufficient_quota_text_is_billing(self):
        assert is_billing_failure(400, "insufficient_quota: out of credits") is True

    def test_plain_rate_limit_is_not_billing(self):
        assert is_billing_failure(429, "Too Many Requests") is False

    def test_auth_failure_is_not_billing(self):
        assert is_billing_failure(401, "Invalid token") is False

    def test_server_error_is_not_billing(self):
        assert is_billing_failure(500, "Internal error") is False

    def test_empty_inputs_are_not_billing(self):
        assert is_billing_failure(None, None) is False


class TestLicenseFailureDetection:
    def test_model_agreement_is_license(self):
        assert (
            is_license_failure(
                "AIError: Model Agreement: Prior to using this model, "
                "you must submit the prompt 'agree'."
            )
            is True
        )

    def test_plain_errors_are_not_license(self):
        assert is_license_failure("Too Many Requests") is False
        assert is_license_failure("Invalid token") is False
        assert is_license_failure(None) is False

    def test_cloudflare_403_maps_to_license_without_raw_json(self):
        from apps.ai_workspace.providers.openai_compatible import OpenAIBaseAdapter

        class Dummy403:
            status_code = 403
            text = (
                '{"errors":[{"message":"AIError: Model Agreement: Prior to '
                'using this model, you must submit the prompt \'agree\'. '
                'By submitting \'agree\', you hereby agree to the '
                'llama-3.2-11b-vision-instruct Community License."}]}'
            )

            def close(self):
                pass

        err = OpenAIBaseAdapter._http_error(Dummy403())
        assert err.code == LICENSE_REQUIRED_CODE
        assert "license" in err.message.lower()
        assert "{" not in err.message and "}" not in err.message

    def test_generic_403_stays_provider_error(self):
        from apps.ai_workspace.providers.openai_compatible import OpenAIBaseAdapter

        class Dummy403:
            status_code = 403
            text = '{"error": "forbidden"}'

            def close(self):
                pass

        err = OpenAIBaseAdapter._http_error(Dummy403())
        assert err.code == "provider_error"

    def test_google_402_maps_to_billing(self, settings, monkeypatch):
        from apps.ai_workspace.providers.google import GoogleAdapter
        from apps.ai_workspace.providers.base import ChatRequest

        settings.GOOGLE_AI_API_KEY = "dummy-key"

        class Dummy402:
            status_code = 402
            text = '{"error": {"message": "Insufficient credits"}}'

            def close(self):
                pass

        monkeypatch.setattr(
            "requests.post", lambda *args, **kwargs: Dummy402()
        )
        request = ChatRequest(messages=[{"role": "user", "content": "hi"}], model="m")
        with pytest.raises(ProviderError) as exc_info:
            list(GoogleAdapter().stream_chat(request))
        assert exc_info.value.code == BILLING_REQUIRED_CODE


class TestOpenAICompatibleMapping:
    def test_402_maps_to_billing_code(self):
        from apps.ai_workspace.providers.openai_compatible import OpenAIBaseAdapter

        class Dummy402:
            status_code = 402
            text = '{"error": {"message": "Insufficient credits. Add funds."}}'

            def close(self):
                pass

        err = OpenAIBaseAdapter._http_error(Dummy402())
        assert err.code == BILLING_REQUIRED_CODE
        assert "billing" in err.message.lower()

    def test_plain_429_stays_rate_limited(self):
        from apps.ai_workspace.providers.openai_compatible import OpenAIBaseAdapter

        class Dummy429:
            status_code = 429
            text = '{"error": {"message": "Too Many Requests"}}'

            def close(self):
                pass

        err = OpenAIBaseAdapter._http_error(Dummy429())
        assert err.code == "rate_limited"


class TestPaymentStateMemory:
    def test_unknown_provider_has_no_state(self):
        assert provider_registry.get_provider_payment_state("nope") is None

    def test_record_and_read_billing(self):
        provider_registry.record_provider_payment_issue("openai_mem", "billing")
        state = provider_registry.get_provider_payment_state("openai_mem")
        assert state is not None and state["category"] == "billing"

    def test_invalid_category_ignored(self):
        provider_registry.record_provider_payment_issue("openai_invalid", "nope")
        assert provider_registry.get_provider_payment_state("openai_invalid") is None

    def test_clear_forgets_state(self):
        provider_registry.record_provider_payment_issue("openai_clear", "billing")
        provider_registry.clear_provider_payment_state("openai_clear")
        assert provider_registry.get_provider_payment_state("openai_clear") is None

    def test_license_category_recorded(self):
        provider_registry.record_provider_payment_issue("cf_lic", "license")
        state = provider_registry.get_provider_payment_state("cf_lic")
        assert state is not None and state["category"] == "license"


class TestSerializerFlags:
    def test_flagged_model_unavailable_with_reason(self, user):
        from apps.ai_workspace.serializers import ModelSerializer

        model = _make_model(provider="openai_compat_flagged")
        provider_registry.record_provider_payment_issue(
            model.provider, "billing"
        )
        data = ModelSerializer(model).data
        assert data["available"] is False
        assert "payment" in data["unavailability_reason"].lower()

    def test_clean_model_available_when_configured(self, user, monkeypatch):
        from apps.ai_workspace.serializers import ModelSerializer

        model = _make_model(provider="openai_compat_clean")

        class _Configured:
            def is_configured(self):
                return True

        monkeypatch.setattr(
            "apps.ai_workspace.providers.get_adapter",
            lambda provider: _Configured(),
        )
        data = ModelSerializer(model).data
        assert data["available"] is True
        assert data["unavailability_reason"] == ""

    def test_note_helper_records_and_clears(self):
        from apps.ai_workspace.gateway import note_provider_call_result

        note_provider_call_result(
            "openai", ProviderError(BILLING_REQUIRED_CODE, "pay up")
        )
        state = provider_registry.get_provider_payment_state("openai")
        assert state is not None and state["category"] == "billing"

        note_provider_call_result(
            "openai", ProviderError("provider_error", "boom")
        )
        assert provider_registry.get_provider_payment_state("openai") is not None

        note_provider_call_result("openai", None)
        assert provider_registry.get_provider_payment_state("openai") is None

    def test_note_helper_maps_license_code(self):
        from apps.ai_workspace.gateway import note_provider_call_result

        note_provider_call_result(
            "cf_note", ProviderError(LICENSE_REQUIRED_CODE, "agree first")
        )
        state = provider_registry.get_provider_payment_state("cf_note")
        assert state is not None and state["category"] == "license"

    def test_serializer_license_reason(self, user):
        from apps.ai_workspace.serializers import ModelSerializer

        model = _make_model(provider="openai_compat_lic")
        provider_registry.record_provider_payment_issue(
            model.provider, "license"
        )
        data = ModelSerializer(model).data
        assert data["available"] is False
        assert "license" in data["unavailability_reason"].lower()


@pytest.mark.django_db
class TestListingIntegration:
    def _list_ids(self, user):
        from rest_framework.test import APIClient

        client = APIClient()
        client.force_authenticate(user)
        from django.urls import reverse

        res = client.get(reverse("ai-workspace-models"))
        assert res.status_code == 200
        return {m["id"]: m for m in res.data["data"]}

    def test_flagged_model_listed_but_disabled(self, user, monkeypatch):
        model = _make_model(provider="openai_compat_listed")

        class _Configured:
            def is_configured(self):
                return True

        monkeypatch.setattr(
            "apps.ai_workspace.views.get_adapter",
            lambda provider: _Configured(),
        )
        monkeypatch.setattr(
            "apps.ai_workspace.providers.get_adapter",
            lambda provider: _Configured(),
        )
        # Visible and runnable before any billing failure.
        before = self._list_ids(user)
        assert before[model.id]["available"] is True

        # After a billing failure it stays visible but disabled with reason.
        provider_registry.record_provider_payment_issue(
            model.provider, "billing"
        )
        after = self._list_ids(user)
        assert after[model.id]["available"] is False
        assert "payment" in after[model.id]["unavailability_reason"].lower()


@pytest.mark.django_db
class TestGatewayBillingSurfacing:
    def test_explicit_billing_failure_records_state_and_surfaces(self, qa_user):
        from unittest import mock as umock

        from apps.ai_workspace import gateway
        from apps.ai_workspace.providers.base import ChatChunk

        model = _make_model(provider="openai_compat_gw_fail")

        class _BillingAdapter:
            name = "openai_compatible"

            def is_configured(self):
                return True

            def stream_chat(self, request):
                raise ProviderError(BILLING_REQUIRED_CODE, "insufficient quota")
                yield  # pragma: no cover - makes this a generator

        conv = AiConversation.objects.create(user=qa_user, model=None)
        with umock.patch.object(
            gateway, "get_adapter", return_value=_BillingAdapter()
        ):
            body = "".join(
                gateway.stream_reply(qa_user, conv, model, "hi", "pay-1")
            )
        assert "billing" in body.lower()
        state = provider_registry.get_provider_payment_state(model.provider)
        assert state is not None and state["category"] == "billing"

    def test_success_clears_recorded_state(self, qa_user):
        from unittest import mock as umock

        from apps.ai_workspace import gateway
        from apps.ai_workspace.providers.base import ChatChunk

        model = _make_model(provider="openai_compat_gw_ok")
        provider_registry.record_provider_payment_issue(
            model.provider, "billing"
        )

        class _GoodAdapter:
            name = "openai_compatible"

            def is_configured(self):
                return True

            def stream_chat(self, request):
                yield ChatChunk(text="hello")

        conv = AiConversation.objects.create(user=qa_user, model=None)
        with umock.patch.object(
            gateway, "get_adapter", return_value=_GoodAdapter()
        ):
            body = "".join(
                gateway.stream_reply(qa_user, conv, model, "hi", "pay-2")
            )
        assert "hello" in body
        assert (
            provider_registry.get_provider_payment_state(model.provider) is None
        )
