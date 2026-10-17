"""Quality-first capability routing tests (canonical architecture).

Guards the MODEL CAPABILITY & QUALITY implementation:

- Every AI operation declares required capabilities (no generic product_ai).
- Only VERIFIED_PRODUCTION, capability-matching, configured-provider models
  are production-eligible; mocks / local-deterministic / BETA never are.
- Recommended default is quality-first, never cheapest-first.
- User-selected incompatible models raise MODEL_CAPABILITY_MISMATCH.
- Fallbacks stay same-capability; empty eligibility fails clearly.
- /ai/models/ contract exposes only compatible production models.
"""

import pytest
from django.contrib.auth import get_user_model

from apps.ai_tools import eligibility as _elig
from apps.ai_tools.capabilities import (
    TEST_ONLY_MODEL_IDS,
    TOOL_REQUIRED_CAPABILITIES,
    VERIFIED_PRODUCTION,
    model_supports_operation,
    required_capabilities_for_operation,
)
from apps.ai_tools.registry import get_image_models

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _relax_live_gate(settings):
    # Routing-logic tests must not depend on live provider spend: relax the
    # live-inference gate so statically-assessed models are eligible.
    # The gate itself is covered by TestLiveVerificationGate below.
    settings.AI_REQUIRE_LIVE_VERIFICATION = False


@pytest.fixture
def qa_user(db):
    return get_user_model().objects.create_user(
        email="qa-cap-test@toolhub.local", password="password", is_qa_user=True
    )


class TestToolCapabilityContracts:
    def test_every_ai_operation_has_contract(self):
        for op in (
            "background-remove", "passport-photo", "upscale", "enhance",
            "object-remove", "inpaint", "generative-fill",
            "background-generate", "expand", "relight", "shadow",
            "recolor", "retouch", "fashion-retouch", "text-to-image",
            "face-restore", "product-edit", "mockup-generate",
        ):
            assert required_capabilities_for_operation(op), op

    def test_product_tools_have_individual_contracts(self):
        contracts = {
            op: tuple(required_capabilities_for_operation(op))
            for op in (
                "product-staging", "product-photography", "fashion-model",
                "ghost-mannequin", "flat-lay", "fashion-retouch",
                "infographic", "size-chart", "carousel", "social-creative",
                "ad-creative",
            )
        }
        for op, caps in contracts.items():
            assert caps, op
            assert caps != ("product_ai",), op
        # Distinct tools must not all share one identical contract.
        assert len(set(contracts.values())) > 1

    def test_object_remove_requires_inpainting(self):
        caps = required_capabilities_for_operation("object-remove")
        assert "object_removal" in caps and "inpainting" in caps

    def test_passport_reuses_background_removal(self):
        assert required_capabilities_for_operation("passport-photo") == ["background_removal"]


class TestProductionEligibility:
    def test_mock_models_never_production_eligible(self, qa_user):
        for op in ("background-remove", "generative-fill", "expand", "relight", "text-to-image"):
            ids = {m["id"] for m in get_image_models(op, qa_user)}
            assert not (ids & set(TEST_ONLY_MODEL_IDS)), (op, ids)

    def test_mock_reachable_only_via_test_only_flag(self, qa_user):
        prod = {m["id"] for m in get_image_models("background-remove", qa_user)}
        test_only = {
            m["id"]
            for m in get_image_models(
                "background-remove", qa_user,
                production_only=False, include_test_only=True,
            )
        }
        assert "mock-bg-remove" not in prod
        assert "mock-bg-remove" in test_only

    def test_local_deterministic_not_an_ai_model(self, qa_user):
        for op in ("fashion-model", "ghost-mannequin", "product-staging", "upscale", "relight"):
            ids = {m["id"] for m in get_image_models(op, qa_user)}
            assert "local-deterministic" not in ids, op

    def test_text_to_image_model_rejected_for_object_remove(self, qa_user):
        assert model_supports_operation("cf-flux-klein-4b", "text-to-image") is True
        assert model_supports_operation("cf-flux-klein-4b", "object-remove") is False

    def test_gap_operations_have_no_production_model(self, qa_user, settings):
        # With image-provider keys absent, capability gaps fail clearly
        # instead of returning mock/deterministic output. (Keys are forced
        # off here so the test is deterministic in any environment.)
        settings.FAL_KEY = ""
        settings.PHOTOROOM_API_KEY = ""
        settings.OPENROUTER_API_KEY = ""
        settings.COMFYUI_ENABLED = False
        for op in ("enhance", "relight", "shadow", "fashion-model", "product-staging"):
            assert get_image_models(op, qa_user) == [], op


