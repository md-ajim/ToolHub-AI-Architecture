"""Tests for the PhotoRoom provider + fal relight (HTTP mocked — no spend).

Covers: PHOTOROOM_API_KEY gating, ghost/flat-lay feature routing, prompt
pass-through, binary response parsing, auth/quota error mapping, registry
visibility, and fal relighting style handling.
"""

import io

from django.core.files.base import ContentFile
from django.test import SimpleTestCase, override_settings
from PIL import Image as PILImage
from unittest.mock import patch, MagicMock

from apps.ai_tools.providers.base import ImageProcessingRequest, ProviderError
from apps.ai_tools.providers.photoroom import PhotoRoomImageProvider
from apps.ai_tools.registry import get_image_models


def make_image_file(size=(64, 64)):
    img = PILImage.new("RGB", size, color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ContentFile(buf.getvalue(), name="test.png")


def make_result_png(size=(64, 64)):
    buf = io.BytesIO()
    PILImage.new("RGB", size, color=(20, 90, 160)).save(buf, format="PNG")
    return buf.getvalue()


def binary_response(status=200, content_type="image/png"):
    resp = MagicMock()
    resp.status_code = status
    resp.headers = {"content-type": content_type}
    resp.content = make_result_png()
    resp.text = ""
    return resp


@override_settings(PHOTOROOM_API_KEY="test-pr-key")
class PhotoRoomProviderTest(SimpleTestCase):
    def test_not_configured_without_key(self):
        with override_settings(PHOTOROOM_API_KEY=""):
            provider = PhotoRoomImageProvider()
            self.assertFalse(provider.is_configured())
            with self.assertRaises(ProviderError) as ctx:
                provider.process(
                    ImageProcessingRequest(image_file=make_image_file(), operation="ghost-mannequin")
                )
            self.assertEqual(ctx.exception.code, "not_configured")

    def test_supports_only_fashion_ops(self):
        provider = PhotoRoomImageProvider()
        self.assertTrue(provider.supports("ghost-mannequin"))
        self.assertTrue(provider.supports("flat-lay"))
        self.assertTrue(provider.supports("shadow"))
        self.assertTrue(provider.supports("retouch"))
        self.assertTrue(provider.supports("fashion-retouch"))
        self.assertFalse(provider.supports("background-remove"))
        self.assertFalse(provider.supports("relight"))

    @patch("apps.ai_tools.providers.photoroom.requests.post")
    def test_ghost_mannequin_posts_feature_flag(self, mock_post):
        mock_post.return_value = binary_response()
        provider = PhotoRoomImageProvider()
        result = provider.process(
            ImageProcessingRequest(
                image_file=make_image_file(), operation="ghost-mannequin",
                model_id="photoroom-ghost-mannequin",
            )
        )
        self.assertEqual(result.width, 64)
        self.assertEqual(result.model_id, "photoroom-ghost-mannequin")
        args, kwargs = mock_post.call_args
        self.assertIn("image-api.photoroom.com/v2/edit", args[0])
        self.assertEqual(kwargs["headers"]["x-api-key"], "test-pr-key")
        self.assertEqual(kwargs["data"]["ghostMannequin.mode"], "ai.auto")
        self.assertIn("imageFile", kwargs["files"])

    @patch("apps.ai_tools.providers.photoroom.requests.post")
    def test_flat_lay_with_prompt(self, mock_post):
        mock_post.return_value = binary_response()
        provider = PhotoRoomImageProvider()
        provider.process(
            ImageProcessingRequest(
                image_file=make_image_file(), operation="flat-lay",
                model_id="photoroom-flat-lay", prompt="a clean studio flat lay",
            )
        )
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs["data"]["flatLay.mode"], "ai.auto")
        self.assertEqual(kwargs["data"]["flatLay.prompt"], "a clean studio flat lay")

    @patch("apps.ai_tools.providers.photoroom.requests.post")
    def test_auth_failure_mapped(self, mock_post):
        mock_post.return_value = binary_response(status=401, content_type="application/json")
        provider = PhotoRoomImageProvider()
        with self.assertRaises(ProviderError) as ctx:
            provider.process(
                ImageProcessingRequest(image_file=make_image_file(), operation="flat-lay")
            )
        self.assertEqual(ctx.exception.code, "not_configured")

    @patch("apps.ai_tools.providers.photoroom.requests.post")
    def test_quota_exhausted_mapped(self, mock_post):
        mock_post.return_value = binary_response(status=402, content_type="application/json")
        provider = PhotoRoomImageProvider()
        with self.assertRaises(ProviderError) as ctx:
            provider.process(
                ImageProcessingRequest(image_file=make_image_file(), operation="ghost-mannequin")
            )
        self.assertEqual(ctx.exception.code, "quota_exceeded")

    @patch("apps.ai_tools.providers.photoroom.requests.post")
    def test_non_image_response_rejected(self, mock_post):
        resp = binary_response(content_type="application/json")
        resp.content = b'{"error": "x"}'
        mock_post.return_value = resp
        provider = PhotoRoomImageProvider()
        with self.assertRaises(ProviderError) as ctx:
            provider.process(
                ImageProcessingRequest(image_file=make_image_file(), operation="flat-lay")
            )
        self.assertEqual(ctx.exception.code, "provider_error")

    def test_wrong_model_id_rejected(self):
        provider = PhotoRoomImageProvider()
        with self.assertRaises(ProviderError) as ctx:
            provider.process(
                ImageProcessingRequest(
                    image_file=make_image_file(), operation="ghost-mannequin",
                    model_id="fal-esrgan-upscale",
                )
            )
        self.assertEqual(ctx.exception.code, "unsupported_operation")

    @patch("apps.ai_tools.providers.photoroom.requests.post")
    def test_beautify_retouch(self, mock_post):
        mock_post.return_value = binary_response()
        provider = PhotoRoomImageProvider()
        result = provider.process(
            ImageProcessingRequest(
                image_file=make_image_file(), operation="retouch",
                model_id="photoroom-beautify",
            )
        )
        self.assertEqual(result.width, 64)
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs["data"]["beautify.mode"], "ai.auto")

    @patch("apps.ai_tools.providers.photoroom.requests.post")
    def test_shadow_uses_overrides_model(self, mock_post):
        mock_post.return_value = binary_response()
        provider = PhotoRoomImageProvider()
        result = provider.process(
            ImageProcessingRequest(
                image_file=make_image_file(), operation="shadow",
                model_id="photoroom-shadow",
                extra={"opacity": 0.8, "blur": 30, "distance": 60, "direction": "bottom-left"},
            )
        )
        self.assertEqual(result.width, 64)
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs["data"]["shadow.mode"], "ai.auto-with-overrides")
        self.assertEqual(kwargs["data"]["shadow.intensityOverride"], 0.8)
        self.assertEqual(kwargs["data"]["shadow.softnessOverride"], 0.5)
        self.assertEqual(kwargs["data"]["shadow.spreadOverride"], "long")
        self.assertEqual(kwargs["data"]["shadow.directionOverride"], "frontLeft")
        self.assertEqual(
            kwargs["headers"].get("pr-ai-shadows-model-version"), "2026-04-15"
        )


