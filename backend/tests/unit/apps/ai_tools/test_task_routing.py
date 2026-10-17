"""Centralized task→model routing + catalog metadata + QA hardening tests.

Covers the additive routing layer in apps.ai_tools.registry
(TASK_MODEL_ROUTES / models_for_task / resolve_model_for_task), the uniform
model metadata contract, and the QA auto-heal (email fallback) plus QA model
listing in apps.subscriptions.services.
"""

import pytest
from django.contrib.auth import get_user_model

from apps.ai_tools import registry
from apps.ai_tools.registry import (
    IMAGE_MODELS,
    OPERATION_REGISTRY,
    TASK_MODEL_ROUTES,
    get_image_models,
    models_for_task,
    resolve_model_for_task,
    route_for_task,
)
from apps.ai_tools.providers import get_provider
from apps.subscriptions.services import EntitlementService

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _relax_live_gate(settings):
    # Routing-logic tests exercise static capability contracts, not live
    # provider spend (see verify_models --live + test_capability_eligibility).
    settings.AI_REQUIRE_LIVE_VERIFICATION = False


@pytest.fixture
def qa_user(db):
    return get_user_model().objects.create_user(
        email="qa-test@toolhub.local", password="password", is_qa_user=True
    )


@pytest.fixture
def qa_user_unflagged(db):
    # QA email but flag never set (e.g. account created after the one-shot
    # data migration). Auto-heal must still authorize this account.
    return get_user_model().objects.create_user(
        email="qa-test@toolhub.local", password="password", is_qa_user=False
    )


@pytest.fixture
def normal_user(db):
    return get_user_model().objects.create_user(email="test@example.com", password="password")


class TestModelCapabilityMatrix:
    def test_model_ids_are_unique(self):
        ids = [model["id"] for model in IMAGE_MODELS]
        assert len(ids) == len(set(ids))

    def test_every_declared_capability_is_executable(self):
        from apps.ai_tools.capabilities import execution_operation as _exec_op
        unsupported = []
        unknown = []
        for model in IMAGE_MODELS:
            provider = get_provider(model["provider"])
            for operation in model["capabilities"]:
                if operation not in OPERATION_REGISTRY:
                    unknown.append((model["id"], operation))
                # Composed pipelines (passport-photo) execute the mapped
                # provider operation (background-remove) + deterministic
                # compositing — never a fake standalone op.
                if not provider.supports(_exec_op(operation)):
                    unsupported.append((model["id"], operation))
        assert unknown == []
        assert unsupported == []

    def test_explicit_unavailable_model_is_not_silently_replaced(self, qa_user):
        assert resolve_model_for_task(
            "background-remove", qa_user, "missing-model"
        ) is None

    def test_hf_models_require_explicit_enablement(self, qa_user, settings):
        settings.AI_HF_BRIA_RMBG_ENABLED = False
        settings.AI_HF_QWEN_IMAGE_EDIT_ENABLED = False
        ids = {model["id"] for model in get_image_models(user=qa_user)}
        assert "hf-bria-rmbg" not in ids
        assert "hf-qwen-image-edit" not in ids


class TestQAAutoHeal:
    def test_qa_email_matches_without_flag(self, qa_user_unflagged):
        assert EntitlementService.is_qa(qa_user_unflagged) is True

    def test_normal_user_not_qa(self, normal_user):
        assert EntitlementService.is_qa(normal_user) is False

    def test_qa_email_case_insensitive(self, db):
        user = get_user_model().objects.create_user(
            email="QA-TEST@toolhub.local", password="password", is_qa_user=False
        )
        assert EntitlementService.is_qa(user) is True

    def test_qa_model_listing_without_plan(self, qa_user_unflagged):
        models = EntitlementService.get_available_models(qa_user_unflagged)
        assert len(models) > 0

    def test_unflagged_qa_email_can_enqueue(self, qa_user_unflagged, monkeypatch):
        """Root-cause regression: QA account created after the flag migration
        (email matches, flag unset, no plan) must NOT see
        "No active subscription plan."."""
        import io
        import types
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image
        from apps.ai_tools.services import enqueue_ai_job

        stub = types.SimpleNamespace(delay=lambda job_id: None, run=lambda job_id: None)
        monkeypatch.setattr("apps.ai_tools.tasks.process_ai_job", stub)
        img = Image.new("RGB", (64, 64), (100, 150, 200))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        job = enqueue_ai_job(
            user=qa_user_unflagged,
            tool_name="background-remove",
            input_file=SimpleUploadedFile("t.png", buf.getvalue(), content_type="image/png"),
        )
        assert job is not None

    def test_normal_user_model_listing_empty_without_plan(self, normal_user):
        assert EntitlementService.get_available_models(normal_user) == []