class TestEligibilityService:
    def test_compatible_models_ordered_quality_first(self, qa_user, settings):
        settings.AI_HF_BRIA_RMBG_ENABLED = True
        models = _elig.get_compatible_models_for_tool("background-remove", qa_user)
        assert models, "expected at least local-rmbg in this env"
        assert all(m["quality_status"] == VERIFIED_PRODUCTION for m in models)
        assert all(not m.get("is_mock") for m in models)
        # Recommended first, never cheapest-first by construction.
        assert models[0].get("recommended") is True

    def test_recommended_default_matches_first_compatible(self, qa_user, settings):
        settings.AI_HF_BRIA_RMBG_ENABLED = True
        models = _elig.get_compatible_models_for_tool("background-remove", qa_user)
        recommended = _elig.get_recommended_model_for_tool("background-remove", qa_user)
        assert recommended is not None
        assert recommended["id"] == models[0]["id"]

    def test_validate_accepts_compatible_model(self, qa_user):
        model = _elig.validate_model_for_tool(
            "background-remove", "local-rmbg-u2net", qa_user
        )
        assert model["id"] == "local-rmbg-u2net"

    def test_validate_rejects_incompatible_model_with_mismatch(self, qa_user):
        with pytest.raises(_elig.ModelCapabilityMismatch) as exc:
            _elig.validate_model_for_tool(
                "object-remove", "cf-flux-klein-4b", qa_user
            )
        assert "MODEL_CAPABILITY_MISMATCH" in str(exc.value)

    def test_validate_rejects_mock_model(self, qa_user):
        with pytest.raises(_elig.ModelCapabilityMismatch):
            _elig.validate_model_for_tool(
                "background-remove", "mock-bg-remove", qa_user
            )

    def test_fallbacks_exclude_failed_and_mock(self, qa_user, settings):
        settings.AI_HF_BRIA_RMBG_ENABLED = True
        models = _elig.get_compatible_models_for_tool("background-remove", qa_user)
        assert len(models) >= 1
        fallbacks = _elig.fallback_models_for_tool(
            "background-remove", models[0]["id"], qa_user
        )
        assert all(m["id"] != models[0]["id"] for m in fallbacks)
        assert all(not m.get("is_mock") for m in fallbacks)

    def test_no_compatible_model_returns_none(self, qa_user, settings):
        settings.FAL_KEY = ""
        settings.PHOTOROOM_API_KEY = ""
        settings.COMFYUI_ENABLED = False
        assert _elig.get_recommended_model_for_tool("relight", qa_user) is None
        assert _elig.get_compatible_models_for_tool("relight", qa_user) == []

    def test_keyed_models_cover_former_gaps(self, qa_user, settings):
        # With provider keys present, former gaps resolve to real assessed
        # models (still PENDING without live records — see gate tests).
        settings.FAL_KEY = "test-key"
        settings.PHOTOROOM_API_KEY = "test-key"
        assert "fal-clarity-enhance" in {
            m["id"] for m in get_image_models("enhance", qa_user)
        }
        assert "fal-relight" in {
            m["id"] for m in get_image_models("relight", qa_user)
        }
        assert "photoroom-shadow" in {
            m["id"] for m in get_image_models("shadow", qa_user)
        }


