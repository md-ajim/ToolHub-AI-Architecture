import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
import datetime
from decimal import Decimal

from apps.subscriptions.models import Plan, PlanPrice, Subscription, SubscriptionStatus, CreditWallet, CreditTransaction, TransactionType, BillingInterval
from apps.subscriptions.services import EntitlementService, CreditService

User = get_user_model()

@pytest.fixture
def user(db):
    return User.objects.create_user(email="testuser@example.com", password="password")

@pytest.fixture
def plan(db):
    plan = Plan.objects.create(
        name="Pro Plan",
        storage_limit=1024*1024*500, # 500MB
        daily_limit=100,
        batch_limit=10,
        api_limit=500,
        features={
            "tool_bg-remove": True,
            "tool_upscale": True,
            "ai_access": True,
            "high_resolution_export": True,
            "monthly_credits": 1000,
            "workspace_tier": "pro",
            "workspace_daily_messages": 200,
            "workspace_burst_per_minute": 20,
        }
    )
    PlanPrice.objects.create(plan=plan, billing_interval=BillingInterval.MONTHLY, amount=1500)
    return plan

@pytest.fixture
def subscription(db, user, plan):
    return Subscription.objects.create(
        user=user,
        plan=plan,
        status=SubscriptionStatus.ACTIVE,
        provider='stripe',
        expires_at=timezone.now() + datetime.timedelta(days=30)
    )

@pytest.mark.django_db
class TestEntitlementService:
    def test_get_active_plan_with_subscription(self, user, subscription, plan):
        active_plan = EntitlementService.get_active_plan(user)
        assert active_plan == plan

    def test_get_active_plan_no_subscription(self, user):
        active_plan = EntitlementService.get_active_plan(user)
        assert active_plan is None

    def test_has_feature(self, user, subscription):
        assert EntitlementService.has_feature(user, "tool_bg-remove") is True
        assert EntitlementService.has_feature(user, "cloud_history") is False

    def test_get_limit(self, user, subscription):
        assert EntitlementService.get_limit(user, "storage_limit") == 1024*1024*500
        assert EntitlementService.get_limit(user, "daily_limit") == 100

    def test_can_use_tool(self, user, subscription):
        assert EntitlementService.can_use_tool(user, "bg-remove") is True
        assert EntitlementService.can_use_tool(user, "unknown-tool") is False

@pytest.mark.django_db
class TestCreditService:
    def test_get_wallet(self, user):
        wallet = CreditService.get_wallet(user)
        assert wallet.balance == 0
        assert wallet.user == user

    def test_add_allocation(self, user):
        CreditService.add_allocation(user, 500, "test_allocation")
        wallet = CreditService.get_wallet(user)
        assert wallet.balance == 500
        assert CreditTransaction.objects.filter(wallet=wallet, transaction_type=TransactionType.ALLOCATION).count() == 1

    def test_reserve_credits_success(self, user):
        CreditService.add_allocation(user, 500, "test_allocation")
        result = CreditService.reserve_credits(user, 100, "test_job")
        assert result is True
        wallet = CreditService.get_wallet(user)
        assert wallet.balance == 400
        assert CreditTransaction.objects.filter(wallet=wallet, transaction_type=TransactionType.USAGE).count() == 1

    def test_reserve_credits_insufficient(self, user):
        CreditService.add_allocation(user, 50, "test_allocation")
        with pytest.raises(CreditService.InsufficientCredits):
            CreditService.reserve_credits(user, 100, "test_job")
        wallet = CreditService.get_wallet(user)
        assert wallet.balance == 50

    def test_refund_credits(self, user):
        CreditService.add_allocation(user, 500, "test_allocation")
        CreditService.reserve_credits(user, 100, "test_job")
        CreditService.refund_credits(user, 100, "test_job_failed")
        wallet = CreditService.get_wallet(user)
        assert wallet.balance == 500
        assert CreditTransaction.objects.filter(wallet=wallet, transaction_type=TransactionType.REFUND).count() == 1
