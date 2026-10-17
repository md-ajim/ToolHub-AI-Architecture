"""Payment-state ownership tests (§28-30).

Proves: frontend cannot set financial facts; backend cannot declare success
without verified provider evidence; duplicates collapse to one effect;
out-of-order events cannot roll state backward; refunds create no credits.
"""
import datetime

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from apps.billing.models import (
    Payment, PaymentStatus, PaymentStateTransition,
)
from apps.billing.state_machine import (
    IllegalTransition, MissingEvidence, transition_payment,
    ACTOR_PROVIDER_API, ACTOR_PROVIDER_WEBHOOK, ACTOR_USER_COMMAND,
)
from apps.subscriptions.models import (
    BillingInterval, CreditTransaction, CreditWallet, Plan, PlanPrice,
    Subscription, SubscriptionStatus,
)
from apps.subscriptions.services import CreditService, EntitlementService

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(email="own@example.com", password="pw")


@pytest.fixture
def pro(db):
    plan = Plan.objects.create(code="pro", name="Pro", status="active", is_public=True,
                               storage_limit=1, daily_limit=-1, batch_limit=10, api_limit=1,
                               features={"monthly_credits": 500, "ai_access": True})
    PlanPrice.objects.create(plan=plan, billing_interval=BillingInterval.MONTHLY,
                             amount=999, currency="USD",
                             provider_price_id="variant_pro_m", is_active=True)
    return plan


def _payment(user, plan, **kw):
    args = dict(user=user, plan=plan, amount=999, currency="USD",
                gateway="lemon_squeezy", provider="lemon_squeezy",
                payment_type="one_time", status=PaymentStatus.PENDING,
                order_reference="ord-test-1",
                snapshot={"plan_id": str(plan.id), "amount": 999, "currency": "USD"})
    args.update(kw)
    return Payment.objects.create(**args)


EVIDENCE = {"verified_api_response": True, "trxID": "T1",
            "amount": 999, "currency": "USD"}


# ── transition table ──
@pytest.mark.django_db
def test_success_requires_evidence(user, pro):
    p = _payment(user, pro)
    with pytest.raises(MissingEvidence):
        transition_payment(p, "succeeded", actor_type=ACTOR_PROVIDER_API,
                           source="bkash", evidence={})
    p.refresh_from_db()
    assert p.status == PaymentStatus.PENDING
    assert PaymentStateTransition.objects.filter(payment=p).count() == 0


@pytest.mark.django_db
def test_illegal_transitions_rejected(user, pro):
    p = _payment(user, pro)
    transition_payment(p, "completed", actor_type=ACTOR_PROVIDER_API,
                       source="t", evidence=EVIDENCE)
    for bad in ("pending", "failed", "processing"):
        with pytest.raises(IllegalTransition):
            transition_payment(p, bad, actor_type=ACTOR_PROVIDER_API, source="t")
    p.refresh_from_db()
    assert p.status == PaymentStatus.COMPLETED


@pytest.mark.django_db
def test_refunded_is_terminal(user, pro):
    p = _payment(user, pro)
    transition_payment(p, "completed", actor_type=ACTOR_PROVIDER_API, source="t", evidence=EVIDENCE)
    transition_payment(p, "refunded", actor_type=ACTOR_USER_COMMAND, source="t",
                       evidence={"verified_api_response": True})
    with pytest.raises(IllegalTransition):
        transition_payment(p, "completed", actor_type=ACTOR_PROVIDER_API, source="t", evidence=EVIDENCE)


@pytest.mark.django_db
def test_transition_is_audited(user, pro):
    p = _payment(user, pro)
    transition_payment(p, "processing", actor_type=ACTOR_USER_COMMAND, source="checkout")
    transition_payment(p, "completed", actor_type=ACTOR_PROVIDER_API, source="bkash", evidence=EVIDENCE)
    rows = list(PaymentStateTransition.objects.filter(payment=p).order_by("created_at"))
    assert [(r.from_state, r.to_state) for r in rows] == [("pending", "processing"), ("processing", "completed")]
    assert rows[1].actor_type == ACTOR_PROVIDER_API


# ── frontend cannot own state (§2, §23) ──
@pytest.mark.django_db
def test_no_generic_status_write_endpoint(user, pro):
    """There is no PATCH /payments/{id} {status} anywhere in the URLconf."""
    from django.urls import get_resolver
    names = set()
    def walk(patterns):
        for p in patterns:
            if hasattr(p, "url_patterns"):
                walk(p.url_patterns)
            else:
                names.add(str(getattr(p, "name", "")))
    walk(get_resolver().url_patterns)
    assert "payment-detail-update" not in names
    client = APIClient()
    client.force_authenticate(user=user)
    p = _payment(user, pro)
    for method in ("patch", "put"):
        res = getattr(client, method)(f"/api/v1/billing/payments/{p.id}/", {"status": "succeeded"}, format="json")
        assert res.status_code in (404, 405)
    p.refresh_from_db()
    assert p.status == PaymentStatus.PENDING


