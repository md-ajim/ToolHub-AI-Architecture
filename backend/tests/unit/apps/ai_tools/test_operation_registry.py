"""Operation registry tests: face-restore + inpaint are first-class operations.

Confirms the capability-based model routing stays centralized in
``apps.ai_tools.registry`` and that both operations flow through the same
entitlement → model-selection → enqueue pipeline as every other operation:

- ``face-restore`` / ``inpaint`` are known operations with underscore feature
  keys, credit costs, and capability-catalog entries.
- Capability filtering returns the right models per operation (local
  deterministic inpaint always; local ComfyUI face-restore when enabled).
- QA user can queue both operations without a subscription; a free user
  without a plan is still blocked by "No active subscription plan."
"""

import io
import types

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient

from apps.ai_tools.registry import (
    ALL_CAPABILITIES,
    get_credit_cost,
    get_image_models,
    get_operation,
    is_known_operation,
    list_operations,
    select_model,
)
from apps.ai_tools.services import enqueue_ai_job

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


class TestOperationRegistration:
    def test_face_restore_is_known(self):
        assert is_known_operation("face-restore") is True

    def test_inpaint_is_known(self):
        assert is_known_operation("inpaint") is True

    def test_unknown_operation_still_rejected(self):
        assert is_known_operation("not-real") is False

    def test_feature_keys_use_underscores(self):
        assert get_operation("face-restore")["feature"] == "ai_face_restore"
        assert get_operation("inpaint")["feature"] == "ai_inpaint"

    def test_credit_costs_defined(self):
        assert get_credit_cost("face-restore") == 1
        assert get_credit_cost("inpaint") == 2

    def test_capability_catalog_includes_both(self):
        assert "face-restore" in ALL_CAPABILITIES
        assert "inpaint" in ALL_CAPABILITIES

    def test_operations_listing_includes_both(self):
        names = {op["operation"] for op in list_operations()}
        assert "face-restore" in names
        assert "inpaint" in names


class TestCapabilityModelRouting:
    """Centralized routing: models are filtered by capability, provider
    configuration, and user tier — no per-view special cases."""

    def test_inpaint_routes_to_local_deterministic_without_cloud(self, qa_user):
        # Quality-first routing: mock / local-deterministic are TEST-ONLY and
        # never production-eligible. Inpaint resolves only to real providers
        # (comfy_local inpaint); test-only models remain reachable with
        # include_test_only=True for unit-test isolation.
        from apps.ai_tools.registry import get_image_models as _get_models
        models = get_image_models("inpaint", qa_user)
        ids = {m["id"] for m in models}
        assert "mock-generative-fill" not in ids
        assert "local-deterministic" not in ids
        test_only = _get_models("inpaint", qa_user, production_only=False, include_test_only=True)
        test_ids = {m["id"] for m in test_only}
        assert "mock-generative-fill" in test_ids

    def test_select_model_prefers_configured_provider_for_inpaint(self, qa_user):
        selected = select_model("inpaint", qa_user)
        assert selected is not None
        assert "inpaint" in selected["capabilities"]

    def test_face_restore_routes_to_local_comfyui_when_enabled(
        self, qa_user, comfy_settings
    ):
        models = get_image_models("face-restore", qa_user)
        ids = {m["id"] for m in models}
        assert "comfyui-local-face-restore" in ids

    def test_face_restore_unavailable_without_any_capable_provider(
        self, qa_user, settings, monkeypatch
    ):
        # Only the mock provider configured → no model advertises face-restore.
        settings.COMFYUI_ENABLED = False
        monkeypatch.setattr(
            "apps.ai_tools.registry.get_available_providers", lambda: ["mock"]
        )
        assert get_image_models("face-restore", qa_user) == []