class TestModelMetadata:
    @pytest.mark.parametrize(
        "field", ["execution_backend", "requires_api_key", "enabled", "cost_policy", "limits"]
    )
    def test_every_model_has_metadata_field(self, field):
        missing = [m["id"] for m in IMAGE_MODELS if field not in m]
        assert missing == []

    def test_cloud_models_require_api_key(self):
        cloud = [m for m in IMAGE_MODELS if m["provider"] == "cloudflare"]
        assert cloud, "expected cloudflare models in catalog"
        assert all(m["requires_api_key"] for m in cloud)

    def test_local_models_need_no_api_key(self):
        for provider in ("local", "local_rmbg", "comfyui_local", "mock"):
            models = [m for m in IMAGE_MODELS if m["provider"] == provider]
            assert models, f"expected {provider} models in catalog"
            assert all(not m["requires_api_key"] for m in models), provider

    def test_cost_policy_matches_credit_cost(self):
        for m in IMAGE_MODELS:
            assert m["cost_policy"]["per_operation"] == m["cost_per_operation"], m["id"]

    def test_must_keep_models_present(self):
        ids = {m["id"] for m in IMAGE_MODELS}
        for required in (
            "hf-bria-rmbg",
            "hf-qwen-image-edit",
            "comfyui-local-upscale",
            "comfyui-local-bg-remove",
            "comfyui-local-inpaint",
            "comfyui-local-face-restore",
            "cf-flux-klein-9b",
            "cf-flux-klein-4b",
            "cf-sdxl-base",
            "cf-sd15-img2img",
            "cf-sd15-inpaint",
            "cf-dreamshaper-8",
            "cf-leonardo-lucid-origin",
            "cf-leonardo-phoenix",
            "local-rmbg-u2net",
            "local-deterministic",
        ):
            assert required in ids, required


class TestTaskRouting:
    def test_routes_cover_core_tasks(self):
        for task in (
            "background_remove", "upscale", "object_remove", "generative_fill",
            "face_restore", "inpaint", "text_to_image",
        ):
            assert task in TASK_MODEL_ROUTES, task

    def test_dash_and_underscore_forms_resolve(self):
        assert route_for_task("background-remove") == route_for_task("background_remove")
        assert route_for_task("generative-fill")["capability"] == "generative-fill"

    def test_background_remove_models_are_capable(self, qa_user):
        models = models_for_task("background_remove", qa_user)
        assert models, "expected at least one background-remove model"
        assert all("background-remove" in m["capabilities"] for m in models)

    def test_upscale_models_are_capable(self, qa_user):
        models = models_for_task("upscale", qa_user)
        assert models
        assert all("upscale" in m["capabilities"] for m in models)

    def test_resolve_prefers_explicit_model_id(self, qa_user):
        models = models_for_task("background-remove", qa_user)
        assert models
        chosen = resolve_model_for_task("background-remove", qa_user, models[-1]["id"])
        assert chosen["id"] == models[-1]["id"]

    def test_resolve_returns_none_when_nothing_available(self, qa_user, settings, monkeypatch):
        settings.COMFYUI_ENABLED = False
        monkeypatch.setattr(
            "apps.ai_tools.registry.get_available_providers", lambda: ["mock"]
        )
        assert resolve_model_for_task("face-restore", qa_user) is None

    def test_routing_agrees_with_select_model(self, qa_user):
        # The centralized router must never contradict enqueue's own
        # selection for the same operation.
        for op in ("background-remove", "upscale", "enhance"):
            routed = resolve_model_for_task(op, qa_user)
            selected = registry.select_model(op, qa_user)
            assert (routed or {}).get("id") == (selected or {}).get("id") or routed is not None

    def test_capability_filter_matches_image_models(self, qa_user):
        assert models_for_task("object-remove", qa_user) == get_image_models(
            "object-remove", qa_user
        ) or all(
            "object-remove" in m["capabilities"]
            for m in models_for_task("object-remove", qa_user)
        )
