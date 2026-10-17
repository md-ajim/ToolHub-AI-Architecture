import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from django.utils import timezone
import datetime
from decimal import Decimal

from apps.subscriptions.models import Plan, PlanPrice, Subscription, SubscriptionStatus, CreditWallet
from apps.billing.models import Payment, Invoice, BillingProfile
from apps.billing.webhooks import _handle_checkout_completed, _handle_invoice_payment_succeeded

User = get_user_model()

@pytest.fixture
def user(db):
    return User.objects.create_user(email="testuser@example.com", password="password")

@pytest.fixture
def plan(db):
    plan = Plan.objects.create(
        code="pro",
        name="Pro Plan",
        features={"monthly_credits": 1000}
    )
    # Canonical: checkout sends PlanPrice.provider_price_id (per-interval),
    # never Plan.provider_price_id.
    PlanPrice.objects.create(
        plan=plan, billing_interval="monthly", amount=999, currency="USD",
        provider_price_id="price_12345", is_active=True,
    )
    return plan

@pytest.mark.django_db
@patch('stripe.Subscription.retrieve')
def test_handle_checkout_completed(mock_retrieve, user, plan):
    # Mock Stripe subscription retrieve
    mock_retrieve.return_value = {
        'current_period_start': 1600000000,
        'current_period_end': 1602592000,
        'items': {'data': [{'price': {'id': 'price_12345'}}]}
    }
    
    session_data = {
        'mode': 'subscription',
        'metadata': {'user_id': user.id},
        'subscription': 'sub_123',
        'customer': 'cus_123'
    }
    
    _handle_checkout_completed(session_data)
    
    # Check if subscription was created
    sub = Subscription.objects.get(user=user)
    assert sub.plan == plan
    assert sub.status == SubscriptionStatus.ACTIVE
    assert sub.provider_subscription_id == 'sub_123'
    
    # Check if billing profile was created
    profile = BillingProfile.objects.get(user=user)
    assert profile.provider_customer_id == 'cus_123'

@pytest.mark.django_db
def test_handle_invoice_payment_succeeded(user, plan):
    # Setup active subscription
    sub = Subscription.objects.create(
        user=user,
        plan=plan,
        status=SubscriptionStatus.ACTIVE,
        provider='stripe',
        provider_subscription_id='sub_123',
        expires_at=timezone.now() + datetime.timedelta(days=30)
    )
    
    invoice_data = {
        'subscription': 'sub_123',
        'amount_paid': 1500,
        'currency': 'usd',
        'payment_intent': 'pi_123',
        'created': 1600000000,
        'number': 'INV-123',
        'hosted_invoice_url': 'http://example.com/inv'
    }
    
    _handle_invoice_payment_succeeded(invoice_data)
    
    # Check payment recorded (amount stored in minor units)
    payment = Payment.objects.get(user=user)
    assert payment.amount == 1500
    assert payment.transaction_id == 'pi_123'
    
    # Check invoice recorded
    invoice = Invoice.objects.get(payment=payment)
    assert invoice.invoice_number == 'INV-123'
    
    # Check credits allocated
    wallet = CreditWallet.objects.get(user=user)
    # The monthly_credits from plan features is 1000
    assert wallet.balance == 1000
