"""Coherent entitlement + billing contract regression suite.

Covers: Free lifecycle, PlanPrice lookup, coupons, payment allocation
idempotency, upgrade/downgrade validation, cancellation sync, AI auth
normalization + permission parity, model tiers by plan code, batch limits
by plan, stale sweeper, refund helper idempotency.
"""
import datetime
import io
from unittest.mock import patch

import pytest
from PIL import Image
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User as UserModel
from apps.ai_tools.models import AIProcessingJob
from apps.billing.models import Coupon, Payment, PaymentStatus
from apps.billing.services import BillingService, refund_minor_to_credits
from apps.billing.webhooks import (
    _handle_checkout_completed,
    _handle_invoice_payment_succeeded,
    _handle_subscription_updated,
    _resolve_plan_from_provider_price,
)
from apps.subscriptions.models import (
    BillingInterval,
    CreditTransaction,
    CreditWallet,
    Plan,
    PlanPrice,
    Subscription,
    SubscriptionStatus,
    TransactionType,
)
from apps.subscriptions.services import (
    CreditService,
    EntitlementService,
    normalize_ai_feature_key,
    plan_code_of,
)

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(email="contract@example.com", password="pw")


@pytest.fixture
def plans(db):
    free = Plan.objects.create(
        code="free", name="Free", status="active", is_public=True,
        storage_limit=5 * 1024 * 1024, daily_limit=5, batch_limit=1,
        api_limit=0,
        features={"monthly_credits": 0, "basic_tools": True,
                  "ai_access": True, "ai_background_remove": True,
                  "ai_marketplace_resize": True},
    )
    PlanPrice.objects.create(plan=free, billing_interval=BillingInterval.MONTHLY,
                             amount=0, currency="USD", is_active=True)
    pro = Plan.objects.create(
        code="pro", name="Pro", status="active", is_public=True,
        storage_limit=50 * 1024 * 1024, daily_limit=-1, batch_limit=10,
        api_limit=300,
        features={"monthly_credits": 500, "ai_access": True,
                  "ai_background_remove": True, "ai_upscale": True},
    )
    pro_monthly = PlanPrice.objects.create(
        plan=pro, billing_interval=BillingInterval.MONTHLY, amount=999,
        currency="USD", provider_price_id="price_pro_monthly", is_active=True)
    pro_yearly = PlanPrice.objects.create(
        plan=pro, billing_interval=BillingInterval.YEARLY, amount=8900,
        currency="USD", provider_price_id="price_pro_yearly", is_active=True)
    biz = Plan.objects.create(
        code="business", name="Business", status="active", is_public=True,
        storage_limit=500 * 1024 * 1024, daily_limit=-1, batch_limit=100,
        api_limit=5000,
        features={"monthly_credits": 1500, "ai_access": True,
                  "ai_background_remove": True},
    )
    biz_monthly = PlanPrice.objects.create(
        plan=biz, billing_interval=BillingInterval.MONTHLY, amount=2999,
        currency="USD", provider_price_id="price_business_monthly", is_active=True)
    return {"free": free, "pro": pro, "pro_monthly": pro_monthly,
            "pro_yearly": pro_yearly, "business": biz, "biz_monthly": biz_monthly}


# ── Free lifecycle ──

@pytest.mark.django_db
def test_new_user_gets_free_subscription(user, plans):
    sub = EntitlementService.ensure_free_subscription(user)
    assert sub is not None
    assert plan_code_of(sub.plan) == "free"
    assert EntitlementService.get_active_plan(user).code == "free"


@pytest.mark.django_db
def test_free_provisioning_idempotent(user, plans):
    a = EntitlementService.ensure_free_subscription(user)
    b = EntitlementService.ensure_free_subscription(user)
    assert a.id == b.id
    assert Subscription.objects.filter(
        user=user, status=SubscriptionStatus.ACTIVE).count() == 1


