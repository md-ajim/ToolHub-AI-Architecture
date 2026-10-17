import datetime

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.subscriptions.models import (
    BillingInterval,
    CreditTransaction,
    Plan,
    PlanPrice,
    Subscription,
    SubscriptionStatus,
    TransactionType,
)
from apps.subscriptions.services import CreditService, EntitlementService, UsageService

User = get_user_model()


@pytest.fixture
def normal_user(db):
    return User.objects.create_user(email="normal@example.com", password="password")


@pytest.fixture
def qa_user(db):
    return User.objects.create_user(
        email="qa-test@toolhub.local", password="password", is_qa_user=True
    )


@pytest.fixture
def premium_plan(db):
    plan = Plan.objects.create(
        code="pro",
        name="Pro Plan",
        storage_limit=1024 * 1024 * 500,
        daily_limit=100,
        batch_limit=10,
        api_limit=500,
        features={
            "tool_bg-remove": True,
            "tool_upscale": True,
            "ai_access": True,
            "high_resolution_export": True,
            "workspace_tier": "pro",
            "workspace_daily_messages": 200,
            "workspace_burst_per_minute": 20,
        },
    )
    PlanPrice.objects.create(
        plan=plan, billing_interval=BillingInterval.MONTHLY, amount=1500
    )
    return plan


@pytest.mark.django_db
class TestQAUserAuthentication:
    def test_qa_user_is_authenticated(self, qa_user):
        assert qa_user.is_authenticated

    def test_qa_user_can_authenticate_via_credentials(self, qa_user):
        assert qa_user.check_password("password")

    def test_normal_user_is_authenticated(self, normal_user):
        assert normal_user.is_authenticated


@pytest.mark.django_db
class TestQACreditUnlimited:
    def test_qa_user_is_not_blocked_by_insufficient_credits(self, qa_user):
        # No wallet, no credits at all — reserve must still succeed.
        assert CreditService.reserve_credits(qa_user, 100000, "qa-test-job") is True

    def test_qa_user_reserve_does_not_create_negative_balance(self, qa_user):
        CreditService.reserve_credits(qa_user, 5000, "qa-test-job")
        wallet = CreditService.get_wallet(qa_user)
        # No usage transaction recorded and balance is unchanged (0).
        assert wallet.balance == 0
        assert CreditTransaction.objects.filter(wallet=wallet).count() == 0

    def test_normal_user_is_still_blocked_by_insufficient_credits(self, normal_user):
        with pytest.raises(CreditService.InsufficientCredits):
            CreditService.reserve_credits(normal_user, 100, "normal-job", "normal")

    def test_premium_user_is_still_subject_to_credit_limits(self, normal_user):
        """A user with an active subscription is not automatically unlimited."""
        CreditService.add_allocation(normal_user, 50, "seed")
        with pytest.raises(CreditService.InsufficientCredits):
            CreditService.reserve_credits(normal_user, 100, "premium-job")

    def test_entitlement_is_qa(self, qa_user, normal_user):
        assert EntitlementService.is_qa(qa_user) is True
        assert EntitlementService.is_qa(normal_user) is False
        assert EntitlementService.is_qa(None) is False


@pytest.mark.django_db
class TestQAQuotaUnlimited:
    def test_qa_user_is_not_blocked_by_daily_limit(self, qa_user):
        # Record a massive number of usages; QA should still pass.
        for i in range(500):
            UsageService.record(qa_user, "resize", amount=1)
        assert UsageService.check_limit(qa_user) is True

    def test_normal_user_is_still_blocked_by_daily_limit(self, normal_user):
        # Normal no-plan user has the default daily limit (5).
        for i in range(50):
            UsageService.record(normal_user, "resize", amount=1)
        assert UsageService.check_limit(normal_user) is False

    def test_premium_user_follows_plan_limit(self, normal_user, premium_plan):
        Subscription.objects.create(
            user=normal_user,
            plan=premium_plan,
            status=SubscriptionStatus.ACTIVE,
            expires_at=timezone.now() + datetime.timedelta(days=30),
        )
        for i in range(150):
            UsageService.record(normal_user, "resize", amount=1)
        # Daily limit from plan is 100 → blocked once usage exceeds.
        assert UsageService.check_limit(normal_user) is False


@pytest.mark.django_db
class TestQAPremiumAccess:
    def test_qa_user_gets_max_tier(self, qa_user):
        from apps.ai_workspace import entitlements
        from apps.ai_workspace.models import ModelTier

        assert entitlements.get_user_tier(qa_user) == ModelTier.MAX

    def test_qa_user_has_unlimited_workspace_limits(self, qa_user):
        from apps.ai_workspace import entitlements
        from apps.ai_workspace.ratelimit import RateLimitExceeded, check_burst_limit, check_daily_cap

        assert entitlements.get_daily_message_limit(qa_user) == entitlements.UNLIMITED
        assert entitlements.get_burst_per_minute(qa_user) == entitlements.UNLIMITED
        # Sentinel must not raise for QA.
        check_daily_cap(qa_user, entitlements.UNLIMITED, used_today=99999)
        check_burst_limit(qa_user, entitlements.UNLIMITED)