class TestModelListContract:
    def test_models_endpoint_lists_all_with_honest_flags(self, qa_user):
        from rest_framework.test import APIClient

        client = APIClient()
        client.force_authenticate(qa_user)
        response = client.get("/api/v1/ai/models/", {"tool_name": "background-remove"})
        assert response.status_code == 200
        data = response.data["data"]
        assert data["operation"] == "background-remove"
        assert data["required_capabilities"] == ["background_removal"]
        assert isinstance(data["models"], list)
        assert len(data["models"]) > 1  # visible by design, not hidden
        for m in data["models"]:
            assert "locked" in m and "available" in m and "configured" in m
            assert "requires_plan" in m and "unavailability_reason" in m
            assert "mock" not in str(m["provider"]).lower(), m
        # Runnable entries are flagged available; recommended points at one.
        ids = [m["id"] for m in data["models"]]
        assert data["recommended_model"] in ids
        rec = next(m for m in data["models"] if m["id"] == data["recommended_model"])
        assert rec["available"] is True

    def test_locked_flag_for_lower_tier_user(self, db, settings):
        from django.contrib.auth import get_user_model
        from rest_framework.test import APIClient

        settings.AI_REQUIRE_LIVE_VERIFICATION = False
        user = get_user_model().objects.create_user(
            email="free-vis@toolhub.local", password="password"
        )
        client = APIClient()
        client.force_authenticate(user)
        response = client.get("/api/v1/ai/models/", {"tool_name": "text-to-image"})
        assert response.status_code == 200
        models = response.data["data"]["models"]
        assert models, "compatible premium models must be VISIBLE, not hidden"
        assert all(m["locked"] is True for m in models)
        assert all(m["requires_plan"] == "Pro" for m in models)
        assert all(m["available"] is False for m in models)

    def test_models_endpoint_lists_unrunnable_with_honest_flags(self, qa_user, settings):
        # Visibility contract: retouch lists its assessed model even though
        # no key exists here — flagged not-available, never hidden.
        from rest_framework.test import APIClient

        settings.PHOTOROOM_API_KEY = ""
        settings.OPENROUTER_API_KEY = ""
        client = APIClient()
        client.force_authenticate(qa_user)
        response = client.get("/api/v1/ai/models/", {"tool_name": "retouch"})
        assert response.status_code == 200
        data = response.data["data"]
        ids = [m["id"] for m in data["models"]]
        assert "photoroom-beautify" in ids
        entry = next(m for m in data["models"] if m["id"] == "photoroom-beautify")
        assert entry["available"] is False
        assert entry["configured"] is False
        assert data["recommended_model"] is None


class TestTierLockedExecution:
    def test_locked_model_rejected_with_tier_error(self, db, settings):
        from django.contrib.auth import get_user_model

        settings.AI_REQUIRE_LIVE_VERIFICATION = False
        user = get_user_model().objects.create_user(
            email="free-lock@toolhub.local", password="password"
        )
        with pytest.raises(PermissionError, match="MODEL_TIER_LOCKED"):
            _elig.validate_model_for_tool("text-to-image", "cf-flux-klein-4b", user)

    def test_unrunnable_model_rejected_with_unavailable(self, qa_user):
        # local-rmbg is assessed-compatible with background-remove but (with
        # the live gate enforced) not runnable here → MODEL_UNAVAILABLE.
        from django.test import override_settings

        with override_settings(AI_REQUIRE_LIVE_VERIFICATION=True):
            from apps.ai_tools import live_status as _live

            orig = _live.load_records
            _live.load_records = lambda: {}
            # clear mtime cache so the monkeypatched loader is honored
            _live._CACHE["mtime"] = None
            try:
                with pytest.raises(_elig.ModelUnavailable, match="MODEL_UNAVAILABLE"):
                    _elig.validate_model_for_tool(
                        "background-remove", "local-rmbg-u2net", qa_user
                    )
            finally:
                _live.load_records = orig
                _live._CACHE["mtime"] = None

    def test_truly_incompatible_model_still_mismatch(self, qa_user):
        with pytest.raises(_elig.ModelCapabilityMismatch, match="MODEL_CAPABILITY_MISMATCH"):
            _elig.validate_model_for_tool("object-remove", "cf-flux-klein-4b", qa_user)


class TestLiveVerificationGate:
    """The production quality gate: assessed VERIFIED counts only with a
    live-inference record (or an explicitly relaxed gate, as above)."""

    def test_pending_without_live_record(self, qa_user, settings, monkeypatch):
        from apps.ai_tools import live_status as _live

        settings.AI_REQUIRE_LIVE_VERIFICATION = True
        monkeypatch.setattr(_live, "load_records", lambda: {})
        models = get_image_models("background-remove", qa_user)
        assert all(m["quality_status"] != "VERIFIED_PRODUCTION" for m in models)
        assert "local-rmbg-u2net" not in {m["id"] for m in models}

    def test_verified_with_live_record(self, qa_user, settings, monkeypatch):
        from apps.ai_tools import live_status as _live

        settings.AI_REQUIRE_LIVE_VERIFICATION = True
        monkeypatch.setattr(
            _live,
            "load_records",
            lambda: {"local-rmbg-u2net": {"inference_success": True}},
        )
        ids = {m["id"] for m in get_image_models("background-remove", qa_user)}
        assert "local-rmbg-u2net" in ids

    def test_failed_live_record_never_promotes(self, qa_user, settings, monkeypatch):
        from apps.ai_tools import live_status as _live

        settings.AI_REQUIRE_LIVE_VERIFICATION = True
        monkeypatch.setattr(
            _live,
            "load_records",
            lambda: {"local-rmbg-u2net": {"inference_success": False}},
        )
        ids = {m["id"] for m in get_image_models("background-remove", qa_user)}
        assert "local-rmbg-u2net" not in ids