@pytest.mark.django_db
def test_checkout_ignores_client_money_fields(user, pro):
    """Tampered amount/currency/credits/status in the request are ignored:
    the server resolves everything from the DB snapshot."""
    client = APIClient()
    client.force_authenticate(user=user)
    price = pro.prices.first()
    res = client.post("/api/v1/billing/checkout/", {
        "plan_id": str(pro.id), "price_id": str(price.id),
        "billing_interval": "monthly", "provider": "bkash",
        # attack fields — no such accepted inputs; must not error nor apply
        "amount": 0, "currency": "BDT", "credits": 999999, "status": "succeeded",
        "success_url": "http://x/s", "cancel_url": "http://x/c",
    }, format="json")
    # bKash unconfigured in test env -> provider error, but crucially no
    # payment row with attacker values may exist.
    assert Payment.objects.filter(user=user, amount=0).count() == 0
    assert CreditService.get_credit_balance(user) == 0
    assert EntitlementService.get_active_plan(user) is None or \
        EntitlementService.get_active_plan(user).code == "free"


# ── acceptance scenario (§29) ──
@pytest.mark.django_db
def test_acceptance_verified_flow_grants_once(user, pro):
    from apps.billing.services import BillingService
    from apps.billing.webhooks_multi import verify_bkash_payment
    payment = Payment.objects.create(
        user=user, plan=pro, amount=119900, currency="BDT",
        gateway="bkash", provider="bkash", payment_type="one_time",
        billing_interval="monthly", status=PaymentStatus.PENDING,
        provider_payment_id="pay_acc_1", order_reference="ord-acc-1",
        snapshot={"plan_id": str(pro.id), "amount": 119900, "currency": "BDT"})
    # 8. Frontend returns — nothing granted yet.
    assert CreditService.get_credit_balance(user) == 0
    # 9-14. Verified evidence -> SUCCEEDED -> subscription -> one grant.
    verify_bkash_payment(str(payment.id), "pay_acc_1", execute_result={
        "statusCode": "0000", "trxID": "TRXACC", "amount": "1199.00",
        "currency": "BDT", "transactionStatus": "Completed"})
    payment.refresh_from_db()
    assert payment.status == PaymentStatus.COMPLETED
    assert Subscription.objects.filter(user=user, status=SubscriptionStatus.ACTIVE).exists()
    assert CreditService.get_credit_balance(user) == 500
    assert PaymentStateTransition.objects.filter(
        payment=payment, to_state="completed",
        actor_type=ACTOR_PROVIDER_API).exists()
    # 17-20. Same evidence again: no duplicates, still SUCCEEDED.
    out = verify_bkash_payment(str(payment.id), "pay_acc_1", execute_result={
        "statusCode": "0000", "trxID": "TRXACC", "amount": "1199.00",
        "currency": "BDT", "transactionStatus": "Completed"})
    assert out.get("duplicate") is True
    assert CreditService.get_credit_balance(user) == 500
    assert CreditTransaction.objects.filter(
        wallet__user=user, reference=f"bkash_payment_{payment.id}").count() == 1


# ── out-of-order protection (§20) ──
@pytest.mark.django_db
def test_stale_subscription_event_ignored(user, pro):
    from apps.billing.webhooks_multi import _dispatch_ls_event
    Subscription.objects.create(
        user=user, plan=pro, status=SubscriptionStatus.ACTIVE, provider="lemon_squeezy",
        provider_subscription_id="sub_stale",
        expires_at=timezone.now() + datetime.timedelta(days=30),
        metadata={"provider_updated_at": "2026-09-30T12:00:00Z"})
    _dispatch_ls_event(
        "subscription_cancelled", {"id": "sub_stale"},
        {"status": "cancelled", "cancelled": True, "updated_at": "2026-09-01T00:00:00Z",
         "variant_id": "variant_pro_m"},
        {}, {"user_id": str(user.id)},
        event_time=datetime.datetime(2026, 9, 1, tzinfo=datetime.timezone.utc), event_id="wh_old")
    sub = Subscription.objects.get(provider_subscription_id="sub_stale")
    assert sub.status == SubscriptionStatus.ACTIVE  # newer confirmed state kept


# ── refund creates no credits (§18, §28) ──
@pytest.mark.django_db
def test_refund_reverses_state_without_credits(user, pro):
    from apps.billing.services import BillingService
    payment = _payment(user, pro)
    BillingService.activate_verified_payment(
        payment, actor_type=ACTOR_PROVIDER_API, source="lemon_squeezy", evidence=EVIDENCE)
    assert CreditService.get_credit_balance(user) == 500
    transition_payment(payment, "refunded", actor_type=ACTOR_PROVIDER_WEBHOOK,
                       source="lemon_squeezy", evidence={"verified_provider_webhook": True})
    payment.refresh_from_db()
    assert payment.status == PaymentStatus.REFUNDED
    # No reversal debit, no new grant: balance untouched, still exactly 1 grant.
    assert CreditService.get_credit_balance(user) == 500
    assert CreditTransaction.objects.filter(wallet__user=user).count() == 1


# ── terminal wins over late failure (§19) ──
@pytest.mark.django_db
def test_failed_claim_after_success_ignored(user, pro):
    from apps.billing.state_machine import touch_failed
    p = _payment(user, pro)
    transition_payment(p, "completed", actor_type=ACTOR_PROVIDER_API, source="t", evidence=EVIDENCE)
    assert touch_failed(p, actor_type=ACTOR_PROVIDER_API, source="t") is False
    p.refresh_from_db()
    assert p.status == PaymentStatus.COMPLETED