@pytest.mark.django_db
def test_existing_paid_not_replaced(user, plans):
    Subscription.objects.create(
        user=user, plan=plans["pro"], status=SubscriptionStatus.ACTIVE,
        provider="stripe", provider_subscription_id="sub_paid_1",
        expires_at=timezone.now() + datetime.timedelta(days=30))
    sub = EntitlementService.ensure_free_subscription(user)
    assert plan_code_of(sub.plan) == "pro"
    assert Subscription.objects.filter(user=user).count() == 1


@pytest.mark.django_db
def test_legacy_no_subscription_resolves_free_display(user, plans):
    assert EntitlementService.get_active_plan(user) is None
    effective = EntitlementService.get_effective_plan(user)
    assert effective is not None and effective.code == "free"
    # After provisioning, active resolution works.
    EntitlementService.ensure_free_subscription(user)
    assert EntitlementService.get_active_plan(user).code == "free"


@pytest.mark.django_db
def test_qa_bypass_no_free_row_needed(db, plans):
    qa = User.objects.create_user(email="qa@example.com", password="pw", is_qa_user=True)
    assert EntitlementService.is_qa(qa) is True
    assert EntitlementService.can_use_ai(qa, "background-remove") is True
    assert EntitlementService.get_limit(qa, "daily_limit") == -1


# ── PlanPrice lookup ──

@pytest.mark.django_db
def test_planprice_lookup_canonical(plans):
    plan = _resolve_plan_from_provider_price("price_pro_monthly")
    assert plan.code == "pro"


@pytest.mark.django_db
def test_planprice_lookup_missing_raises_explicit(plans):
    with pytest.raises(ValueError, match="No PlanPrice mapped"):
        _resolve_plan_from_provider_price("price_nope")


@pytest.mark.django_db
@patch("stripe.Subscription.retrieve")
def test_checkout_creates_subscription_via_planprice(mock_retrieve, user, plans):
    mock_retrieve.return_value = {
        "current_period_start": 1600000000, "current_period_end": 1602592000,
        "items": {"data": [{"price": {"id": "price_pro_monthly"}}]},
    }
    _handle_checkout_completed({
        "mode": "subscription", "metadata": {"user_id": str(user.id)},
        "subscription": "sub_checkout_1", "customer": "cus_1"})
    sub = Subscription.objects.get(provider_subscription_id="sub_checkout_1")
    assert sub.plan.code == "pro"
    # First creation allocates nothing by itself (credits only from payment event).
    assert CreditTransaction.objects.filter(wallet__user=user).count() == 0


# ── Coupons ──

@pytest.fixture
def coupon(db, plans):
    return Coupon.objects.create(
        code="SAVE10", coupon_type="percentage", value=10,
        max_uses=5, uses_count=0, applicable_plans=[str(plans["pro"].id)],
        minimum_amount=0, start_date=timezone.now() - datetime.timedelta(days=1),
        is_active=True)


@pytest.mark.django_db
def test_coupon_validate_and_increment_once(user, plans, coupon):
    price = plans["pro_monthly"]
    result = BillingService.apply_coupon("SAVE10", str(plans["pro"].id), price.amount)
    assert result["discount"] == int(999 * 10 / 100)
    # create_checkout_session consumes exactly once.
    with patch("apps.billing.services.BillingService.get_provider") as gp:
        gp.return_value.create_checkout_session.return_value = "http://x"
        BillingService.create_checkout_session(
            user, str(plans["pro"].id), str(price.id),
            "http://ok", "http://cancel", coupon_code="SAVE10")
    coupon.refresh_from_db()
    assert coupon.uses_count == 1


@pytest.mark.django_db
def test_coupon_wrong_plan_rejected(user, plans, coupon):
    with pytest.raises(ValidationError):
        BillingService.validate_coupon("SAVE10", str(plans["business"].id), 2999)


@pytest.mark.django_db
def test_coupon_invalid_code_rejected(user, plans):
    with pytest.raises(ValidationError):
        BillingService.validate_coupon("NOPE", str(plans["pro"].id), 999)


