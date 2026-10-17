"""Affiliate pipeline tests: tracking, attribution, commission, payout."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.affiliates import services
from apps.affiliates.models import (
    AffiliatePartner,
    Commission,
    Payout,
    Referral,
)

User = get_user_model()


@pytest.fixture
def owner(db):
    return User.objects.create_user(email="owner@example.com", password="password")


@pytest.fixture
def friend(db):
    return User.objects.create_user(email="friend@example.com", password="password")


@pytest.fixture
def partner(owner):
    return services.get_or_create_partner(owner)


def _client(user=None):
    client = APIClient()
    if user:
        client.force_authenticate(user)
    return client


@pytest.mark.django_db
class TestProgramAndLink:
    def test_program_is_public(self):
        res = _client().get("/api/v1/affiliates/program/")
        assert res.status_code == 200
        program = res.data["data"]["program"]
        assert program["commission_percent"] == 20
        assert program["holding_days"] == 30
        assert program["min_payout_cents"] == 5000
        assert program["cookie_days"] == 60

    def test_link_requires_auth(self):
        res = _client().post("/api/v1/affiliates/link/")
        assert res.status_code in (401, 403)

    def test_link_idempotent(self, owner):
        first = _client(owner).post("/api/v1/affiliates/link/").data["data"]
        second = _client(owner).post("/api/v1/affiliates/link/").data["data"]
        assert first["code"] == second["code"]
        assert first["path"] == f"/r/{first['code']}"
        assert AffiliatePartner.objects.filter(user=owner).count() == 1


@pytest.mark.django_db
class TestClicks:
    def test_click_recorded(self, partner):
        before = partner.clicks.count()
        res = _client().post(
            "/api/v1/affiliates/clicks/", {"code": partner.code}, format="json"
        )
        assert res.status_code == 200
        assert partner.clicks.count() == before + 1

    def test_unknown_code_404s(self):
        res = _client().post(
            "/api/v1/affiliates/clicks/", {"code": "NOPE1234"}, format="json"
        )
        assert res.status_code == 404


@pytest.mark.django_db
class TestAttribution:
    def test_attribute_new_user(self, friend, partner):
        referral = services.attribute_referral(friend, partner.code)
        assert referral is not None
        assert referral.partner_id == partner.id
        assert referral.status == "pending"

    def test_first_attribution_wins(self, friend, partner, owner):
        other = User.objects.create_user(email="other@example.com", password="x")
        other_partner = services.get_or_create_partner(other)
        services.attribute_referral(friend, partner.code)
        # Second code must not steal the referral.
        kept = services.attribute_referral(friend, other_partner.code)
        assert kept.partner_id == partner.id
        assert Referral.objects.filter(referred_user=friend).count() == 1

    def test_self_referral_blocked(self, owner, partner):
        assert services.attribute_referral(owner, partner.code) is None
        assert Referral.objects.filter(referred_user=owner).count() == 0

    def test_unknown_and_suspended_codes_ignored(self, friend, partner):
        assert services.attribute_referral(friend, "NOPE1234") is None
        partner.status = AffiliatePartner.STATUS_SUSPENDED
        partner.save()
        assert services.attribute_referral(friend, partner.code) is None
        assert Referral.objects.filter(referred_user=friend).count() == 0

    def test_attribute_endpoint(self, friend, partner):
        res = _client(friend).post(
            "/api/v1/affiliates/attribute/",
            {"referral_code": partner.code},
            format="json",
        )
        assert res.status_code == 200
        assert res.data["data"]["attributed"] is True

    def test_register_attribution_end_to_end(self, partner):
        client = _client()
        res = client.post(
            "/api/v1/auth/register/",
            {"email": "newbie@example.com", "password": "SecurePassword123!",
             "full_name": "New", "referral_code": partner.code},
            format="json",
        )
        assert res.status_code in (200, 201), res.content[:300]
        user = User.objects.get(email="newbie@example.com")
        assert user.referral.partner_id == partner.id


@pytest.mark.django_db
class TestCommissionAndPayout:
    def _paid_referral(self, friend, partner, amount_minor=999):
        from apps.billing.models import Payment

        referral = services.attribute_referral(friend, partner.code)
        payment = Payment.objects.create(
            user=friend,
            amount=amount_minor,
            currency="USD",
            gateway="stripe",
            status="completed",
            transaction_id="tx-1",
        )
        return referral, payment

    def test_accrue_once_per_referral(self, friend, partner, settings):
        settings.AFFILIATE_COMMISSION_PERCENT = 20
        referral, payment = self._paid_referral(friend, partner)
        first = services.accrue_commission_for_payment(payment)
        assert first is not None
        assert first.amount_minor == 199  # 20% of 999, floored
        assert first.status == "pending"
        # Second payment by same user accrues nothing.
        from apps.billing.models import Payment

        payment2 = Payment.objects.create(
            user=friend, amount=999, currency="USD", gateway="stripe",
            status="completed", transaction_id="tx-2",
        )
        assert services.accrue_commission_for_payment(payment2) is None
        assert Commission.objects.filter(referral=referral).count() == 1
        referral.refresh_from_db()
        assert referral.status == "qualified"

    def test_holding_and_balance(self, friend, partner, settings):
        from datetime import timedelta

        from django.utils import timezone

        settings.AFFILIATE_COMMISSION_PERCENT = 20
        settings.AFFILIATE_HOLDING_DAYS = 30
        referral, payment = self._paid_referral(friend, partner, amount_minor=10000)
        services.accrue_commission_for_payment(payment)
        balance = services.partner_balance_cents(partner)
        assert balance["pending_cents"] == 2000
        assert balance["available_cents"] == 0
        # Age past holding → available.
        Commission.objects.filter(partner=partner).update(
            created_at=timezone.now() - timedelta(days=31)
        )
        balance = services.partner_balance_cents(partner)
        assert balance["available_cents"] == 2000
        assert balance["pending_cents"] == 0

    def test_payout_minimum_and_flow(self, friend, partner, settings):
        from datetime import timedelta

        from django.utils import timezone

        settings.AFFILIATE_COMMISSION_PERCENT = 20
        settings.AFFILIATE_HOLDING_DAYS = 0
        settings.AFFILIATE_MIN_PAYOUT_CENTS = 5000
        # Below minimum → rejected.
        referral, payment = self._paid_referral(friend, partner, amount_minor=999)
        services.accrue_commission_for_payment(payment)
        res = _client(partner.user).post("/api/v1/affiliates/payouts/", {}, format="json")
        assert res.status_code == 400
        # Fund past minimum → full-balance payout created.
        friend2 = User.objects.create_user(email="f2@example.com", password="x")
        services.attribute_referral(friend2, partner.code)
        from apps.billing.models import Payment

        payment2 = Payment.objects.create(
            user=friend2, amount=50000, currency="USD", gateway="stripe",
            status="completed", transaction_id="tx-3",
        )
        services.accrue_commission_for_payment(payment2)
        res = _client(partner.user).post("/api/v1/affiliates/payouts/", {}, format="json")
        assert res.status_code == 201, res.content[:300]
        body = res.data["data"]
        assert body["amount_minor"] == 199 + 10000
        assert body["status"] == "requested"
        assert body["created_at"]  # GET/POST parity for the frontend contract
        # Balance now locked in the payout.
        balance = services.partner_balance_cents(partner)
        assert balance["available_cents"] == 0
        assert Payout.objects.filter(partner=partner).count() == 1

    def test_stats_endpoint(self, friend, partner):
        services.attribute_referral(friend, partner.code)
        res = _client(partner.user).get("/api/v1/affiliates/stats/")
        assert res.status_code == 200
        data = res.data["data"]
        assert data["enrolled"] is True
        assert data["code"] == partner.code
        assert data["signups"] == 1
        assert "program" in data


@pytest.mark.django_db
class TestWebhookAccrual:
    def test_invoice_webhook_accrues_commission(self, friend, partner, settings):
        import datetime

        from django.utils import timezone

        from apps.billing.webhooks import _handle_invoice_payment_succeeded
        from apps.subscriptions.models import Plan, Subscription, SubscriptionStatus

        settings.AFFILIATE_COMMISSION_PERCENT = 20
        services.attribute_referral(friend, partner.code)
        plan = Plan.objects.create(
            code="pro-wh",
            name="Pro WH",
            features={"monthly_credits": 100},
        )
        Subscription.objects.create(
            user=friend,
            plan=plan,
            status=SubscriptionStatus.ACTIVE,
            provider="stripe",
            provider_subscription_id="sub_wh_1",
            expires_at=timezone.now() + datetime.timedelta(days=30),
        )
        _handle_invoice_payment_succeeded({
            "subscription": "sub_wh_1",
            "amount_paid": 999,
            "currency": "usd",
            "payment_intent": "pi_wh_1",
            "created": 1600000000,
            "number": "INV-WH-1",
            "hosted_invoice_url": "http://example.com/inv",
        })
        commission = Commission.objects.get(referral__referred_user=friend)
        assert commission.amount_minor == 199
        assert commission.status == "pending"
        assert commission.partner_id == partner.id
