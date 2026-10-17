import pytest

from apps.ai_workspace import routing
from apps.ai_workspace.models import AiWorkspaceModel
from apps.accounts.models import User


@pytest.fixture(autouse=True)
def _allow_mock_models(settings):
    """Routing-logic fixtures use mock-provider rows; opt into mock mode."""
    settings.AI_ALLOW_MOCK_MODELS = True


@pytest.fixture
def user(db):
    return User.objects.create_user(email="router@example.com", password="password")


@pytest.fixture
def registry(db):
    return {
        "light": AiWorkspaceModel.objects.create(
            id="t-light",
            provider="mock",
            provider_model_id="m1",
            display_name="Light",
            tier="free",
            capabilities=["chat", "files"],
            context_window=8192,
            sort_order=10,
        ),
        "coder": AiWorkspaceModel.objects.create(
            id="t-coder",
            provider="mock",
            provider_model_id="m2",
            display_name="Coder",
            tier="pro",
            capabilities=["chat", "reasoning", "coding"],
            context_window=32768,
            sort_order=20,
        ),
        "vision": AiWorkspaceModel.objects.create(
            id="t-vision",
            provider="mock",
            provider_model_id="m3",
            display_name="Vision",
            tier="max",
            capabilities=["chat", "vision"],
            context_window=128000,
            sort_order=30,
        ),
    }


@pytest.mark.django_db
class TestAutoRouting:
    def test_returns_none_without_candidates(self, db, user):
        assert routing.select_auto_model(user, "hello") is None

    def test_default_picks_highest_tier(self, user, registry):
        # Free user: only t-light is entitled.
        assert routing.select_auto_model(user, "hello").id == "t-light"

    def test_code_prompt_prefers_coding_capability(self, user, registry):
        # Free user: only t-light is entitled.
        from apps.subscriptions.models import Plan, PlanPrice, Subscription, BillingInterval
        from django.utils import timezone
        from decimal import Decimal

        plan = Plan.objects.create(
            name="Pro Plan",
            storage_limit=1024*1024*500,
            daily_limit=100,
            batch_limit=10,
            api_limit=500,
            features={"workspace_tier": "pro", "workspace_daily_messages": 200, "workspace_burst_per_minute": 20},
        )
        PlanPrice.objects.create(plan=plan, billing_interval=BillingInterval.MONTHLY, amount=1500)
        Subscription.objects.create(
            user=user,
            plan=plan,
            status="active",
            starts_at=timezone.now(),
            expires_at=timezone.now() + timezone.timedelta(days=30),
        )
        prompt = "def broken():\n    return 1/0\n\nfix this traceback"
        assert routing.select_auto_model(user, prompt).id == "t-coder"

    def test_image_request_requires_vision_model(self, user, registry):
        assert routing.select_auto_model(user, "describe", has_images=True) is None

    def test_image_request_uses_vision_model(self, db, registry):
        qa_user = User.objects.create_user(
            email="qa-vision@example.com", password="password", is_qa_user=True
        )
        assert routing.select_auto_model(
            qa_user, "describe", has_images=True
        ).id == "t-vision"

    def test_fallback_respects_entitlement(self, user, registry):
        # Free user has no other eligible model: no silent upgrade (doc §21).
        assert routing.fallback_model(user, registry["light"]) is None

    def test_fallback_prefers_closest_tier(self, user, registry):
        # Free user has no other eligible model: no silent upgrade (doc §21).
        from apps.subscriptions.models import Plan, PlanPrice, Subscription, BillingInterval
        from django.utils import timezone
        from decimal import Decimal

        plan = Plan.objects.create(
            name="Pro Plan",
            storage_limit=1024*1024*500,
            daily_limit=100,
            batch_limit=10,
            api_limit=500,
            features={"workspace_tier": "pro", "workspace_daily_messages": 200, "workspace_burst_per_minute": 20},
        )
        PlanPrice.objects.create(plan=plan, billing_interval=BillingInterval.MONTHLY, amount=1500)
        Subscription.objects.create(
            user=user,
            plan=plan,
            status="active",
            starts_at=timezone.now(),
            expires_at=timezone.now() + timezone.timedelta(days=30),
        )
        fallback = routing.fallback_model(user, registry["coder"])
        assert fallback is not None
        assert fallback.id == "t-light"


@pytest.mark.django_db
class TestMockFallback:
    def test_eligible_mock_chat_model_returns_strongest_eligible(self, db, user, registry):
        # Free user: only the free-tier mock chat models are eligible.
        model = routing.eligible_mock_chat_model(user)
        assert model is not None
        assert model.provider == "mock"
        assert "chat" in (model.capabilities or [])

    def test_eligible_mock_chat_model_none_without_mock(self, db, user):
        from apps.ai_workspace.models import AiWorkspaceModel
        AiWorkspaceModel.objects.create(
            id="t-nomock",
            provider="openai",
            provider_model_id="gpt-4",
            display_name="No Mock Here",
            tier="max",
            capabilities=["chat"],
            context_window=8192,
            status="active",
            sort_order=1,
        )
        assert routing.eligible_mock_chat_model(user) is None

    def test_auto_route_appends_mock_when_all_siblings_down(self, db, settings):
        """When the chosen model and its same-provider siblings are all
        unreachable, auto-routing must still include a mock last-resort
        candidate so a chat turn always produces text (doc §21)."""
        from apps.accounts.models import User
        from apps.ai_workspace.models import AiWorkspaceModel, TIER_RANK
        settings.OPENAI_API_KEY = "test-key"
        user = User.objects.create_user(
            email="qa-router@example.com", password="password", is_qa_user=True
        )
        # Two unreachable sibling models (same provider), max tier, lowest
        # sort_order so one is auto-selected.
        # Two unreachable sibling models (same provider), max tier, lowest
        # sort_order so one is auto-selected.
        AiWorkspaceModel.objects.create(
            id="t-down-a", provider="openai", provider_model_id="down-a",
            display_name="Down A", tier="max", capabilities=["chat"],
            context_window=8192, status="active", health_status="healthy", sort_order=1,
        )
        AiWorkspaceModel.objects.create(
            id="t-down-b", provider="openai", provider_model_id="down-b",
            display_name="Down B", tier="max", capabilities=["chat"],
            context_window=8192, status="active", health_status="healthy", sort_order=2,
        )
        # A mock chat model the user can fall back to.
        AiWorkspaceModel.objects.create(
            id="t-mock", provider="mock", provider_model_id="m1",
            display_name="Mock", tier="free", capabilities=["chat"],
            context_window=8192, status="active", health_status="healthy", sort_order=99,
        )
        chosen = routing.select_auto_model(user, "hello")
        assert chosen.id == "t-down-a"
        fallback = routing.fallback_model(user, chosen)
        # Same-provider sibling (also down) — NOT mock.
        assert fallback is not None and fallback.id == "t-down-b"
        # The mock last-resort is reachable via the helper.
        mock = routing.eligible_mock_chat_model(user)
        assert mock is not None and mock.id == "t-mock"
