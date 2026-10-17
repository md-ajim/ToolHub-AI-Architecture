"""QA authorization + cloud provider cost-protection tests for AI tools.

Confirms the full request path from entitlement through model selection to job
enqueue behaves correctly for both account classes and safeguards cloud spend:

- QA user (qa-test@toolhub.local) can queue an image operation WITHOUT any
  subscription — the "No active subscription plan." error must never reach QA.
- Normal free user without a plan is still blocked by the exact same message.
- Once an AI result pipeline is used, QA must never be charged credits.
- Cloud provider / model / cost limits (via env) block dispatch BEFORE any
  provider call, and returning the controlled 429 message. Local/mock providers
  are always exempt — and QA cannot bypass the platform spend shield.
- Usage accounting rows are written only for cloud providers after dispatch.
"""

import datetime
import io
import types

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from PIL import Image

from apps.ai_tools.limits import ProviderLimitError, ProviderLimitService
from apps.ai_tools.services import enqueue_ai_job
from apps.subscriptions.models import (
    BillingInterval,
    Plan,
    PlanPrice,
    Subscription,
    SubscriptionStatus,
)
from apps.subscriptions.services import CreditService, EntitlementService

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _relax_live_gate(settings):
    # Routing-logic tests exercise static capability contracts, not live
    # provider spend (see verify_models --live + test_capability_eligibility).
    settings.AI_REQUIRE_LIVE_VERIFICATION = False


