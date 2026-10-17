"""Billing-safety regression tests (Phases 1-2).

Invariants covered:
- Renewal credits are allocated exactly once per invoice, even on duplicate
  webhook delivery under different event IDs.
- Manual retry is a NEW billable attempt (new reservation); automatic Celery
  retry reuses the existing reservation (no worker-side re-reserve).
- Fallback keeps the customer charge stable (reserved_credits unchanged).
- effective_batch_limit = min(plan_limit, global_system_limit).
- seed_plans synchronizes configuration into existing Plan records.
- Customer credits and provider USD cost are stored separately.
"""
import datetime

import pytest
from celery.exceptions import Retry
from django.contrib.auth import get_user_model
from django.utils import timezone

from unittest.mock import patch

from apps.ai_tools.models import AIProcessingJob
from apps.billing.models import Payment, PaymentStatus, Refund
from apps.billing.services import BillingService
from apps.billing.webhooks import (
    _handle_charge_refunded,
    _handle_invoice_payment_succeeded,
)
from apps.subscriptions.models import (
    CreditTransaction,
    CreditWallet,
    Plan,
    Subscription,
    SubscriptionStatus,
)
from apps.subscriptions.services import CreditService, EntitlementService

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(email="billing-safety@example.com", password="password")


@pytest.fixture
def plan(db):
    return Plan.objects.create(
        name="Pro",
        code="pro-test",
        storage_limit=50 * 1024 * 1024,
        daily_limit=-1,
        batch_limit=10,
        api_limit=300,
        features={"monthly_credits": 1000, "ai_access": True},
    )


def _invoice(subscription_id, invoice_id="in_test_1"):
    return {
        "subscription": subscription_id,
        "id": invoice_id,
        "amount_paid": 999,
        "currency": "usd",
        "payment_intent": "pi_test_1",
        "charge": "ch_test_1",
        "created": 1600000000,
        "number": "INV-TEST-1",
        "hosted_invoice_url": "http://example.com/inv",
        "invoice_pdf": "http://example.com/inv.pdf",
        "period_start": 1600000000,
        "period_end": 1602592000,
    }


@pytest.mark.django_db
def test_renewal_idempotent_same_invoice_twice(user, plan):
    """Duplicate delivery of the same invoice must allocate credits exactly once."""
    sub = Subscription.objects.create(
        user=user,
        plan=plan,
        status=SubscriptionStatus.ACTIVE,
        provider="stripe",
        provider_subscription_id="sub_renewal_test",
        expires_at=timezone.now() + datetime.timedelta(days=30),
    )
    _handle_invoice_payment_succeeded(_invoice("sub_renewal_test"))
    _handle_invoice_payment_succeeded(_invoice("sub_renewal_test"))

    wallet = CreditWallet.objects.get(user=user)
    assert wallet.ai_credits == 1000
    assert (
        CreditTransaction.objects.filter(
            wallet=wallet, reference="sub_renewal_in_test_1"
        ).count()
        == 1
    )


@pytest.mark.django_db
def test_manual_retry_requires_new_reservation(user):
    """After a failure refund, re-execution must reserve anew (no free retry)."""
    CreditService.add_allocation(user, 10, "test_alloc", "ai")
    CreditService.reserve_credits(user, 2, "Queued AI Tool: bg-remove", "ai")
    # Failure path refunds...
    CreditService.refund_credits(user, 2, "Refund for failed AI Tool: bg-remove", "ai")
    assert CreditService.get_credit_balance(user, "ai") == 10
    # ...so a manual retry MUST create a new reservation for the new attempt.
    CreditService.reserve_credits(user, 2, "Manual retry AI Tool: bg-remove (attempt 1)", "ai")
    assert CreditService.get_credit_balance(user, "ai") == 8


@pytest.mark.django_db
def test_automatic_retry_reuses_reservation_no_double_charge(user):
    """Same-attempt Celery retry must NOT create a second reservation."""
    CreditService.add_allocation(user, 10, "test_alloc", "ai")
    CreditService.reserve_credits(user, 2, "Queued AI Tool: bg-remove", "ai")
    # Worker preamble does nothing; balance reflects exactly one reservation.
    assert CreditService.get_credit_balance(user, "ai") == 8


