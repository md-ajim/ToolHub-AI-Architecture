"""Rate-limit sentinel arithmetic.

Regression coverage: the QA unlimited sentinel (-1) is scaled by callers
(e.g. compare multiplies the per-model budget by model count). A scaled
sentinel must keep the bypass instead of tripping the zero guard — QA
compare runs failed with "Too many requests." before this guard accepted
any negative value.
"""
import pytest

from apps.ai_workspace import entitlements
from apps.ai_workspace.ratelimit import RateLimitExceeded, check_burst_limit


@pytest.fixture
def qa_user(db):
    from django.contrib.auth import get_user_model

    return get_user_model().objects.create_user(
        email="rl-qa@example.com", password="password", is_qa_user=True
    )


@pytest.mark.django_db
class TestBurstSentinelScaling:
    def test_scaled_unlimited_sentinel_does_not_raise(self, qa_user):
        per_model = entitlements.get_burst_per_minute(qa_user)
        assert per_model == entitlements.UNLIMITED
        # Compare path: per-model budget × model count.
        check_burst_limit(qa_user, per_model * 2)
        check_burst_limit(qa_user, per_model * 3)

    def test_raw_sentinel_does_not_raise(self, qa_user):
        check_burst_limit(qa_user, entitlements.UNLIMITED)

    def test_zero_budget_rejected(self, qa_user):
        with pytest.raises(RateLimitExceeded) as exc:
            check_burst_limit(qa_user, 0)
        assert exc.value.code == "rate_limited"