def make_png() -> SimpleUploadedFile:
    img = Image.new("RGB", (64, 64), (100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return SimpleUploadedFile("test.png", buf.getvalue(), content_type="image/png")


def make_large_png(width: int = 5000, height: int = 100) -> SimpleUploadedFile:
    img = Image.new("RGB", (width, height), (10, 200, 90))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return SimpleUploadedFile("huge.png", buf.getvalue(), content_type="image/png")


@pytest.fixture
def qa_user(db):
    return get_user_model().objects.create_user(
        email="qa-test@toolhub.local", password="password", is_qa_user=True
    )


@pytest.fixture
def normal_user(db):
    return get_user_model().objects.create_user(email="test@example.com", password="password")


@pytest.fixture
def ai_task_stub(monkeypatch):
    stub = types.SimpleNamespace(delay=lambda job_id: None, run=lambda job_id: None)
    monkeypatch.setattr("apps.ai_tools.tasks.process_ai_job", stub)
    return stub


@pytest.fixture
def comfy_task_stub(monkeypatch):
    stub = types.SimpleNamespace(delay=lambda job_id: None, run=lambda job_id: None)
    monkeypatch.setattr("apps.ai_tools.tasks.process_comfyui_job", stub)
    return stub


@pytest.fixture
def comfy_settings(settings):
    settings.COMFYUI_ENABLED = True
    settings.COMFYUI_QA_ACCESSIBLE = True
    settings.CELERY_TASK_ALWAYS_EAGER = False
    return settings


@pytest.fixture
def hf_settings(settings):
    settings.AI_HF_BRIA_RMBG_ENABLED = True
    settings.AI_HF_QWEN_IMAGE_EDIT_ENABLED = True
    return settings


def _give_plan(user):
    plan = Plan.objects.create(
        code="pro",
        name="Pro Plan",
        features={"ai_access": True, "ai_background_remove": True},
    )
    PlanPrice.objects.create(plan=plan, billing_interval=BillingInterval.MONTHLY, amount=1500)
    Subscription.objects.create(
        user=user,
        plan=plan,
        status=SubscriptionStatus.ACTIVE,
        expires_at=timezone.now() + datetime.timedelta(days=30),
    )
    return plan


class TestQANeverSeesNoPlan:
    """Critical Problem #1 regression guard.

    The QA user has no subscription at all. Every image operation must queue
    successfully and must never raise "No active subscription plan.".
    """

    def test_qa_queues_background_remove_without_plan(self, qa_user, ai_task_stub):
        job = enqueue_ai_job(
            user=qa_user,
            tool_name="background-remove",
            input_file=make_png(),
            model_id="local-rmbg-u2net",
        )
        assert job is not None
        assert job.status == "queued"

    def test_qa_queues_upscale_without_plan(self, qa_user, comfy_settings, comfy_task_stub):
        job = enqueue_ai_job(
            user=qa_user,
            tool_name="upscale",
            input_file=make_png(),
            model_id="comfyui-local-upscale",
        )
        assert job is not None
        assert job.tool_name == "upscale"

    def test_qa_queues_generative_fill_without_plan(self, qa_user, hf_settings, ai_task_stub):
        job = enqueue_ai_job(
            user=qa_user,
            tool_name="generative-fill",
            input_file=make_png(),
            model_id="hf-qwen-image-edit",
        )
        assert job is not None
        assert job.tool_name == "generative-fill"

    def test_qa_queues_passport_photo_without_plan(self, qa_user, ai_task_stub):
        # Composed pipeline reuses verified background-removal models.
        job = enqueue_ai_job(
            user=qa_user,
            tool_name="passport-photo",
            input_file=make_png(),
            model_id="local-rmbg-u2net",
        )
        assert job is not None
        assert job.tool_name == "passport-photo"

    @pytest.mark.parametrize(
        "tool_name,model_id",
        [
            ("enhance", "fal-clarity-enhance"),
            ("relight", "fal-relight"),
            ("shadow", "photoroom-shadow"),
            ("recolor", "fal-flux-kontext-edit"),
            ("retouch", "photoroom-beautify"),
            ("fashion-model", "fal-fashn-tryon"),
        ],
    )
    def test_qa_keyed_operations_queue_with_real_models(
        self, qa_user, ai_task_stub, settings, tool_name, model_id
    ):
        # Former gaps now resolve to real assessed models when provider keys
        # exist (keys forced on for determinism; live gate still applies in
        # production). No mock, no fake output.
        settings.FAL_KEY = "test-key"
        settings.PHOTOROOM_API_KEY = "test-key"
        job = enqueue_ai_job(
            user=qa_user,
            tool_name=tool_name,
            input_file=make_png(),
            model_id=model_id,
        )
        assert job is not None
        assert job.model_id == model_id
        assert job.provider in {"fal", "photoroom"}

    @pytest.mark.parametrize(
        "tool_name",
        ["enhance", "relight", "shadow"],
    )
    def test_qa_gap_operation_fails_clearly_without_fake_output(
        self, qa_user, ai_task_stub, settings, tool_name
    ):
        # No verified production model exists for these capabilities yet:
        # fail clearly instead of returning mock/deterministic output.
        settings.FAL_KEY = ""
        settings.PHOTOROOM_API_KEY = ""
        settings.OPENROUTER_API_KEY = ""
        settings.COMFYUI_ENABLED = False
        with pytest.raises(ValueError, match="No compatible production model"):
            enqueue_ai_job(
                user=qa_user,
                tool_name=tool_name,
                input_file=make_png(),
            )

    def test_mock_model_rejected_in_production(self, qa_user, ai_task_stub):
        # TEST-ONLY mocks are never resolvable through production enqueue.
        with pytest.raises(ValueError, match="MODEL_CAPABILITY_MISMATCH"):
            enqueue_ai_job(
                user=qa_user,
                tool_name="background-remove",
                input_file=make_png(),
                model_id="mock-bg-remove",
            )

    def test_qa_job_never_reserves_credits(self, qa_user, ai_task_stub):
        # QA has no wallet row at all; enqueue must pass and the QA account must
        # never be charged (no CreditTransaction rows).
        job = enqueue_ai_job(user=qa_user, tool_name="background-remove", input_file=make_png(), model_id="local-rmbg-u2net")
        assert job is not None
        assert job.reserved_credits == 0
        assert job.parameters["quoted_credits"] > 0
        from apps.subscriptions.models import CreditTransaction

        assert CreditTransaction.objects.filter(wallet__user=qa_user).count() == 0


class TestNormalUserStillProtected:
    def test_free_user_without_plan_still_blocked(self, normal_user, ai_task_stub):
        with pytest.raises(PermissionError) as exc:
            enqueue_ai_job(
                user=normal_user,
                tool_name="background-remove",
                input_file=make_png(),
                model_id="local-rmbg-u2net",
            )
        assert "No active subscription plan" in str(exc.value)

    def test_free_user_not_treated_as_qa(self, normal_user):
        assert EntitlementService.is_qa(normal_user) is False

    def test_paid_user_with_plan_queues(self, normal_user, ai_task_stub):
        _give_plan(normal_user)
        CreditService.add_allocation(normal_user, 100, "seed")
        job = enqueue_ai_job(
            user=normal_user,
            tool_name="background-remove",
            input_file=make_png(),
            model_id="local-rmbg-u2net",
        )
        assert job is not None

    def test_production_never_resolves_mock_demo(self, normal_user, ai_task_stub):
        # Mock is TEST-ONLY: a paid-plan user requesting it gets a clear
        # capability-mismatch error, never a $0 fake demo job.
        _give_plan(normal_user)

        with pytest.raises(ValueError, match="MODEL_CAPABILITY_MISMATCH"):
            enqueue_ai_job(
                user=normal_user,
                tool_name="background-remove",
                input_file=make_png(),
                model_id="mock-bg-remove",
            )

    def test_paid_user_without_credits_blocked_for_paid_model(self, normal_user, monkeypatch, ai_task_stub):
        # The protection still holds for real (paid) providers: no credits
        # means no queue.
        _give_plan(normal_user)
        monkeypatch.setattr(
            "apps.ai_tools.services.resolve_model_for_task",
            lambda op, user, mid=None, model_filter=None: CLOUD_TEST_MODEL,
        )
        from apps.subscriptions.services import CreditService as CS

        with pytest.raises(CS.InsufficientCredits):
            enqueue_ai_job(
                user=normal_user,
                tool_name="background-remove",
                input_file=make_png(),
            )

    def test_qa_flag_is_isolated(self, qa_user, normal_user):
        assert EntitlementService.is_qa(qa_user) is True
        assert EntitlementService.is_qa(normal_user) is False


CLOUD_TEST_MODEL = {
    "id": "cloud-test-model",
    "provider": "huggingface",
    "internal_model_id": "briaai/RMBG-2.0",
    "capabilities": ["background-remove"],
    "supported_input_formats": ["PNG"],
    "max_resolution": (4096, 4096),
    "cost_per_operation": 2,
    "availability": True,
}


class TestProviderCostProtection:
    """Cloud spend shield — enforced before dispatch, tests must not hit APIs."""

    def test_cloud_provider_limited_at_zero_blocks_qa_too(self, qa_user, monkeypatch, ai_task_stub):
        # Even QA cannot bypass the owner's spend shield when a limit is hit.
        monkeypatch.setenv("PROVIDER_DAILY_LIMIT_HUGGINGFACE", "0")
        monkeypatch.setattr(
            "apps.ai_tools.services.models_for_task",
            lambda op, user=None: [CLOUD_TEST_MODEL],
        )
        monkeypatch.setattr(
            "apps.ai_tools.services.resolve_model_for_task",
            lambda op, user, mid=None, model_filter=None: CLOUD_TEST_MODEL,
        )
        with pytest.raises(ProviderLimitError):
            enqueue_ai_job(user=qa_user, tool_name="background-remove", input_file=make_png())

    def test_local_provider_exempt_from_limits(self, qa_user, monkeypatch, ai_task_stub):
        monkeypatch.setenv("PROVIDER_DAILY_LIMIT_LOCAL_RMBG", "0")
        job = enqueue_ai_job(
            user=qa_user,
            tool_name="background-remove",
            input_file=make_png(),
            model_id="local-rmbg-u2net",
        )
        assert job is not None

    def test_limit_cleared_allows_dispatch(self, qa_user, monkeypatch, ai_task_stub, settings):
        monkeypatch.setenv("PROVIDER_DAILY_LIMIT_HUGGINGFACE", "5")
        monkeypatch.setattr(
            "apps.ai_tools.services.models_for_task",
            lambda op, user=None: [CLOUD_TEST_MODEL],
        )
        monkeypatch.setattr(
            "apps.ai_tools.services.resolve_model_for_task",
            lambda op, user, mid=None, model_filter=None: CLOUD_TEST_MODEL,
        )
        job = enqueue_ai_job(user=qa_user, tool_name="background-remove", input_file=make_png())
        assert job is not None

    def test_usage_recorded_for_cloud_provider_after_dispatch(self, qa_user, monkeypatch, ai_task_stub):
        monkeypatch.setenv("PROVIDER_DAILY_LIMIT_HUGGINGFACE", "5")
        monkeypatch.setattr(
            "apps.ai_tools.services.models_for_task",
            lambda op, user=None: [CLOUD_TEST_MODEL],
        )
        monkeypatch.setattr(
            "apps.ai_tools.services.resolve_model_for_task",
            lambda op, user, mid=None, model_filter=None: CLOUD_TEST_MODEL,
        )
        enqueue_ai_job(user=qa_user, tool_name="background-remove", input_file=make_png())
        from apps.subscriptions.models import UsageRecord

        assert UsageRecord.objects.filter(usage_type="provider:huggingface").count() == 1
        assert UsageRecord.objects.filter(usage_type="model:briaai/RMBG-2.0").count() == 1
        assert UsageRecord.objects.filter(usage_type="cloud_cost").count() == 1

    def test_no_usage_recorded_for_local_provider(self, qa_user, ai_task_stub):
        from apps.subscriptions.models import UsageRecord

        enqueue_ai_job(user=qa_user, tool_name="background-remove", input_file=make_png(), model_id="local-rmbg-u2net")
        assert UsageRecord.objects.filter(usage_type="provider:mock").count() == 0

    def test_is_allowed_respects_model_user_limit(self, qa_user, monkeypatch):
        from apps.subscriptions.models import UsageRecord

        monkeypatch.setenv("MODEL_USER_LIMIT_HUGGINGFACE_BRIAAI_RMBG_2_0", "1")
        ProviderLimitService.record_usage(qa_user, "huggingface", "briaai/RMBG-2.0", cost=2)
        assert ProviderLimitService.is_allowed(qa_user, "huggingface", "briaai/RMBG-2.0") is False
        assert ProviderLimitService.is_allowed(qa_user, "huggingface", "other/model") is True

    def test_disabled_provider_blocks(self, qa_user, monkeypatch):
        monkeypatch.setenv("PROVIDER_ENABLED_CLOUDFLARE", "false")
        assert ProviderLimitService.is_allowed(qa_user, "cloudflare", "cf-sdxl-base") is False
        with pytest.raises(ProviderLimitError):
            ProviderLimitService.enforce(qa_user, "cloudflare", "cf-sdxl-base")

    def test_unconfigured_limits_allow(self, qa_user):
        assert ProviderLimitService.is_allowed(qa_user, "cloudflare", "cf-sdxl-base") is True


class TestOversizeAutoFit:
    """Any-size uploads are fitted to the model's max resolution (aspect
    preserved) instead of hard-failing the job."""

    def test_oversize_image_queues_fitted(self, qa_user, ai_task_stub):
        job = enqueue_ai_job(
            user=qa_user,
            tool_name="background-remove",
            input_file=make_large_png(5000, 100),
            model_id="local-rmbg-u2net",  # max_resolution (4096, 4096)
        )
        assert job is not None
        assert job.input_width == 4096
        assert job.input_height <= 100
        # Aspect ratio preserved (≈50:1).
        assert abs(job.input_width / job.input_height - 50) < 1

    def test_fit_recorded_and_original_preserved(self, qa_user, ai_task_stub):
        job = enqueue_ai_job(
            user=qa_user,
            tool_name="background-remove",
            input_file=make_large_png(5000, 100),
            model_id="local-rmbg-u2net",
        )
        note = job.parameters["downscaled_to_fit_model"]
        assert note["from"] == [5000, 100]
        assert note["to"] == [job.input_width, job.input_height]
        with Image.open(job.original_file) as original:
            assert original.size == (5000, 100)

    def test_fitting_image_needs_no_downscale(self, qa_user, ai_task_stub):
        job = enqueue_ai_job(
            user=qa_user,
            tool_name="background-remove",
            input_file=make_png(),
            model_id="local-rmbg-u2net",
        )
        assert job.input_width == 64
        assert job.input_height == 64
        assert job.parameters["downscaled_to_fit_model"] is None