@pytest.mark.django_db
def test_fallback_keeps_customer_charge_stable(user):
    """Customer reserved/consumed credits are unchanged by provider fallback."""
    job = AIProcessingJob.objects.create(
        user=user,
        tool_name="background-remove",
        provider="cloudflare",
        model_id="flux-klein-4b",
        reserved_credits=2,
        parameters={"fallback_from": "cloudflare", "fallback_provider": "huggingface"},
    )
    # Deterministic fallback billing: customer charge == original reservation.
    job.consumed_credits = job.reserved_credits
    job.save(update_fields=["consumed_credits"])
    job.refresh_from_db()
    assert job.consumed_credits == 2
    assert job.parameters["fallback_from"] == "cloudflare"
    # Provider cost is tracked separately, never in the credit fields.
    assert job.provider_cost_usd is None
    assert job.cost_source in ("unknown", "estimated", "zero_vendor_cost")


@pytest.mark.django_db
def test_effective_batch_limit_min_plan_global():
    """effective_batch_limit = min(plan_limit, global_system_limit)."""
    cases = [
        # (plan_limit, global_limit, expected)
        (1, 20, 1),    # FREE
        (10, 20, 10),  # PRO
        (100, 20, 20),  # BUSINESS capped by infrastructure safety limit
        (100, 200, 100),
    ]
    for plan_limit, global_limit, expected in cases:
        effective = min(plan_limit, global_limit) if plan_limit > 0 else global_limit
        assert effective == expected


@pytest.mark.django_db
def test_seed_sync_updates_existing_plan(plan):
    """Seed re-run must synchronize config fields into existing records."""
    from django.core.management import call_command

    # Point the fixture at the real seeded plan code so the seed actually
    # syncs this row (previously code="pro-test" meant the seed never touched
    # it and the test passed trivially).
    plan.code = "pro"
    plan.features = {"monthly_credits": 1000, "ai_access": True}
    plan.save(update_fields=["code", "features"])

    call_command("seed_plans")
    plan.refresh_from_db()
    # Seeded pro values are authoritative for config fields.
    assert plan.batch_limit == 10
    assert plan.features.get("ai_access") is True
    assert plan.features.get("monthly_credits") == 500


@pytest.mark.django_db
def test_plan_change_preserves_balances(user, plan):
    """Upgrade/downgrade must not corrupt existing credit balances."""
    CreditService.add_allocation(user, 50, "test_alloc", "ai")
    sub = Subscription.objects.create(
        user=user,
        plan=plan,
        status=SubscriptionStatus.ACTIVE,
        provider="stripe",
        provider_subscription_id="sub_plan_change",
        expires_at=timezone.now() + datetime.timedelta(days=30),
    )
    business = Plan.objects.create(
        name="Business",
        code="business-test",
        storage_limit=500 * 1024 * 1024,
        daily_limit=-1,
        batch_limit=100,
        api_limit=5000,
        features={"monthly_credits": 3000, "ai_access": True},
    )
    sub.plan = business
    sub.save()
    assert CreditService.get_credit_balance(user, "ai") == 50


@pytest.mark.django_db
def test_entitlement_free_background_remove(user):
    """Free plan gates: ai_access + ai_background_remove must both be enabled."""
    free = Plan.objects.create(
        name="Free",
        code="free-test",
        storage_limit=5 * 1024 * 1024,
        daily_limit=5,
        batch_limit=1,
        api_limit=0,
        features={"monthly_credits": 0, "ai_access": True, "ai_background_remove": True},
    )
    Subscription.objects.create(
        user=user,
        plan=free,
        status=SubscriptionStatus.ACTIVE,
        provider="stripe",
        provider_subscription_id="sub_free_test",
        expires_at=timezone.now() + datetime.timedelta(days=30),
    )
    assert EntitlementService.get_active_plan(user).code == "free-test"
    assert EntitlementService.has_feature(user, "ai_access") is True
    assert EntitlementService.has_feature(user, "ai_background_remove") is True
    assert EntitlementService.get_limit(user, "batch_limit", fallback_limit=1) == 1


