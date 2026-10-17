"""Gateway resilience: auto-routed chat turns must always produce text.

Verifies doc §21 — when the auto-selected provider and its same-provider
fallback siblings are all unreachable, the gateway falls back to the
always-available ``mock`` provider instead of emitting a hard SSE error.

These tests call ``gateway.stream_reply`` directly (bypassing the DRF view +
throttles, which depend on Redis). For QA users rate limits are no-ops, so
no external services are required.
"""
from datetime import timedelta
from unittest import mock

import pytest
from django.utils import timezone

from apps.ai_workspace import gateway
from apps.ai_workspace.models import (
    AiConversation,
    AiMessage,
    AiUsageRecord,
    AiWorkspaceModel,
)
from apps.ai_workspace.providers.base import ChatChunk, ProviderError
from apps.subscriptions.models import (
    CreditTransaction,
    Plan,
    Subscription,
    SubscriptionStatus,
)
from apps.subscriptions.services import CreditService


@pytest.fixture(autouse=True)
def _allow_mock_models(settings):
    """Gateway fallback tests exercise the mock last-resort; opt in."""
    settings.AI_ALLOW_MOCK_MODELS = True


UNREACHABLE = "unreachable"


class _UnreachableAdapter:
    """Adapter that is 'configured' but always fails with a retryable error."""

    name = UNREACHABLE

    def is_configured(self) -> bool:
        return True

    def stream_chat(self, request):
        raise ProviderError("provider_error", "simulated provider failure")


class _RecordingMockAdapter:
    """Stand-in mock adapter that emits a deterministic chunk."""

    name = "mock"

    def is_configured(self) -> bool:
        return True

    def stream_chat(self, request):
        yield ChatChunk(text="mocked-fallback-text")


class _EmptyAdapter:
    name = "mock"

    def is_configured(self) -> bool:
        return True

    def stream_chat(self, request):
        return iter(())


class _PartialAdapter:
    name = "mock"

    def is_configured(self) -> bool:
        return True

    def stream_chat(self, request):
        yield ChatChunk(text="partial-output")


def _fake_get_adapter(provider):
    if provider == UNREACHABLE:
        return _UnreachableAdapter()
    if provider == "mock":
        return _RecordingMockAdapter()
    raise ProviderError("provider_not_found", f"Unknown provider '{provider}'.")


def _make_qa_user():
    from django.contrib.auth import get_user_model

    return get_user_model().objects.create_user(
        email="qa-test@example.com", password="password", is_qa_user=True
    )


def _make_billed_user_and_model():
    from django.contrib.auth import get_user_model

    user = get_user_model().objects.create_user(
        email="gateway-billing@example.com",
        password="password",
    )
    plan = Plan.objects.create(
        name="Pro",
        code="pro-gateway-billing",
        storage_limit=50 * 1024 * 1024,
        daily_limit=-1,
        batch_limit=10,
        api_limit=300,
        features={"monthly_credits": 100, "ai_access": True},
    )
    Subscription.objects.create(
        user=user,
        plan=plan,
        status=SubscriptionStatus.ACTIVE,
        provider="stripe",
        provider_subscription_id="sub_gateway_billing",
        expires_at=timezone.now() + timedelta(days=30),
    )
    CreditService.add_allocation(user, 5, "gateway-test-allocation", "ai")
    model = AiWorkspaceModel.objects.create(
        id="t-billed-mock",
        provider="mock",
        provider_model_id="mock-billed",
        display_name="Billed Mock",
        tier="free",
        capabilities=["chat"],
        context_window=8192,
        max_output_tokens=2048,
        status="active",
        health_status="healthy",
        sort_order=1,
        cost_policy={"credits_per_message": 2},
    )
    return user, model


def _make_models():
    AiWorkspaceModel.objects.create(
        id="t-down-a", provider=UNREACHABLE, provider_model_id="down-a",
        display_name="Down A", tier="max", capabilities=["chat"],
        context_window=8192, status="active", health_status="healthy", sort_order=1,
        cost_policy={"credits_per_message": 0},
    )
    AiWorkspaceModel.objects.create(
        id="t-down-b", provider=UNREACHABLE, provider_model_id="down-b",
        display_name="Down B", tier="max", capabilities=["chat"],
        context_window=8192, status="active", health_status="healthy", sort_order=2,
        cost_policy={"credits_per_message": 0},
    )
    AiWorkspaceModel.objects.create(
        id="t-mock", provider="mock", provider_model_id="mock-1",
        display_name="Mock", tier="free", capabilities=["chat"],
        context_window=8192, status="active", health_status="healthy", sort_order=99,
        cost_policy={"credits_per_message": 0},
    )