@override_settings(PHOTOROOM_API_KEY="test-pr-key", AI_REQUIRE_LIVE_VERIFICATION=False)
class PhotoRoomRegistryTest(SimpleTestCase):
    def test_registry_shows_photoroom_when_configured(self):
        providers = {m["provider"] for m in get_image_models()}
        self.assertIn("photoroom", providers)

    def test_registry_hides_photoroom_without_key(self):
        with override_settings(PHOTOROOM_API_KEY=""):
            providers = {m["provider"] for m in get_image_models()}
            self.assertNotIn("photoroom", providers)


@override_settings(FAL_KEY="test-fal-key")
class FalRelightTest(SimpleTestCase):
    @patch("apps.ai_tools.providers.fal.requests.post")
    @patch("apps.ai_tools.providers.fal.requests.get")
    def test_relight_sends_lighting_style(self, mock_get, mock_post):
        post_resp = MagicMock()
        post_resp.status_code = 200
        post_resp.json.return_value = {"images": [{"url": "https://cdn.example/r.png"}]}
        mock_post.return_value = post_resp
        get_resp = MagicMock(content=make_result_png())
        get_resp.raise_for_status.return_value = None
        mock_get.return_value = get_resp
        from apps.ai_tools.providers.fal import FalImageProvider

        provider = FalImageProvider()
        result = provider.process(
            ImageProcessingRequest(
                image_file=make_image_file(), operation="relight",
                model_id="fal-relight", extra={"style": "studio"},
            )
        )
        self.assertEqual(result.width, 64)
        args, kwargs = mock_post.call_args
        self.assertIn("/fal-ai/image-apps-v2/relighting", args[0])
        self.assertEqual(kwargs["json"]["lighting_style"], "studio")

    @patch("apps.ai_tools.providers.fal.requests.post")
    @patch("apps.ai_tools.providers.fal.requests.get")
    def test_relight_defaults_unknown_style_to_natural(self, mock_get, mock_post):
        post_resp = MagicMock()
        post_resp.status_code = 200
        post_resp.json.return_value = {"images": [{"url": "https://cdn.example/r.png"}]}
        mock_post.return_value = post_resp
        get_resp = MagicMock(content=make_result_png())
        get_resp.raise_for_status.return_value = None
        mock_get.return_value = get_resp
        from apps.ai_tools.providers.fal import FalImageProvider

        provider = FalImageProvider()
        provider.process(
            ImageProcessingRequest(
                image_file=make_image_file(), operation="relight",
                model_id="fal-relight", extra={"style": "disco-fever"},
            )
        )
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs["json"]["lighting_style"], "natural")