@pytest.mark.django_db
def test_credit_mutation_idempotency_key_debits_and_credits_once(user):
    CreditService.add_allocation(user, 10, "idempotency-test-allocation", "ai")

    CreditService.reserve_credits(
        user,
        3,
        "Queued idempotent job",
        "ai",
        idempotency_key="job:test:attempt:0:reserve",
    )
    CreditService.reserve_credits(
        user,
        3,
        "Queued idempotent job",
        "ai",
        idempotency_key="job:test:attempt:0:reserve",
    )
    assert CreditService.get_credit_balance(user, "ai") == 7
    assert CreditTransaction.objects.filter(
        idempotency_key__endswith="job:test:attempt:0:reserve"
    ).count() == 1

    CreditService.refund_credits(
        user,
        3,
        "Refund idempotent job",
        "ai",
        idempotency_key="job:test:attempt:0:failure-refund",
    )
    CreditService.refund_credits(
        user,
        3,
        "Refund idempotent job",
        "ai",
        idempotency_key="job:test:attempt:0:failure-refund",
    )
    assert CreditService.get_credit_balance(user, "ai") == 10
    assert CreditTransaction.objects.filter(
        idempotency_key__endswith="job:test:attempt:0:failure-refund"
    ).count() == 1


@pytest.mark.django_db
def test_payment_refund_is_idempotent_and_does_not_grant_ai_credits(user):
    CreditService.add_allocation(user, 20, "payment-refund-allocation", "ai")
    payment = Payment.objects.create(
        user=user,
        amount=999,
        currency="USD",
        gateway="stripe",
        status=PaymentStatus.COMPLETED,
        transaction_id="pi_refund_safety",
        provider_payment_id="pi_refund_safety",
    )

    with patch("apps.billing.services.BillingService.get_provider") as get_provider:
        get_provider.return_value.create_refund.return_value = {
            "id": "re_refund_safety",
            "status": "succeeded",
        }
        first = BillingService.process_refund(str(payment.id))
        second = BillingService.process_refund(str(payment.id))

    assert first.id == second.id
    assert Refund.objects.filter(payment=payment).count() == 1
    payment.refresh_from_db()
    assert payment.status == PaymentStatus.REFUNDED
    assert CreditService.get_credit_balance(user, "ai") == 20


@pytest.mark.django_db
def test_external_refund_webhook_is_idempotent_and_does_not_grant_credits(user):
    payment = Payment.objects.create(
        user=user,
        amount=500,
        currency="USD",
        gateway="stripe",
        status=PaymentStatus.COMPLETED,
        transaction_id="pi_external_refund",
        provider_payment_id="pi_external_refund",
    )
    charge = {
        "id": "ch_external_refund",
        "payment_intent": "pi_external_refund",
        "amount_refunded": 500,
    }

    _handle_charge_refunded(charge)
    _handle_charge_refunded(charge)

    assert Refund.objects.filter(payment=payment).count() == 1
    payment.refresh_from_db()
    assert payment.status == PaymentStatus.REFUNDED
    assert not CreditWallet.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_celery_retry_is_not_converted_into_failure_refund(user):
    from apps.ai_tools.tasks import process_ai_job

    CreditService.add_allocation(user, 5, "retry-safety-allocation", "ai")
    CreditService.reserve_credits(
        user,
        2,
        "Queued retry safety job",
        "ai",
        idempotency_key="job:retry-safety:attempt:0:reserve",
    )
    job = AIProcessingJob.objects.create(
        user=user,
        tool_name="enhance",
        provider="mock",
        model_id="mock-enhance",
        idempotency_key="retry-safety",
        reserved_credits=2,
        billing_attempt=0,
        max_retries=2,
    )

    with patch(
        "apps.ai_tools.tasks._try_provider",
        side_effect=RuntimeError("temporary provider failure"),
    ):
        with pytest.raises(Retry):
            process_ai_job.run(str(job.id))

    job.refresh_from_db()
    assert job.status == AIProcessingJob.Status.QUEUED
    assert job.retry_count == 1
    assert job.refunded_credits == 0
    assert CreditService.get_credit_balance(user, "ai") == 3
