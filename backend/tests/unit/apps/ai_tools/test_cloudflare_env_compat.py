"""Cloudflare credential env compatibility (canonical + legacy spellings).

Canonical: CLOUDFLARE_API_TOKEN / CLOUDFLARE_ACCOUNT_ID.
Legacy (kept working): CLDFLARE_* (typo) and CF_* aliases.
Precedence: CLOUDFLARE_* > CLDFLARE_* > CF_*.
"""

from django.test import SimpleTestCase, override_settings

from apps.ai_tools.providers.cloudflare import CloudflareImageProvider


@override_settings(
    CLOUDFLARE_ACCOUNT_ID="canon-acct",
    CLOUDFLARE_API_TOKEN="canon-tok",
    CLDFLARE_ACCOUNT_ID="legacy-acct",
    CLDFLARE_API_TOKEN="legacy-tok",
    CF_ACCOUNT_ID="cf-acct",
    CF_API_TOKEN="cf-tok",
)
class CanonicalPrecedenceTest(SimpleTestCase):
    def test_canonical_wins_over_legacy_and_cf(self):
        provider = CloudflareImageProvider()
        self.assertEqual(provider._account_id, "canon-acct")
        self.assertEqual(provider._api_token, "canon-tok")
        self.assertTrue(provider.is_configured())


@override_settings(
    CLOUDFLARE_ACCOUNT_ID="",
    CLOUDFLARE_API_TOKEN="",
    CLDFLARE_ACCOUNT_ID="legacy-acct",
    CLDFLARE_API_TOKEN="legacy-tok",
)
class LegacyFallbackTest(SimpleTestCase):
    def test_legacy_spelling_keeps_working(self):
        provider = CloudflareImageProvider()
        self.assertEqual(provider._account_id, "legacy-acct")
        self.assertEqual(provider._api_token, "legacy-tok")
        self.assertTrue(provider.is_configured())


@override_settings(
    CLOUDFLARE_ACCOUNT_ID="",
    CLOUDFLARE_API_TOKEN="",
    CLDFLARE_ACCOUNT_ID="",
    CLDFLARE_API_TOKEN="",
    CF_ACCOUNT_ID="cf-acct",
    CF_API_TOKEN="cf-tok",
)
class CfAliasFallbackTest(SimpleTestCase):
    def test_cf_alias_keeps_working(self):
        provider = CloudflareImageProvider()
        self.assertTrue(provider.is_configured())


@override_settings(
    CLOUDFLARE_ACCOUNT_ID="",
    CLOUDFLARE_API_TOKEN="",
    CLDFLARE_ACCOUNT_ID="",
    CLDFLARE_API_TOKEN="",
    CF_ACCOUNT_ID="",
    CF_API_TOKEN="",
)
class UnconfiguredTest(SimpleTestCase):
    def test_missing_credentials_not_configured(self):
        self.assertFalse(CloudflareImageProvider().is_configured())