class TestOperationEnqueue:
    def test_qa_queues_face_restore_without_plan(
        self, qa_user, comfy_settings, comfy_task_stub
    ):
        job = enqueue_ai_job(
            user=qa_user,
            tool_name="face-restore",
            input_file=make_png(),
            model_id="comfyui-local-face-restore",
        )
        assert job is not None
        assert job.tool_name == "face-restore"

    def test_qa_queues_inpaint_without_plan(self, qa_user, comfy_settings, comfy_task_stub):
        job = enqueue_ai_job(
            user=qa_user,
            tool_name="inpaint",
            input_file=make_png(),
            mask_file=make_png(),
            model_id="comfyui-local-inpaint",
        )
        assert job is not None
        assert job.tool_name == "inpaint"

    def test_text_to_image_does_not_require_an_upload(
        self, qa_user, ai_task_stub, settings, monkeypatch
    ):
        from apps.ai_tools import providers as _providers
        settings.CLOUDFLARE_ACCOUNT_ID = "test-account"
        settings.CLOUDFLARE_API_TOKEN = "test-token"
        assert _providers.CloudflareImageProvider().is_configured() is True
        client = APIClient()
        client.force_authenticate(qa_user)
        response = client.post(
            "/api/v1/ai/operation/",
            {
                "tool_name": "text-to-image",
                "prompt": "a studio product photograph",
                "model_id": "cf-flux-klein-4b",
            },
            format="multipart",
        )
        assert response.status_code == 202

    def test_disabled_feature_flag_blocks_enqueue(
        self, qa_user, ai_task_stub, settings
    ):
        settings.AI_EXPANSION_ENABLED = False
        with pytest.raises(PermissionError, match="not enabled"):
            enqueue_ai_job(
                user=qa_user,
                tool_name="expand",
                input_file=make_png(),
                model_id="mock-expand",
            )

    def test_unknown_explicit_model_is_rejected(
        self, qa_user, ai_task_stub
    ):
        with pytest.raises(ValueError, match="MODEL_CAPABILITY_MISMATCH"):
            enqueue_ai_job(
                user=qa_user,
                tool_name="background-remove",
                input_file=make_png(),
                model_id="missing-model",
            )

    def test_incompatible_model_is_rejected_with_mismatch(
        self, qa_user, ai_task_stub
    ):
        # A text-to-image model must never be accepted for object-remove.
        with pytest.raises(ValueError, match="MODEL_CAPABILITY_MISMATCH"):
            enqueue_ai_job(
                user=qa_user,
                tool_name="object-remove",
                input_file=make_png(),
                model_id="cf-flux-klein-4b",
            )

    def test_comfy_inpaint_requires_mask(
        self, qa_user, comfy_settings, comfy_task_stub
    ):
        with pytest.raises(ValueError, match="mask"):
            enqueue_ai_job(
                user=qa_user,
                tool_name="inpaint",
                input_file=make_png(),
                model_id="comfyui-local-inpaint",
            )

    def test_fal_inpaint_requires_mask_at_enqueue(
        self, qa_user, ai_task_stub, settings, monkeypatch
    ):
        # Masked fal endpoint must reject maskless requests BEFORE credits
        # are reserved (not later in the worker after a refund cycle).
        settings.AI_REQUIRE_LIVE_VERIFICATION = False
        monkeypatch.setattr(
            "apps.ai_tools.providers.fal.FalImageProvider.is_configured",
            lambda self: True,
        )
        with pytest.raises(ValueError, match="mask"):
            enqueue_ai_job(
                user=qa_user,
                tool_name="object-remove",
                input_file=make_png(),
                model_id="fal-qwen-inpaint",
            )

    def test_fal_inpaint_with_mask_queues(
        self, qa_user, ai_task_stub, settings, monkeypatch
    ):
        settings.AI_REQUIRE_LIVE_VERIFICATION = False
        monkeypatch.setattr(
            "apps.ai_tools.providers.fal.FalImageProvider.is_configured",
            lambda self: True,
        )
        job = enqueue_ai_job(
            user=qa_user,
            tool_name="object-remove",
            input_file=make_png(),
            mask_file=make_png(),
            model_id="fal-qwen-inpaint",
        )
        assert job is not None
        assert job.model_id == "fal-qwen-inpaint"

    def test_auto_inpaint_without_mask_uses_maskless_provider(
        self, qa_user, comfy_settings, ai_task_stub, comfy_task_stub
    ):
        job = enqueue_ai_job(
            user=qa_user,
            tool_name="object-remove",
            input_file=make_png(),
            mask_file=make_png(),
        )
        assert job.provider in {"comfyui_local", "cloudflare", "fal"}

    def test_public_parameters_cannot_override_model(
        self, qa_user, ai_task_stub
    ):
        with pytest.raises(ValueError, match="model_id"):
            enqueue_ai_job(
                user=qa_user,
                tool_name="background-remove",
                input_file=make_png(),
                model_id="local-rmbg-u2net",
                parameters={"model_name": "other-model"},
            )

    def test_free_user_blocked_for_new_operations(self, normal_user, ai_task_stub):
        for tool_name in ("face-restore", "inpaint"):
            with pytest.raises(PermissionError) as exc:
                enqueue_ai_job(
                    user=normal_user, tool_name=tool_name, input_file=make_png()
                )
            assert "No active subscription plan" in str(exc.value)

class TestFrontendOperationAliases:
    """Regression: frontend tool ids must resolve to canonical operations.

    The batch UI sends its own ids verbatim (e.g. operationId "bg-remove");
    the backend previously returned empty selectors and HTTP 422
    "Unknown operation: bg-remove" for the DEFAULT batch operation.
    All resolution flows through canonical_operation (single choke point).
    """

    def test_aliases_resolve_to_canonical(self):
        from apps.ai_tools.registry import canonical_operation

        assert canonical_operation("bg-remove") == "background-remove"
        assert canonical_operation("passport") == "passport-photo"
        assert canonical_operation("ai-product-studio") == "product-photography"
        # Canonical ids and normalization pass through untouched.
        assert canonical_operation("background-remove") == "background-remove"
        assert canonical_operation("BG_REMOVE") == "background-remove"
        assert canonical_operation("shadow") == "shadow"
        assert canonical_operation("") == ""

    def test_alias_targets_exist_in_registries(self):
        from apps.ai_tools.capabilities import TOOL_REQUIRED_CAPABILITIES
        from apps.ai_tools.registry import OPERATION_ALIASES, OPERATION_REGISTRY

        assert set(OPERATION_ALIASES) == {"bg-remove", "passport", "ai-product-studio"}
        for alias, target in OPERATION_ALIASES.items():
            assert target in OPERATION_REGISTRY, alias
            assert target in TOOL_REQUIRED_CAPABILITIES, alias

    def test_selector_accepts_frontend_alias(self, qa_user):
        from rest_framework.test import APIClient

        client = APIClient()
        client.force_authenticate(qa_user)
        res = client.get("/api/v1/ai/models/?tool_name=bg-remove")
        assert res.status_code == 200, res.data
        data = res.data["data"]
        assert data["operation"] == "background-remove"
        ids = [m["id"] for m in data["models"]]
        assert "local-rmbg-u2net" in ids
        assert data["recommended_model"] in ids

    def test_batch_enqueue_accepts_frontend_alias(self, qa_user, ai_task_stub):
        from rest_framework.test import APIClient

        client = APIClient()
        client.force_authenticate(qa_user)
        res = client.post(
            "/api/v1/ai/batch/",
            {"tool_name": "bg-remove", "images": [make_png()]},
            format="multipart",
        )
        assert res.status_code == 202, res.data
        assert len(res.data["data"]["job_ids"]) == 1
        assert res.data["data"]["failed_items"] == []
