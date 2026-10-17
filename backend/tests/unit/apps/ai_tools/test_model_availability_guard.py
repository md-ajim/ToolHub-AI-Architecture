"""Output availability guard: a model that cannot produce valid output is
disabled globally (shared cache) until it recovers. Config/registry/
routing/credits untouched.
"""
import pytest
from django.contrib.auth import get_user_model

from apps.ai_tools import model_availability as guard
from apps.ai_tools.providers.base import ProviderError

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _locmem_cache(settings):
    settings.CACHES = {
        "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
    }
    settings.AI_REQUIRE_LIVE_VERIFICATION = False
    yield
    from django.core.cache import cache

    cache.clear()


@pytest.fixture
def qa_user(db):
    return get_user_model().objects.create_user(
        email="guard-qa@toolhub.local", password="password", is_qa_user=True
    )


class TestFailureClassification:
    def test_provider_output_failures_tracked(self):
        for code in (
            "provider_error",
            "provider_unavailable",
            "timeout",
            "rate_limited",
            "cloudflare_api_error",
            "unexpected_response",
            "output_invalid",
            "empty_response",
            "not_configured",
            "provider_billing_required",
        ):
            assert guard.should_track_failure(ProviderError(code, "x")) is True, code

    def test_user_input_and_unrelated_errors_never_tracked(self):
        for code in (
            "invalid_image",
            "invalid_input",
            "invalid_request",
            "unsupported_operation",
            "unknown_provider",
        ):
            assert guard.should_track_failure(ProviderError(code, "x")) is False, code

    def test_secret_details_never_cached(self):
        guard.record_model_failure(
            "cf-sdxl-base", "cloudflare",
            ProviderError("provider_error", "sk-secret-key quota xyz"),
        )
        state = guard.get_model_outage("cf-sdxl-base")
        assert state is not None
        assert "sk-secret" not in str(state)
        assert state["reason"]
        assert "sk-secret" not in state["reason"]


class TestGlobalDisableAndRecovery:
    def test_failure_disables_model_globally(self, qa_user):
        from apps.ai_tools import eligibility as elig

        # Sanity: model starts runnable in selector when no outage.
        before = {m["id"]: m for m in elig.get_selector_models("background-remove", qa_user)}
        assert "local-rmbg-u2net" in before
        assert before["local-rmbg-u2net"]["available"] is True

        guard.note_model_call_result(
            "local-rmbg-u2net", "local_rmbg",
            ProviderError("output_invalid", "Provider returned no image data."),
        )
        assert guard.is_model_unavailable("local-rmbg-u2net") is True

        # Same flag for every user/session (shared cache, no user key).
        after = {m["id"]: m for m in elig.get_selector_models("background-remove", qa_user)}
        assert after["local-rmbg-u2net"]["available"] is False
        assert after["local-rmbg-u2net"]["unavailability_reason"]
        assert "no output" in after["local-rmbg-u2net"]["unavailability_reason"].lower()
        # Model stays listed (never removed), only disabled.
        assert "local-rmbg-u2net" in after

        # Runnable set excludes it: no auto-pick, no execution.
        runnable_ids = {m["id"] for m in elig.get_compatible_models_for_tool("background-remove", qa_user)}
        assert "local-rmbg-u2net" not in runnable_ids

    def test_success_recovers_model(self, qa_user):
        from apps.ai_tools import eligibility as elig

        guard.note_model_call_result(
            "local-rmbg-u2net", "local_rmbg", ProviderError("timeout", "t"),
        )
        assert guard.is_model_unavailable("local-rmbg-u2net") is True
        guard.note_model_call_result("local-rmbg-u2net", "local_rmbg", None)
        assert guard.is_model_unavailable("local-rmbg-u2net") is False
        after = {m["id"]: m for m in elig.get_selector_models("background-remove", qa_user)}
        assert after["local-rmbg-u2net"]["available"] is True

    def test_single_user_input_error_does_not_disable(self):
        guard.note_model_call_result(
            "local-rmbg-u2net", "local_rmbg",
            ProviderError("invalid_image", "Could not decode input image."),
        )
        assert guard.is_model_unavailable("local-rmbg-u2net") is False

    def test_transient_and_persistent_cooldowns_differ(self):
        assert guard._cooldown_for("timeout") == guard.TRANSIENT_COOLDOWN_SECONDS
        assert guard._cooldown_for("output_invalid") == guard.PERSISTENT_COOLDOWN_SECONDS
        assert guard.TRANSIENT_COOLDOWN_SECONDS < guard.PERSISTENT_COOLDOWN_SECONDS

    def test_registry_config_untouched(self):
        from apps.ai_tools.registry import IMAGE_MODELS

        # No registry entry removed/renamed; guard only overlays cache state.
        ids = {m["id"] for m in IMAGE_MODELS}
        assert "cf-sdxl-base" in ids
        assert "fal-clarity-enhance" in ids