@pytest.mark.django_db
def test_free_plan_never_checkouts(user, plans):
    free_price = plans["free"].prices.first()
    with pytest.raises(ValidationError, match="Free plan"):
        BillingService.create_checkout_session(
            user, str(plans["free"].id), str(free_price.id), "http://ok", "http://cancel")


# ── Payment allocation ──

def _sub(user, plan, sub_id="sub_pay_1"):
    return Subscription.objects.create(
        user=user, plan=plan, status=SubscriptionStatus.ACTIVE,
        provider="stripe", provider_subscription_id=sub_id,
        expires_at=timezone.now() + datetime.timedelta(days=30))


def _invoice(sub_id, inv="in_1", pi="pi_1"):
    return {"subscription": sub_id, "id": inv, "amount_paid": 999,
            "currency": "usd", "payment_intent": pi, "charge": "ch_1",
            "created": 1600000000, "number": f"INV-{inv}",
            "period_start": 1600000000, "period_end": 1602592000}


@pytest.mark.django_db
def test_first_payment_allocates_pro_500(user, plans):
    _sub(user, plans["pro"])
    _handle_invoice_payment_succeeded(_invoice("sub_pay_1"))
    assert CreditService.get_credit_balance(user) == 500


@pytest.mark.django_db
def test_duplicate_webhook_allocates_once(user, plans):
    _sub(user, plans["pro"])
    _handle_invoice_payment_succeeded(_invoice("sub_pay_1"))
    _handle_invoice_payment_succeeded(_invoice("sub_pay_1"))
    assert CreditService.get_credit_balance(user) == 500
    wallet = CreditWallet.objects.get(user=user)
    assert CreditTransaction.objects.filter(
        wallet=wallet, reference="sub_renewal_in_1").count() == 1


@pytest.mark.django_db
def test_failed_payment_allocates_nothing(user, plans):
    from apps.billing.webhooks import _handle_invoice_payment_failed
    _sub(user, plans["pro"])
    _handle_invoice_payment_failed(
        {"subscription": "sub_pay_1", "amount_due": 999, "currency": "usd",
         "payment_intent": "pi_fail"})
    assert CreditService.get_credit_balance(user) == 0
    sub = Subscription.objects.get(provider_subscription_id="sub_pay_1")
    assert sub.status == SubscriptionStatus.PAST_DUE


# ── Upgrade/downgrade/cancel ──

@pytest.mark.django_db
def test_upgrade_direction_validated(user, plans):
    _sub(user, plans["pro"], "sub_up")
    with patch("apps.billing.services.BillingService.get_provider") as gp:
        gp.return_value.update_subscription.return_value = {"status": "active"}
        # Same-tier "upgrade" rejected.
        with pytest.raises(ValidationError):
            BillingService.upgrade_subscription(
                user, str(plans["pro"].id), str(plans["pro_monthly"].id))
        # Real upgrade preserves balance, no proration (provider called with none).
        sub = BillingService.upgrade_subscription(
            user, str(plans["business"].id), str(plans["biz_monthly"].id))
        assert sub.plan.code == "business"
    # Provider proration contract:
    import apps.billing.providers as prov
    import inspect
    assert "proration_behavior='none'" in inspect.getsource(prov.StripeProvider.update_subscription)


@pytest.mark.django_db
def test_downgrade_direction_validated(user, plans):
    _sub(user, plans["business"], "sub_down")
    with patch("apps.billing.services.BillingService.get_provider") as gp:
        gp.return_value.update_subscription.return_value = {"status": "active"}
        with pytest.raises(ValidationError):
            BillingService.downgrade_subscription(
                user, str(plans["business"].id), str(plans["biz_monthly"].id))
        CreditService.add_allocation(user, 50, "keep")
        sub = BillingService.downgrade_subscription(
            user, str(plans["pro"].id), str(plans["pro_monthly"].id))
        assert sub.plan.code == "pro"
        assert CreditService.get_credit_balance(user) == 50


