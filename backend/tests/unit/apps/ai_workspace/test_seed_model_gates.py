"""Seed-gate coverage for the official provider/model ecosystem.

Verifies (without touching the database):
- every official provider family has a credential gate, including ``meta``
  (previously missing, so Meta models could never seed);
- the Cloudflare gate accepts the canonical CLOUDFLARE_* spelling as well
  as the legacy CLDFLARE_* / CF_* aliases;
- the Hugging Face gate accepts HF_API_TOKEN or HUGGINGFACE_API_KEY.
"""

from django.test import SimpleTestCase, override_settings

from apps.ai_workspace.management.commands.seed_ai_models import (
    OFFICIAL_MODELS,
    _REQUIRED_SETTING,
    _gate_satisfied,
    _provider_gate_satisfied,
)


class SeedGateConfigTest(SimpleTestCase):
    def test_all_official_providers_have_gates(self):
        providers = {spec["provider"] for spec in OFFICIAL_MODELS}
        for provider in providers:
            self.assertIn(
                provider,
                _REQUIRED_SETTING,
                f"provider '{provider}' has seeded models but no credential gate",
            )

    def test_meta_provider_has_gate(self):
        self.assertIn("meta", _REQUIRED_SETTING)
        self.assertTrue(
            any(spec["provider"] == "meta" for spec in OFFICIAL_MODELS)
        )

    def test_cloudflare_gate_accepts_canonical_spelling(self):
        gate = _REQUIRED_SETTING["cloudflare"]
        self.assertIn("CLOUDFLARE_API_TOKEN", gate)

    @override_settings(CLOUDFLARE_API_TOKEN="canon", CLDFLARE_API_TOKEN="", CF_API_TOKEN="")
    def test_cloudflare_gate_satisfied_by_canonical(self):
        self.assertTrue(_gate_satisfied(_REQUIRED_SETTING["cloudflare"]))

    @override_settings(CLOUDFLARE_API_TOKEN="", CLDFLARE_API_TOKEN="legacy", CF_API_TOKEN="")
    def test_cloudflare_gate_satisfied_by_legacy(self):
        self.assertTrue(_gate_satisfied(_REQUIRED_SETTING["cloudflare"]))

    @override_settings(
        CLOUDFLARE_API_TOKEN="tok",
        CLOUDFLARE_ACCOUNT_ID="",
        CLDFLARE_ACCOUNT_ID="",
        CF_ACCOUNT_ID="",
    )
    def test_cloudflare_provider_gate_requires_account(self):
        self.assertFalse(_provider_gate_satisfied("cloudflare"))

    @override_settings(
        CLOUDFLARE_API_TOKEN="",
        CLDFLARE_API_TOKEN="",
        CLDFLARE_ACCOUNT_ID="",
        CLOUDFLARE_ACCOUNT_ID="",
        CF_API_TOKEN="",
        CF_ACCOUNT_ID="",
    )
    def test_cloudflare_gate_unsatisfied_when_empty(self):
        self.assertFalse(_gate_satisfied(_REQUIRED_SETTING["cloudflare"]))

    @override_settings(HF_API_TOKEN="tok", HUGGINGFACE_API_KEY="")
    def test_hf_gate_satisfied_by_token(self):
        self.assertTrue(_gate_satisfied(_REQUIRED_SETTING["huggingface"]))

    @override_settings(HF_API_TOKEN="", HUGGINGFACE_API_KEY="key")
    def test_hf_gate_satisfied_by_alias(self):
        self.assertTrue(_gate_satisfied(_REQUIRED_SETTING["huggingface"]))