def _drain(stream):
    """Consume a stream_reply generator into a single string of SSE frames."""
    return "".join(stream)


@pytest.mark.django_db
def test_auto_route_falls_back_to_mock_when_provider_down():
    """Primary + sibling both unreachable -> mock last-resort yields text."""
    user = _make_qa_user()
    _make_models()
    conv = AiConversation.objects.create(user=user, model=None)

    with mock.patch.object(gateway, "get_adapter", side_effect=_fake_get_adapter):
        body = _drain(
            gateway.stream_reply(user, conv, None, "hello world", "test-1")
        )

    # Text arrived via the mock last-resort.
    assert "mocked-fallback-text" in body
    assert "provider_not_configured" not in body
    assert "unexpected gateway failure" not in body.lower()


@pytest.mark.django_db
def test_explicit_selection_does_not_fall_back_to_mock():
    """An explicitly-chosen unreachable model stays explicit (doc §21) —
    no silent mock fallback for explicit selections."""
    user = _make_qa_user()
    _make_models()
    down_model = AiWorkspaceModel.objects.get(id="t-down-a")
    conv = AiConversation.objects.create(user=user, model=down_model)

    with mock.patch.object(gateway, "get_adapter", side_effect=_fake_get_adapter):
        body = _drain(
            gateway.stream_reply(user, conv, down_model, "hello world", "explicit-1")
        )

    # Explicit selection with a down provider surfaces a provider error,
    # never the mock text.
    assert "mocked-fallback-text" not in body
    assert "error" in body.lower()


@pytest.mark.django_db
def test_empty_provider_response_refunds_exactly_once():
    user, model = _make_billed_user_and_model()
    conversation = AiConversation.objects.create(user=user, model=model)

    with mock.patch.object(
        gateway,
        "get_adapter",
        return_value=_EmptyAdapter(),
    ):
        body = _drain(
            gateway.stream_reply(
                user,
                conversation,
                model,
                "hello",
                "empty-response-1",
            )
        )

    assert "empty_response" in body
    assert CreditService.get_credit_balance(user, "ai") == 5
    assert CreditTransaction.objects.filter(
        wallet__user=user,
        transaction_type="refund",
    ).count() == 1
    assert not AiUsageRecord.objects.filter(user=user).exists()
    assert AiMessage.objects.filter(
        conversation=conversation,
        author="assistant",
    ).get().status == "failed"


@pytest.mark.django_db
def test_disconnect_after_partial_output_charges_and_replays_once():
    user, model = _make_billed_user_and_model()
    conversation = AiConversation.objects.create(user=user, model=model)

    with mock.patch.object(
        gateway,
        "get_adapter",
        return_value=_PartialAdapter(),
    ):
        stream = gateway.stream_reply(
            user,
            conversation,
            model,
            "hello",
            "partial-response-1",
        )
        next(stream)
        assert "partial-output" in next(stream)
        stream.close()

        replay = _drain(
            gateway.stream_reply(
                user,
                conversation,
                model,
                "hello",
                "partial-response-1",
            )
        )

    assert CreditService.get_credit_balance(user, "ai") == 3
    assert AiUsageRecord.objects.filter(user=user).count() == 1
    message = AiMessage.objects.get(
        conversation=conversation,
        author="assistant",
        idempotency_key="partial-response-1",
    )
    assert message.status == "completed"
    assert message.content == "partial-output"
    assert "replayed" in replay


def test_gateway_error_response_carries_fetchapi_contract():
    """fetchApi parses message/errors; legacy `error` key is preserved."""
    from apps.ai_workspace.gateway import GatewayError
    from apps.ai_workspace.views import _gateway_error_response

    res = _gateway_error_response(GatewayError("rate_limited", "Too many requests."))
    assert res.status_code == 429
    assert res.data["success"] is False
    assert res.data["message"] == "Too many requests."
    assert res.data["errors"] == {"code": "rate_limited"}
    assert res.data["error"] == {"code": "rate_limited", "message": "Too many requests."}