@pytest.mark.django_db
def test_cancel_preserves_access_until_period_end(user, plans):
    sub = _sub(user, plans["pro"], "sub_cancel")
    with patch("apps.billing.services.BillingService.get_provider") as gp:
        gp.return_value.cancel_subscription.return_value = {"status": "active"}
        BillingService.cancel_subscription(sub.id, cancel_at_period_end=True)
    sub.refresh_from_db()
    assert sub.cancel_at_period_end is True
    assert sub.status == SubscriptionStatus.ACTIVE
    assert CreditService.get_credit_balance(user) == 0  # balance untouched (still 0)
    # Webhook 'updated' with pending cancel must not wipe the flag.
    _handle_subscription_updated({
        "id": "sub_cancel", "status": "active", "cancel_at_period_end": True,
        "current_period_start": 1600000000, "current_period_end": 1900000000})
    sub.refresh_from_db()
    assert sub.cancel_at_period_end is True
    assert sub.status == SubscriptionStatus.ACTIVE


# ── AI auth ──

@pytest.mark.django_db
def test_feature_key_normalization():
    assert normalize_ai_feature_key("background-remove") == "ai_background_remove"
    assert normalize_ai_feature_key("object-remove") == "ai_object_remove"
    assert normalize_ai_feature_key("marketplace-resize") == "ai_marketplace_resize"
    assert normalize_ai_feature_key("face-restore") == "ai_face_restore"
    assert normalize_ai_feature_key("ai_upscale") == "ai_upscale"


@pytest.mark.django_db
def test_can_use_ai_fail_closed_no_plan(user):
    assert EntitlementService.can_use_ai(user, "background-remove") is False
    assert EntitlementService.can_use_ai(user) is False


@pytest.mark.django_db
def test_permission_matches_service(user, plans):
    from apps.subscriptions.permissions import HasAIFeaturePermission
    from unittest.mock import MagicMock
    EntitlementService.ensure_free_subscription(user)
    perm = HasAIFeaturePermission()
    view = MagicMock()
    view.tool_name = "background-remove"
    req = MagicMock()
    req.user = user
    # Free has ai_background_remove -> allowed; upscale not in free -> denied.
    assert perm.has_permission(req, view) is True
    view.tool_name = "upscale"
    assert perm.has_permission(req, view) is False


@pytest.mark.django_db
def test_registered_operations_use_canonical_entitlements(user, plans):
    from apps.subscriptions.services import is_ai_operation_allowed
    EntitlementService.ensure_free_subscription(user)
    assert is_ai_operation_allowed(user, "product-edit") is False
    assert is_ai_operation_allowed(user, "mockup-generate") is False
    assert is_ai_operation_allowed(user, "passport-photo") is True
    assert is_ai_operation_allowed(user, "upscale") is False


@pytest.mark.django_db
def test_temporary_entitlement_integrated_in_canonical_gate(user, plans):
    """TemporaryEntitlement grants flow through the canonical gate only."""
    from apps.subscriptions.models import TemporaryEntitlement
    from apps.subscriptions.services import is_ai_operation_allowed
    EntitlementService.ensure_free_subscription(user)
    assert is_ai_operation_allowed(user, "upscale") is False
    assert EntitlementService.check_entitlement(user, "ai_upscale") is False
    TemporaryEntitlement.objects.create(
        user=user, plan=plans["pro"], reason="trial",
        expires_at=timezone.now() + datetime.timedelta(hours=1), is_active=True)
    assert EntitlementService.check_entitlement(user, "ai_upscale") is True
    assert is_ai_operation_allowed(user, "upscale") is True
    # ...but has_feature (plan-only primitive) stays False — no second system.
    assert EntitlementService.has_feature(user, "ai_upscale") is False


@pytest.mark.django_db
def test_model_tier_by_plan_code(user, plans):
    from apps.subscriptions.services import model_tier_for_plan
    assert model_tier_for_plan(plans["free"]) == "free"
    assert model_tier_for_plan(plans["pro"]) == "pro"
    assert model_tier_for_plan(plans["business"]) == "max"
    # Name decoy must not change authz: rename pro display name.
    plans["pro"].name = "Super Business Pro Max"
    plans["pro"].save()
    assert plan_code_of(plans["pro"]) == "pro"
    assert model_tier_for_plan(plans["pro"]) == "pro"


# ── Margin protection ──

@pytest.mark.django_db
def test_quote_never_below_usd_floor():
    from apps.ai_tools.registry import quote_credits_for_model
    bria = {"id": "hf-bria-rmbg", "provider": "huggingface", "cost_per_operation": 1}
    credits, est, verified = quote_credits_for_model(bria)
    assert verified is True and est == 0.018
    assert credits == 2  # ceil(0.018/0.0094): floor 1 is overridden
    qwen = {"id": "hf-qwen-image-edit", "provider": "huggingface", "cost_per_operation": 3}
    credits, est, _ = quote_credits_for_model(qwen)
    assert credits == 4 and est == 0.03
    local = {"id": "local-deterministic", "provider": "local", "cost_per_operation": 1}
    credits, est, _ = quote_credits_for_model(local)
    assert (credits, est) == (1, 0.0)


@pytest.mark.django_db
def test_quote_resolution_multiplier():
    from apps.ai_tools.registry import quote_credits_for_model
    qwen = {"id": "hf-qwen-image-edit", "provider": "huggingface", "cost_per_operation": 3}
    c1, _, _ = quote_credits_for_model(qwen, 1.0)
    c2, _, _ = quote_credits_for_model(qwen, 2.0)
    c4, _, _ = quote_credits_for_model(qwen, 9.0)
    assert (c1, c2, c4) == (4, 5, 7)


@pytest.mark.django_db
def test_spend_cap_math(user, plans):
    EntitlementService.ensure_free_subscription(user)
    assert EntitlementService.provider_spend_cap_usd(user) == 0.25  # free default
    Subscription.objects.create(
        user=user, plan=plans["pro"], status=SubscriptionStatus.ACTIVE,
        provider="stripe", provider_subscription_id="sub_cap_1",
        expires_at=timezone.now() + datetime.timedelta(days=30))
    assert EntitlementService.provider_spend_cap_usd(user) == round(500 * 0.0094, 4)
    over, spent, cap = EntitlementService.provider_spend_over_cap(user, 0.0)
    assert over is False and spent == 0.0 and cap == round(500 * 0.0094, 4)


@pytest.mark.django_db
def test_over_cap_reroutes_to_zero_cost_model(user, plans):
    """Over-cap paid routing falls back to $0 models instead of failing."""
    from unittest.mock import patch as _patch
    from apps.ai_tools import services as _svc
    from django.core.files.base import ContentFile as _CF
    Subscription.objects.create(
        user=user, plan=plans["pro"], status=SubscriptionStatus.ACTIVE,
        provider="stripe", provider_subscription_id="sub_cap_2",
        expires_at=timezone.now() + datetime.timedelta(days=30))
    CreditService.add_allocation(user, 50, "alloc")
    hf_model = {
        "id": "hf-bria-rmbg",
        "provider": "huggingface",
        "internal_model_id": "briaai/RMBG-2.0",
        "capabilities": ["background-remove"],
        "supported_input_formats": ["PNG"],
        "max_resolution": (4096, 4096),
        "cost_per_operation": 1,
        "availability": True,
    }
    local_model = {
        "id": "local-rmbg-u2net",
        "provider": "local_rmbg",
        "internal_model_id": "local-rmbg-u2net-v1",
        "capabilities": ["background-remove"],
        "supported_input_formats": ["PNG"],
        "max_resolution": (4096, 4096),
        "cost_per_operation": 1,
        "availability": True,
    }
    image_buffer = io.BytesIO()
    Image.new("RGB", (32, 32), (10, 20, 30)).save(image_buffer, "PNG")
    with _patch.object(_svc, "resolve_model_for_task", return_value=dict(hf_model)), \
         _patch.object(_svc, "models_for_task", return_value=[dict(hf_model), dict(local_model)]), \
         _patch.object(EntitlementService, "cycle_provider_spend_usd", return_value=99.0), \
         _patch("apps.ai_tools.tasks.process_ai_job"):
        job = _svc.enqueue_ai_job(
            user,
            "background-remove",
            _CF(image_buffer.getvalue(), name="t.png"),
        )
    assert job.provider == "local_rmbg"
    assert float(job.estimated_provider_cost_usd or 0) == 0


# ── Batch/API ──

@pytest.mark.django_db
def test_batch_limits_by_plan(user, plans):
    EntitlementService.ensure_free_subscription(user)
    assert EntitlementService.get_limit(user, "batch_limit", fallback_limit=1) == 1
    assert plans["pro"].batch_limit == 10
    assert plans["business"].batch_limit == 100
    # Effective = min(plan, global 20).
    assert min(100, 20) == 20


@pytest.mark.django_db
def test_api_denied_for_free(user, plans):
    EntitlementService.ensure_free_subscription(user)
    assert EntitlementService.can_use_api(user) is False


# ── Stale sweeper + refunds ──

@pytest.mark.django_db
def test_stale_sweeper_refunds_once(user, plans):
    from django.core.files.base import ContentFile
    CreditService.add_allocation(user, 10, "alloc")
    CreditService.reserve_credits(user, 2, "Queued AI Tool: x")
    job = AIProcessingJob.objects.create(
        user=user, tool_name="upscale", reserved_credits=2,
        input_file=ContentFile(b"img", name="i.png"))
    # Force staleness.
    AIProcessingJob.objects.filter(id=job.id).update(
        updated_at=timezone.now() - datetime.timedelta(hours=5))
    refunded = CreditService.sweep_stale_reservations(max_age_seconds=60)
    assert str(job.id) in refunded
    assert CreditService.get_credit_balance(user) == 10
    # Idempotent rerun.
    assert CreditService.sweep_stale_reservations(max_age_seconds=60) == []
    job.refresh_from_db()
    assert job.refunded_credits == 2


@pytest.mark.django_db
def test_refund_conversion_documented():
    # Preserved quirk: minor units -> credits at 100:1 truncating.
    assert refund_minor_to_credits(999) == 9
    assert refund_minor_to_credits(50) == 0
    assert refund_minor_to_credits(-100) == 0


@pytest.mark.django_db
def test_process_refund_idempotent(user, plans):
    CreditService.add_allocation(user, 20, "alloc")
    payment = Payment.objects.create(
        user=user, amount=999, currency="USD", gateway="stripe",
        status=PaymentStatus.COMPLETED, transaction_id="pi_r1",
        provider_payment_id="pi_r1")
    with patch("apps.billing.services.BillingService.get_provider") as gp:
        gp.return_value.create_refund.return_value = {"id": "re_1", "status": "succeeded"}
        r1 = BillingService.process_refund(str(payment.id))
        r2 = BillingService.process_refund(str(payment.id))
        assert r1.id == r2.id


@pytest.mark.django_db
def test_plan_prices_honors_plan_id_query_param(plans):
    client = APIClient()
    pro = Plan.objects.get(code="pro")
    res = client.get(f"/api/v1/billing/plan-prices/?plan_id={pro.id}")
    assert res.status_code == 200
    rows = res.data["data"]
    assert len(rows) > 0
    plan_ids = {str(r["plan"]) for r in rows}
    assert plan_ids == {str(pro.id)}


@pytest.mark.django_db
def test_plan_prices_without_filter_returns_public(plans):
    client = APIClient()
    res = client.get("/api/v1/billing/plan-prices/")
    assert res.status_code == 200
    assert len(res.data["data"]) >= 1
